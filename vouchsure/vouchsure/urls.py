from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404
from django.views.generic import TemplateView
from vouchers import views

urlpatterns = [
    # Admin URL
    path('admin/', admin.site.urls),

    # Home, contact, papers, dashboard and other pages
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('papers/', views.papers, name='papers'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    # Include voucher URLs (you have another set of URLs in vouchers/urls.py)
    path('vouchers/', include('vouchers.urls')),

    # Custom login error page
    path('custom-login-error/', TemplateView.as_view(template_name='main/error.html'), name='custom_login_error'),
]

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # For production, media files should still be served correctly. 
    # You can use a reverse proxy (e.g., Nginx or a cloud service) to handle media files.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom 404 handler
handler404 = 'vouchers.views.custom_404_view'
