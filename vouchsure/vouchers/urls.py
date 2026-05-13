from django.urls import path
from . import views
from .views import upload_proof_view
from .views import upload_voucher_proof_view

from django.contrib.auth.views import (
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

urlpatterns = [
    # Vouchers main page
    path('', views.voucher_list, name='vouchers'),  # Vouchers home page

    # Voucher selection and payment
    path('buy/', views.voucher_view, name='voucher_view'),
    path('payment/', views.payment_view, name='payment'),

    # Paper-related pages
    path('papers/', views.papers, name='papers'),
    path('papers/deadline/', views.papers_deadline, name='papers_deadline'),

    # Authentication-related pages
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

    # Password reset pages
    path('password_reset/', PasswordResetView.as_view(template_name='main/password_reset.html'), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='main/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='main/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name='main/password_reset_complete.html'), name='password_reset_complete'),

    # Voucher confirmation and history
    path("confirm-voucher-payment/", views.confirm_voucher_payment, name="confirm_voucher_payment"),
    path('voucher-history/', views.voucher_history, name='voucher_history'),

    # Proof upload
    path('upload-proof/', upload_proof_view, name='upload_proof'),
    path('upload-voucher-proof/', upload_voucher_proof_view, name='upload_voucher_proof'),

    # Custom handler for file uploads (optional)
    # Add more URLs for your application as needed
]
