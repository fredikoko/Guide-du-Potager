from rest_framework import serializers
from .models import Subscription, Payment, SubscriptionPlan

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    formatted_price = serializers.CharField(read_only=True)
    display_button_text = serializers.CharField(read_only=True)

    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'plan_type', 'name', 'description', 'price', 'currency',
            'approx_eur', 'discount_badge', 'duration_days',
            'is_featured', 'formatted_price', 'display_button_text', 'is_active', 'order'
        ]

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'plan_type', 'amount', 'status', 'start_date', 'end_date']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'payment_method', 'amount', 'currency', 'status', 'transaction_id', 'phone_number', 'created_at']

class ChariowCheckoutRequestSerializer(serializers.Serializer):
    plan_type = serializers.ChoiceField(choices=['monthly', 'seasonal', 'yearly'])
    redirect_url = serializers.URLField(required=False, allow_blank=True)
