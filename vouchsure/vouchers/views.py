from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from .models import VoucherPaymentProof, PaperPaymentProof
from .forms import CustomUserCreationForm
from .utils import send_confirmation_email, notify_admin_about_paper_order
from django.contrib.auth.decorators import login_required
import os
from django.views.static import serve

# Voucher pricing structure
voucher_prices = {
    'aws-ai': {'50': 1800, '100': 3500},
    'aws-cp': {'50': 1900, '100': 3600},
    'aws-dev': {'50': 3500, '100': 4500},
    'aws-data': {'50': 3500, '100': 4500},
    'aws-sysops': {'50': 3500, '100': 4500},
    'aws-sa': {'50': 3500, '100': 4500},
    'aws-ml': {'50': 3500, '100': 4500},
    'az-900': {'50': 1100}
}

VALID_AMOUNTS = {1000, 1100, 1500, 1800, 1900, 2500, 3500, 3600, 4500}


def home(request):
    return render(request, 'main/index.html')

def media_serve(request, path):
    # Ensure the user doesn't need to be logged in to view media files
    media_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(media_path):
        return serve(request, path, document_root=settings.MEDIA_ROOT)
    else:
        return render(request, '404.html', status=404)
@login_required(login_url='login')
def voucher_list(request):
    return render(request, 'vouchers/vouchers.html')


def voucher_view(request):
    voucher = request.GET.get("voucher")
    discount = request.GET.get("discount")

    if not voucher or not discount:
        return HttpResponseBadRequest("Missing voucher or discount parameter")

    if voucher not in voucher_prices or discount not in voucher_prices[voucher]:
        return HttpResponseBadRequest("Invalid voucher or discount")

    amount = voucher_prices[voucher][discount]
    request.session["voucher_amount"] = amount

    return redirect("payment")


def payment_view(request):
    voucher_amount = request.session.get("voucher_amount")
    if not voucher_amount:
        return HttpResponse("Missing voucher or discount parameter", status=400)

    proof = None
    if request.user.is_authenticated:
        proof = VoucherPaymentProof.objects.filter(email=request.user.email, amount=voucher_amount).order_by('-id').first()

    return render(request, 'vouchers/payment.html', {
        'voucher_amount': voucher_amount,
        'proof': proof,
    })

@login_required
def papers(request):
    step = request.GET.get("step", "1")

    if request.method == "POST":
        if step == "1":
            request.session['paper_type'] = request.POST.get("paper_type")
            request.session['subject'] = request.POST.get("subject")
            return redirect('/vouchers/papers/?step=2')

        elif step == "2":
            request.session['topic'] = request.POST.get("topic")
            request.session['idea'] = request.POST.get("idea")
            request.session['pages'] = request.POST.get("pages")
            return redirect('/vouchers/papers/?step=3')

        elif step == "3":
            request.session['deadline_date'] = request.POST.get("deadline_date")
            request.session['deadline_time'] = request.POST.get("deadline_time")
            return redirect('/vouchers/papers/?step=4')

    if step == "1":
        return render(request, 'main/papers_step1.html')
    elif step == "2":
        return render(request, 'main/papers_step2.html')
    elif step == "3":
        return render(request, 'main/papers_step3.html')
    elif step == "4":
        topic = request.session.get('topic')
        idea = request.session.get('idea')
        pages = request.session.get('pages')
        paper_type = request.session.get('paper_type')
        subject = request.session.get('subject')
        deadline_date = request.session.get('deadline_date')
        deadline_time = request.session.get('deadline_time')

        message = f"""
📝 New Research Paper Order:

Paper Type: {paper_type}
Subject: {subject}
Topic: {topic}
Idea: {idea}
Pages: {pages}
Deadline: {deadline_date} {deadline_time}
"""
        notify_admin_about_paper_order(message)

        return render(request, 'main/papers_payment.html', {'voucher_amount': 4500})
    else:
        return redirect('/vouchers/papers/?step=1')


def contact(request):
    return render(request, 'main/contact.html')


def papers_deadline(request):
    return render(request, 'main/papers_deadline.html')


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


def confirm_voucher_payment(request):
    if request.method == "POST":
        amount = request.POST.get("voucher_amount")
        user_email = request.user.email if request.user.is_authenticated else "Guest"
        print(f"Voucher payment confirmation received from {user_email} for ₹{amount}")
        messages.success(request, "Thanks! We received your voucher payment info. You’ll receive the code via email after verification.")
        return redirect("home")
    return redirect("home")


