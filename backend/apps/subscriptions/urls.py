from django.urls import path
from .views import (
    SubscriptionStatusView,
    ChariowCheckoutView,
    ChariowWebhookView
)

urlpatterns = [
    path('status/', SubscriptionStatusView.as_view(), name='subscription_status'),
    path('checkout/', ChariowCheckoutView.as_view(), name='subscription_checkout'),
    path('webhook/', ChariowWebhookView.as_view(), name='subscription_webhook'),
    path('chariow/checkout/', ChariowCheckoutView.as_view(), name='chariow_checkout'),
    path('chariow/webhook/', ChariowWebhookView.as_view(), name='chariow_webhook'),
]
