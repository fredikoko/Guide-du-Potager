from django.db import models
from django.conf import settings

PLAN_CHOICES = (
    ('monthly', 'Mensuel (2 500 XOF / ~4€)'),
    ('seasonal', 'Saison Potager - 3 Mois (5 000 XOF / ~8€)'),
    ('yearly', 'Annuel (15 000 XOF / ~23€)'),
)

STATUS_CHOICES = (
    ('active', 'Actif'),
    ('expired', 'Expiré'),
    ('canceled', 'Annulé'),
)

PAYMENT_METHODS = (
    ('chariow', 'Chariow (Mobile Money & Carte)'),
)

class SubscriptionPlan(models.Model):
    PLAN_TYPE_CHOICES = (
        ('monthly', 'Mensuel'),
        ('seasonal', 'Saison Potager (3 Mois)'),
        ('yearly', 'Annuel'),
    )

    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, unique=True, verbose_name="Type de formule")
    name = models.CharField(max_length=100, verbose_name="Nom affiché", help_text="Ex: Mensuel, Annuel")
    description = models.CharField(max_length=200, blank=True, default="", verbose_name="Courte description", help_text="Ex: Idéal pour un cycle complet de culture")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")
    currency = models.CharField(max_length=10, default='XOF', verbose_name="Devise")
    approx_eur = models.CharField(max_length=50, blank=True, default="", verbose_name="Équivalence indicative (ex: ~4€)")
    discount_badge = models.CharField(max_length=50, blank=True, default="", verbose_name="Badge promotionnel (ex: -30% ou Recommandé)")
    duration_days = models.PositiveIntegerField(default=30, verbose_name="Durée en jours")
    chariow_product_id = models.CharField(max_length=100, blank=True, verbose_name="ID Produit Chariow (optionnel)")
    is_featured = models.BooleanField(default=False, verbose_name="Formule recommandée")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    order = models.PositiveIntegerField(default=1, verbose_name="Ordre d'affichage")

    class Meta:
        ordering = ['order', 'price']
        verbose_name = "Formule d'abonnement"
        verbose_name_plural = "Formules d'abonnement"

    def __str__(self):
        formatted_price = f"{self.price:,.0f}".replace(",", " ")
        badge = f" ({self.discount_badge})" if self.discount_badge else ""
        return f"{self.name}{badge} - {formatted_price} {self.currency}"

    @property
    def formatted_price(self):
        return f"{self.price:,.0f}".replace(",", " ")

    @property
    def display_button_text(self):
        badge = f" ({self.discount_badge})" if self.discount_badge else ""
        approx = f" ({self.approx_eur})" if self.approx_eur else ""
        return f"{self.name}{badge}\n{self.formatted_price} {self.currency}{approx}"

class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    def __str__(self):
        return f"{self.user.email} - {self.get_plan_type_display()} ({self.status})"

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS, default='chariow')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='XOF')
    status = models.CharField(max_length=20, default='pending')  # pending, completed, failed
    transaction_id = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    pulse_delivery_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment #{self.transaction_id} - {self.user.email} ({self.status})"
