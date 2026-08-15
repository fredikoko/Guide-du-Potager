from django.urls import path
from .views import (
    SubscriptionStatusView, CreateSubscriptionView,
    MobilePaymentView, StripeWebhookView
)

urlpatterns = [
    path('status/', SubscriptionStatusView.as_view(), name='subscription_status'),
    path('create/', CreateSubscriptionView.as_view(), name='subscription_create'),
    path('mobile-payment/', MobilePaymentView.as_view(), name='subscription_mobile_payment'),
    path('webhook/', StripeWebhookView.as_view(), name='subscription_webhook'),
]
