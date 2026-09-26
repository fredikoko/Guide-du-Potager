from django.contrib import admin
from .models import Subscription, Payment, SubscriptionPlan

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price', 'currency', 'approx_eur', 'discount_badge', 'is_featured', 'duration_days', 'is_active', 'order')
    list_editable = ('price', 'currency', 'approx_eur', 'discount_badge', 'is_featured', 'is_active', 'order')
    list_filter = ('is_active', 'is_featured', 'plan_type')
    search_fields = ('name', 'plan_type', 'description')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan_type', 'amount', 'status', 'start_date', 'end_date')
    list_filter = ('plan_type', 'status')
    search_fields = ('user__email', 'user__username')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'payment_method', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('payment_method', 'status', 'currency')
    search_fields = ('transaction_id', 'user__email', 'phone_number')