def upload_proof_view(request):
    voucher_amount = (
        request.POST.get("paper_amount")
        or request.session.get("paper_amount")
        or request.POST.get("voucher_amount")
        or request.session.get("voucher_amount")
        or "Unknown"
    )

    if request.method == 'POST' and request.FILES.get('screenshot'):
        screenshot = request.FILES['screenshot']
        email = request.POST.get('email', 'Not Provided')
        phone = request.POST.get('phone', 'Not Provided')
        optional_message = request.POST.get('message', '')

        PaperPaymentProof.objects.create(
            email=email,
            phone=phone,
            screenshot=screenshot,
            status="Pending"
        )

        fs = FileSystemStorage(location='media/proofs/')
        filename = fs.save(screenshot.name, screenshot)
        file_url = f"http://{request.get_host()}/media/proofs/{filename}"

        user_email = request.user.email if request.user.is_authenticated else 'Anonymous'

        email_subject = "New Payment Proof Uploaded"
        email_message = f"""
Voucher Amount: ₹{voucher_amount}
Form Email: {email}
User Account Email: {user_email}
Phone: {phone}
Message: {optional_message}
Screenshot: {file_url}
"""

        send_confirmation_email(email_subject, email_message)

        return render(request, 'main/upload_proof.html', {
            'submitted': True,
            'paper_amount': voucher_amount,
        })

    return render(request, 'main/upload_proof.html', {
        'paper_amount': 4500
    })


def confirm_paper_payment(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        phone = request.POST.get('phone', 'Not Provided')
        screenshot = request.FILES.get('screenshot')

        if not email or not phone or not screenshot:
            messages.error(request, "All fields are required.")
            return render(request, 'main/papers_payment.html', {'voucher_amount': 4500})

        PaperPaymentProof.objects.create(
            email=email,
            phone=phone,
            screenshot=screenshot,
            status="Pending"
        )

        fs = FileSystemStorage(location='media/proofs/')
        filename = fs.save(screenshot.name, screenshot)
        file_url = f"http://{request.get_host()}/media/proofs/{filename}"

        message = f"""
Paper Amount: ₹4500
User Email: {email}
Phone: {phone}
Screenshot: {file_url}
"""

        send_confirmation_email("Paper Payment Proof Submission", message)

        messages.success(request, "✅ Payment verification pending. We’ll email you once it’s confirmed.")
        return redirect('home')

    return render(request, 'main/papers_payment.html', {'voucher_amount': 4500})


def upload_voucher_proof_view(request):
    voucher_amount = (
        request.POST.get("voucher_amount")
        or request.session.get("voucher_amount")
        or "Unknown"
    )

    if request.method == 'POST' and request.FILES.get('screenshot'):
        screenshot = request.FILES['screenshot']
        email = request.user.email if request.user.is_authenticated else 'Guest'
        phone = request.POST.get('phone', 'Not Provided')
        message_text = request.POST.get('message', '')

        VoucherPaymentProof.objects.create(
            email=email,
            phone=phone,
            message=message_text,
            screenshot=screenshot,
            amount=voucher_amount,
            
        )

        fs = FileSystemStorage(location='media/proofs/')
        filename = fs.save(screenshot.name, screenshot)
        file_url = f"http://{request.get_host()}/media/proofs/{filename}"

        admin_subject = "🧾 New Voucher Payment Proof Uploaded"
        admin_message = f"""
Voucher Amount: ₹{voucher_amount}
User Email: {email}
Phone: {phone}
Message: {message_text}
Screenshot: {file_url}
"""
        send_confirmation_email(admin_subject, admin_message)

        return render(request, 'vouchers/upload_voucher_proof.html', {
            'submitted': True,
            'voucher_amount': voucher_amount
        })

    return render(request, 'vouchers/upload_voucher_proof.html', {
        'voucher_amount': voucher_amount
    })

def custom_404_view(request, exception):
    return render(request, 'main/error.html', status=404)

@login_required
def voucher_history(request):
    user_email = request.user.email
    payments = VoucherPaymentProof.objects.filter(email=user_email).order_by('-uploaded_at')
    return render(request, 'vouchers/voucher_history.html', {'payments': payments})


@login_required
def user_dashboard(request):
    if not request.user.is_authenticated:
        return render(request, 'main/error.html')

    voucher_proofs = VoucherPaymentProof.objects.filter(email=request.user.email).order_by('-uploaded_at')
    paper_proofs = PaperPaymentProof.objects.filter(email=request.user.email).order_by('-uploaded_at')

    return render(request, 'main/user_dashboard.html', {
        'voucher_proofs': voucher_proofs,
        'paper_proofs': paper_proofs,
    })

