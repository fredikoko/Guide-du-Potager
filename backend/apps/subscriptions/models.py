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


class DigitalProductPricing(models.Model):
    """
    Configuration administrable des tarifs pour les achats à l'unité :
    - Le Guide Complet en Ebook PDF
    - Les articles de blog individuels en PDF
    """
    guide_title = models.CharField(
        max_length=200,
        default="Le Guide Complet du Potager Tropical (Ebook PDF)",
        verbose_name="Titre commercial du Guide Complet"
    )
    guide_description = models.TextField(
        default="Accès complet et téléchargement immédiat au format PDF de l'ensemble des parties et chapitres agronomiques du guide.",
        verbose_name="Description de l'offre Guide Complet"
    )
    guide_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=5000.00,
        verbose_name="Prix du Guide Complet (XOF)",
        help_text="Tarif en Francs CFA (XOF) pour l'achat définitif du Guide Complet avec téléchargement PDF"
    )
    article_default_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=500.00,
        verbose_name="Prix par défaut d'un Article individuel (XOF)",
        help_text="Tarif en Francs CFA (XOF) pour l'achat d'un article individuel avec lecture débloquée et téléchargement PDF"
    )
    currency = models.CharField(max_length=10, default='XOF', verbose_name="Devise")
    guide_chariow_product_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="ID Produit Chariow Guide Complet",
        help_text="Optionnel : Identifiant du produit sur Chariow pour le Guide complet"
    )
    article_chariow_product_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="ID Produit Chariow Article",
        help_text="Optionnel : Identifiant du produit sur Chariow pour les articles à l'unité"
    )
    is_active = models.BooleanField(default=True, verbose_name="Tarification active")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")

    class Meta:
        verbose_name = "Tarification des Achats Numériques (Guide & Articles)"
        verbose_name_plural = "Tarification des Achats Numériques"

    def __str__(self):
        g_price = f"{self.guide_price:,.0f}".replace(",", " ")
        a_price = f"{self.article_default_price:,.0f}".replace(",", " ")
        return f"Tarifs Numériques : Guide ({g_price} {self.currency}) | Article ({a_price} {self.currency})"

    @property
    def formatted_guide_price(self):
        return f"{self.guide_price:,.0f}".replace(",", " ")

    @property
    def formatted_article_price(self):
        return f"{self.article_default_price:,.0f}".replace(",", " ")

    @classmethod
    def get_pricing(cls):
        pricing = cls.objects.filter(is_active=True).first()
        if not pricing:
            pricing = cls.objects.create()
        return pricing


class UserPurchase(models.Model):
    """
    Enregistre les achats définitifs à l'unité réalisés par un utilisateur :
    - Guide Complet (Ebook PDF)
    - Article individuel du blog
    - Chapitre individuel
    """
    PURCHASE_TYPE_CHOICES = (
        ('full_guide', 'Guide Complet (Ebook PDF)'),
        ('post', 'Article de Blog (PDF)'),
        ('chapter', 'Chapitre du Guide (PDF)'),
    )
    STATUS_CHOICES = (
        ('completed', 'Validé / Complété'),
        ('pending', 'En attente'),
        ('failed', 'Échoué'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases', verbose_name="Client")
    purchase_type = models.CharField(max_length=20, choices=PURCHASE_TYPE_CHOICES, verbose_name="Type de produit")
    post = models.ForeignKey('blog.Post', on_delete=models.SET_NULL, null=True, blank=True, related_name='purchases', verbose_name="Article concerné")
    chapter = models.ForeignKey('content.Chapter', on_delete=models.SET_NULL, null=True, blank=True, related_name='purchases', verbose_name="Chapitre concerné")
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant payé")
    currency = models.CharField(max_length=10, default='XOF', verbose_name="Devise")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed', verbose_name="Statut de l'achat")
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchases', verbose_name="Paiement associé")
    transaction_id = models.CharField(max_length=100, unique=True, verbose_name="ID Transaction")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'achat")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Achat Numérique (Guide / Article)"
        verbose_name_plural = "Achats Numériques (Guide / Articles)"

    def __str__(self):
        desc = "Guide Complet" if self.purchase_type == 'full_guide' else (
            self.post.title if self.post else (self.chapter.title if self.chapter else self.purchase_type)
        )
        amt = f"{self.amount:,.0f}".replace(",", " ")
        return f"{self.user.email} - {desc} ({amt} {self.currency}) [{self.get_status_display()}]"

