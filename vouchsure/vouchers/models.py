from django.db import models
from django.core.mail import send_mail
from django.conf import settings
class Voucher(models.Model):
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
class ResearchPaper(models.Model):
    title = models.CharField(max_length=200)
    price = models.IntegerField()
    pdf_file = models.FileField(upload_to='papers/')

    def __str__(self):
        return self.title



class PaperPaymentProof(models.Model):
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    screenshot = models.FileField(upload_to='proofs/')
    status = models.CharField(max_length=20, default='pending')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email} - Verified: {self.is_verified}"

    def save(self, *args, **kwargs):
        # Send email only when is_verified changed from False to True
        if self.pk:
            old = PaperPaymentProof.objects.get(pk=self.pk)
            if not old.is_verified and self.is_verified:
                send_mail(
                    subject="📘 Research Paper Order Confirmed!",
                    message=(
                        f"Hi,\n\nYour payment has been successfully verified!\n"
                        "Our team will now prepare and deliver your research paper as per the deadline.\n\n"
                        "Thank you for choosing VouchSure 🚀"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[self.email],
                    fail_silently=False,
                )
        super().save(*args, **kwargs)


class VoucherPaymentProof(models.Model):
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField(blank=True)
    screenshot = models.FileField(upload_to='proofs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    amount = models.CharField(max_length=20, default="Unknown")

    def __str__(self):
        return f"{self.email} - ₹{self.amount} - Verified: {self.is_verified}"

    def save(self, *args, **kwargs):
        if self.pk:
            old = VoucherPaymentProof.objects.get(pk=self.pk)
            if not old.is_verified and self.is_verified:
                send_mail(
                    subject="🎟️ Voucher Payment Verified",
                    message=f"Hi,\n\nYour payment has been verified. You'll receive your voucher shortly.\n\nThank you for choosing VouchSure 💙",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[self.email],
                    fail_silently=False,
                )
        super().save(*args, **kwargs)
