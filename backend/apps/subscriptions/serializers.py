from rest_framework import serializers
from .models import Subscription, Payment, SubscriptionPlan, DigitalProductPricing, UserPurchase

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
    plan_type = serializers.ChoiceField(
        choices=['monthly', 'seasonal', 'yearly', 'full_guide', 'post'],
        default='monthly',
        required=False
    )
    purchase_type = serializers.ChoiceField(
        choices=['full_guide', 'post', 'chapter'],
        required=False,
        allow_null=True
    )
    post_id = serializers.IntegerField(required=False, allow_null=True)
    chapter_id = serializers.IntegerField(required=False, allow_null=True)
    redirect_url = serializers.URLField(required=False, allow_blank=True)


class DigitalProductPricingSerializer(serializers.ModelSerializer):
    formatted_guide_price = serializers.CharField(read_only=True)
    formatted_article_price = serializers.CharField(read_only=True)

    class Meta:
        model = DigitalProductPricing
        fields = [
            'id', 'guide_title', 'guide_description',
            'guide_price', 'formatted_guide_price',
            'article_default_price', 'formatted_article_price',
            'currency', 'is_active', 'updated_at'
        ]


class UserPurchaseSerializer(serializers.ModelSerializer):
    item_title = serializers.SerializerMethodField()

    class Meta:
        model = UserPurchase
        fields = [
            'id', 'purchase_type', 'item_title', 'amount',
            'currency', 'status', 'transaction_id', 'created_at'
        ]

    def get_item_title(self, obj):
        if obj.purchase_type == 'full_guide':
            return "Guide Complet du Potager Tropical"
        elif obj.post:
            return obj.post.title
        elif obj.chapter:
            return obj.chapter.title
        return obj.purchase_type
