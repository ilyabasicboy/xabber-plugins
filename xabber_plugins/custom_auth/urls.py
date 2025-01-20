from django.urls import path
from .views import DeveloperLoginView, DeveloperLogoutView, RegistrationView, VerifyEmail, EmailNotVerified, ResendVerificationCode

urlpatterns = [
    path('login/', DeveloperLoginView.as_view(), name='login'),
    path('logout/', DeveloperLogoutView.as_view(), name='logout'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('email_verification/<str:key>/', VerifyEmail.as_view(), name='email_verification'),
    path('email_not_verified/<int:user_id>/', EmailNotVerified.as_view(), name='email_not_verified'),
    path('resend_verification_code/<int:user_id>/', ResendVerificationCode.as_view(), name='resend_verification_code'),
]
