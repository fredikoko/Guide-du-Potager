import uuid
import logging
from django.conf import settings
from .models import DigitalProductPricing, UserPurchase, Payment
from .services import SubscriptionService

logger = logging.getLogger(__name__)

class PurchaseService:
    @staticmethod
    def get_pricing():
        return DigitalProductPricing.get_pricing()

    @staticmethod
    def user_has_guide_access(user):
        """Vérifie si l'utilisateur possède l'accès au Guide Complet en téléchargement."""
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user.is_staff:
            return True
        return UserPurchase.objects.filter(
            user=user,
            purchase_type='full_guide',
            status='completed'
        ).exists()

    @classmethod
    def user_has_post_access(cls, user, post):
        """
        Vérifie si l'utilisateur peut lire intégralement et télécharger l'article :
        - Gratuit si post non-premium
        - Débloqué si staff/admin
        - Débloqué si abonné actif
        - Débloqué si achat à l'unité de cet article
        """
        if not post.is_premium:
            return True
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user.is_staff:
            return True

        # Vérifier si l'utilisateur possède un abonnement en cours
        profile = getattr(user, 'profile', None)
        if profile and profile.subscription_active:
            from django.utils import timezone
            if profile.subscription_end_date and profile.subscription_end_date > timezone.now():
                return True

        # Vérifier si l'utilisateur a acheté cet article à l'unité
        return UserPurchase.objects.filter(
            user=user,
            post=post,
            status='completed'
        ).exists()

    @classmethod
    def record_completed_purchase(cls, user, purchase_type, post=None, chapter=None, payment_method='chariow', transaction_id=None, phone_number=''):
        """
        Enregistre un achat numérique complété (Guide complet ou Article)
        avec traçabilité du paiement.
        """
        pricing = cls.get_pricing()

        if purchase_type == 'full_guide':
            amount = pricing.guide_price
        elif purchase_type == 'post' and post:
            amount = post.purchase_price
        elif purchase_type == 'chapter' and chapter:
            amount = chapter.purchase_price
        else:
            amount = pricing.article_default_price

        tx_id = transaction_id or f"BUY-{uuid.uuid4().hex[:12].upper()}"

        payment = Payment.objects.create(
            user=user,
            subscription=None,
            payment_method=payment_method,
            amount=amount,
            currency=pricing.currency,
            status='completed',
            transaction_id=tx_id,
            phone_number=phone_number
        )

        purchase = UserPurchase.objects.create(
            user=user,
            purchase_type=purchase_type,
            post=post,
            chapter=chapter,
            amount=amount,
            currency=pricing.currency,
            status='completed',
            payment=payment,
            transaction_id=tx_id
        )

        logger.info(f"Achat numérique validé pour {user.email} : {purchase}")
        return purchase, payment
