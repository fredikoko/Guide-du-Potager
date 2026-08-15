from rest_framework import serializers
from .models import Subscription, Payment

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'plan_type', 'amount', 'status', 'start_date', 'end_date']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'payment_method', 'amount', 'currency', 'status', 'transaction_id', 'phone_number', 'created_at']

class MobilePaymentRequestSerializer(serializers.Serializer):
    plan_type = serializers.ChoiceField(choices=['monthly', 'yearly'])
    payment_method = serializers.ChoiceField(choices=['orange_money', 'wave', 'mtn_money'])
    phone_number = serializers.CharField(max_length=20)

class StripePaymentRequestSerializer(serializers.Serializer):
    plan_type = serializers.ChoiceField(choices=['monthly', 'yearly'])
    payment_method_id = serializers.CharField(max_length=200, required=False)
