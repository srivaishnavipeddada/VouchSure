from django.contrib import admin
from .models import Voucher, ResearchPaper, PaperPaymentProof
from .utils import send_confirmation_email  # You already have this
from django.utils.html import strip_tags
from .models import VoucherPaymentProof
from django.core.mail import send_mail
from .models import VoucherPaymentProof
from django.conf import settings



@admin.action(description="✅ Mark selected as Verified & Send Email")
def mark_verified_and_notify(modeladmin, request, queryset):
    for obj in queryset:
        if not obj.is_verified:
            obj.is_verified = True
            obj.save()

            # Construct HTML email
            subject = "📘 Research Paper Order Confirmed!"
            html_message = f"""
            <html>
              <body style="font-family: Poppins, sans-serif; background-color: #f4f4f4; padding: 20px;">
                <div style="background-color: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: auto;">
                  <h2 style="color: #2b5fc0;">🎓 VouchSure Research Paper Order</h2>
                  <p>Hi there,</p>
                  <p>Your payment has been <strong style="color: green;">successfully verified</strong>! ✅</p>
                  <hr>
                  <p><strong>📄 Paper Title:</strong> {obj.title}</p>
                  <p><strong>⏰ Deadline:</strong> {obj.deadline}</p>

                  <hr>
                  <p>We'll now begin preparing your paper. It will be delivered by the requested deadline.</p>
                  <p>Thanks for choosing <strong>VouchSure</strong> 🚀</p>
                </div>
              </body>
            </html>
            """
            plain_message = strip_tags(html_message)

            send_confirmation_email(
                subject=subject,
                message=plain_message,
                recipient=obj.email,
                html_message=html_message
            )


@admin.register(PaperPaymentProof)
class PaperPaymentProofAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'uploaded_at', 'is_verified')
    list_filter = ('is_verified', 'uploaded_at')
    actions = [mark_verified_and_notify]  # ✅ Triggers email on admin action


@admin.action(description="✅ Mark as Verified & Send Confirmation Email")
def verify_and_notify(modeladmin, request, queryset):
    for obj in queryset:
        if not obj.is_verified:
            obj.is_verified = True
            obj.save()

            subject = "🎫 Voucher Payment Confirmed!"
            html_message = f"""
            <html>
              <body style="font-family: Poppins, sans-serif; background-color: #f0f4ff; padding: 20px;">
                <div style="background-color: #fff; padding: 25px; border-radius: 10px; max-width: 600px; margin: auto; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
                  <h2 style="color: #2b5fc0;">Voucher Payment Verified ✅</h2>
                  <p>Hello,</p>
                  <p>Your payment of <strong>₹{obj.amount}</strong> for the voucher <strong>{obj.voucher_name or "Selected Voucher"}</strong> has been verified successfully.</p>
                  <hr>
                  <p>You will receive your voucher shortly via email or dashboard access.</p>
                  <p>Thank you for choosing <strong>VouchSure</strong> 🙌</p>
                </div>
              </body>
            </html>
            """
            plain_message = strip_tags(html_message)
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,  # use the correct sender name
                [obj.email],  # send to user's email
                html_message=html_message
            )

@admin.register(VoucherPaymentProof)
class VoucherPaymentProofAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'amount', 'is_verified', 'uploaded_at')
    list_filter = ('is_verified', 'uploaded_at')
    actions = [verify_and_notify]

# Register other models
admin.site.register(Voucher)
admin.site.register(ResearchPaper)
