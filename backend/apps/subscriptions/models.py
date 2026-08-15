from django.db import models
from django.conf import settings

PLAN_CHOICES = (
    ('monthly', 'Mensuel (2 500 XOF / ~4€)'),
    ('yearly', 'Annuel (20 000 XOF / ~30€)'),
)

STATUS_CHOICES = (
    ('active', 'Actif'),
    ('expired', 'Expiré'),
    ('canceled', 'Annulé'),
)

PAYMENT_METHODS = (
    ('stripe', 'Carte Bancaire / Stripe'),
    ('orange_money', 'Orange Money (Afrique de l\'Ouest)'),
    ('wave', 'Wave (Afrique de l\'Ouest)'),
    ('mtn_money', 'MTN Mobile Money'),
)

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
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='XOF')
    status = models.CharField(max_length=20, default='pending')  # pending, completed, failed
    transaction_id = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment #{self.transaction_id} - {self.user.email} ({self.status})"
