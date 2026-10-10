from django.urls import path
from .views import (
    SubscriptionStatusView,
    SubscriptionPlanListView,
    ChariowCheckoutView,
    ChariowWebhookView,
    DigitalProductPricingView,
    UserPurchasesListView,
)

urlpatterns = [
    path('plans/', SubscriptionPlanListView.as_view(), name='subscription_plans'),
    path('status/', SubscriptionStatusView.as_view(), name='subscription_status'),
    path('checkout/', ChariowCheckoutView.as_view(), name='subscription_checkout'),
    path('webhook/', ChariowWebhookView.as_view(), name='subscription_webhook'),
    path('chariow/checkout/', ChariowCheckoutView.as_view(), name='chariow_checkout'),
    path('chariow/webhook/', ChariowWebhookView.as_view(), name='chariow_webhook'),
    path('pricing/', DigitalProductPricingView.as_view(), name='digital_pricing'),
    path('my-purchases/', UserPurchasesListView.as_view(), name='user_purchases'),
]
