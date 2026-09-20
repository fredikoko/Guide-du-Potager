from django.urls import path
from .views import (
    UserProfileView, UserHistoryView,
    RequestEmailChangeView, ConfirmEmailChangeView
)

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('history/', UserHistoryView.as_view(), name='user_history'),
    path('request-email-change/', RequestEmailChangeView.as_view(), name='user_request_email_change'),
    path('confirm-email-change/', ConfirmEmailChangeView.as_view(), name='user_confirm_email_change'),
]
