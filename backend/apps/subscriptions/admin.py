from django.contrib import admin
from .models import Subscription, Payment

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
