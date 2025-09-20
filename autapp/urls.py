from django.urls import path
from . import views
from django.contrib.sitemaps.views import sitemap
from autapp.sitemaps import StaticViewSitemap
sitemaps = {
    'static': StaticViewSitemap,
}
urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('', views.index, name='index'),
    path('signup/<str:ref>', views.signup, name='signup'),
    path('accounts/login/', views.login_view, name='login'),
    path("approve/", views.approve_payment, name="pi_approve"),
  path("complete/", views.complete_payment, name="pi_complete"),
        # API endpoints for Pi payments used by frontend
        path('api/pi-payments/approve', views.approve_payment, name='api_pi_approve'),
        path('api/pi-payments/complete', views.complete_payment, name='api_pi_complete'),
    path('dashboard',views.dashboard,name='dashboard'),
    path('verify/<str:username>', views.verify, name='verify'),
    path('profile/', views.profile, name='profile'),
    path('logout/',views.logout_view,name='logout'),
    path("recovery/", views.forgot_password, name="recovery"),
    path("recovery/validate_recovery/", views.validate_recovery, name="validate_recovery"),
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('resend-otp-signup/<str:username>', views.resend_otp_signup, name='resend_otp'),
    path('recovery/resend-otp-fp/', views.resend_otp_token_fp, name='resend_otp_fp'),
    path('pi-auth/', views.pi_auth, name='pi_auth'),
    path('session-debug/', views.session_debug, name='session_debug'),
    path('api/pi-payments/approve-debug', views.approve_debug, name='api_pi_approve_debug'),
    path('validation-key.txt', views.validate_key, name='validate_key'),
    path('pi-debug/', views.pi_debug, name='pi_debug'), 
]

from django.shortcuts import render

def custom_404(request, exception):
    print("trying")
    return render(request, 'custom.html', status=404)


