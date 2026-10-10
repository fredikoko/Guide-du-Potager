from django.contrib import admin
from .models import Subscription, Payment, SubscriptionPlan, DigitalProductPricing, UserPurchase

@admin.register(DigitalProductPricing)
class DigitalProductPricingAdmin(admin.ModelAdmin):
    list_display = ('guide_title', 'guide_price', 'article_default_price', 'currency', 'is_active', 'updated_at')
    list_editable = ('guide_price', 'article_default_price', 'is_active')
    fieldsets = (
        ('Tarifs & Offres des Achats Numériques', {
            'fields': ('guide_title', 'guide_description', 'guide_price', 'article_default_price', 'currency', 'is_active'),
            'description': (
                '<div style="background-color: #e8f5e9; border-left: 4px solid #2e7d32; padding: 12px; margin-bottom: 15px; border-radius: 4px;">'
                '<strong>💡 Configuration des Prix d\'Achat à l\'Unité (Ebook PDF) :</strong><br/>'
                '• <strong>Guide Complet :</strong> Tarif fixé pour le téléchargement direct du PDF complet du manuel.<br/>'
                '• <strong>Article individuel :</strong> Tarif appliqué par défaut pour débloquer un article et télécharger son PDF '
                '(peut également être surchargé par article dans l\'administration des articles).'
                '</div>'
            )
        }),
        ('Intégration Chariow (Optionnel)', {
            'fields': ('guide_chariow_product_id', 'article_chariow_product_id'),
            'classes': ('collapse',)
        }),
    )

@admin.register(UserPurchase)
class UserPurchaseAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'purchase_type', 'item_title', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('purchase_type', 'status', 'currency', 'created_at')
    search_fields = ('transaction_id', 'user__email', 'user__username', 'post__title', 'chapter__title')
    readonly_fields = ('created_at',)

    def item_title(self, obj):
        if obj.purchase_type == 'full_guide':
            return "📖 Guide Complet"
        elif obj.post:
            return f"📰 {obj.post.title}"
        elif obj.chapter:
            return f"📄 {obj.chapter.title}"
        return "-"
    item_title.short_description = "Article / Guide"

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
