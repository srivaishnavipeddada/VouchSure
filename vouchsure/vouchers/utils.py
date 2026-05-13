from django.core.mail import send_mail

# ✅ Generic email sender (used for voucher proof uploads, confirmations, etc.)
def send_confirmation_email(subject, message, recipient='vouchsurehelp@gmail.com', user_email=None):
    try:
        recipient_list = [recipient]
        if user_email and user_email not in recipient_list:
            recipient_list.append(user_email)

        send_mail(
            subject=subject,
            message=message,
            from_email='VouchSure <vouchsurehelp@gmail.com>',
            recipient_list=recipient_list,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False


# ✅ Specifically for admin notification on research paper orders
def notify_admin_about_paper_order(order_details: str):
    try:
        send_mail(
            subject="📝 New Research Paper Order",
            message=order_details,
            from_email='VouchSure <vouchsurehelp@gmail.com>',
            recipient_list=['vouchsurehelp@gmail.com'],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"❌ Paper order email failed: {e}")
        return False
