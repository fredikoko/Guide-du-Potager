from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, CustomTokenObtainPairView, ChangePasswordView,
    PasswordResetView, AccountDeleteView, ValidateEmailView,
    VerifyRegistrationView, ResendVerificationCodeView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('verify-registration/', VerifyRegistrationView.as_view(), name='auth_verify_registration'),
    path('resend-code/', ResendVerificationCodeView.as_view(), name='auth_resend_code'),
    path('login/', CustomTokenObtainPairView.as_view(), name='auth_login'),
    path('refresh/', TokenRefreshView.as_view(), name='auth_refresh'),
    path('validate-email/', ValidateEmailView.as_view(), name='auth_validate_email'),
    path('password-reset/', PasswordResetView.as_view(), name='auth_password_reset'),
    path('change-password/', ChangePasswordView.as_view(), name='auth_change_password'),
    path('account/', AccountDeleteView.as_view(), name='auth_account_delete'),
]
