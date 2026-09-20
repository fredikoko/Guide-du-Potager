import hmac
import hashlib
import json
import logging
import uuid
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Payment
from .services import SubscriptionService

logger = logging.getLogger(__name__)
User = get_user_model()

class ChariowService:
    """
    Service pour interagir avec l'API Chariow (Checkout & Pulses Webhooks).
    Documentation officielle : https://chariow.dev
    """

    @staticmethod
    def get_base_url():
        return getattr(settings, 'CHARIOW_BASE_URL', 'https://api.chariow.com/v1').rstrip('/')

    @staticmethod
    def get_product_id_for_plan(plan_type):
        from .models import SubscriptionPlan
        plan = SubscriptionPlan.objects.filter(plan_type=plan_type, is_active=True).first()
        if plan and plan.chariow_product_id:
            return plan.chariow_product_id
        if plan_type == 'yearly':
            return getattr(settings, 'CHARIOW_PRODUCT_YEARLY_ID', '')
        return getattr(settings, 'CHARIOW_PRODUCT_MONTHLY_ID', '')

    @classmethod
    def create_checkout_session(cls, user, plan_type, redirect_url=None, customer_ip=None):
        """
        Initie une session de paiement Chariow en appelant POST /v1/checkout.
        Retourne l'URL de paiement sécurisée (checkout_url).
        """
        api_key = getattr(settings, 'CHARIOW_API_KEY', '')
        if not api_key:
            logger.error("CHARIOW_API_KEY non configurée dans les paramètres.")
            return {
                'success': False,
                'error': 'Le service de paiement Chariow n\'est pas configuré (clé API manquante).'
            }

        product_id = cls.get_product_id_for_plan(plan_type)
        if not product_id:
            logger.error(f"Aucun ID de produit Chariow configuré pour le plan : {plan_type}")
            return {
                'success': False,
                'error': f"ID de produit Chariow introuvable pour la formule {plan_type}."
            }

        first_name = user.first_name or getattr(user, 'username', '') or 'Client'
        last_name = user.last_name or ''

        payload = {
            'product_id': product_id,
            'email': user.email,
            'first_name': first_name,
            'last_name': last_name,
            'custom_metadata': {
                'user_id': str(user.id),
                'plan_type': plan_type,
            }
        }

        if redirect_url:
            payload['redirect_url'] = redirect_url
        if customer_ip:
            payload['customer_ip'] = customer_ip

        headers = {
            'Authorization': f"Bearer {api_key}",
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        endpoint = f"{cls.get_base_url()}/checkout"

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=15)
            data = response.json() if response.content else {}
        except requests.RequestException as exc:
            logger.exception("Erreur réseau lors de la communication avec l'API Chariow.")
            return {
                'success': False,
                'error': f"Erreur de communication avec Chariow : {str(exc)}"
            }

        if response.status_code not in (200, 201):
            err_msg = data.get('message') or data.get('error') or f"Erreur Chariow HTTP {response.status_code}"
            logger.warning(f"Échec de l'appel Chariow /checkout : {err_msg}")
            return {
                'success': False,
                'error': err_msg
            }

        # Extraire le lien de paiement depuis la réponse Chariow
        # Schémas supportés: data.payment.checkout_url, payment.checkout_url, ou direct checkout_url
        checkout_url = (
            data.get('data', {}).get('payment', {}).get('checkout_url')
            or data.get('payment', {}).get('checkout_url')
            or data.get('checkout_url')
        )

        if not checkout_url:
            # Si le produit est gratuit ou déjà validé
            step = data.get('step') or data.get('data', {}).get('step')
            if step == 'completed':
                # Activer directement l'abonnement
                sub, pay = SubscriptionService.activate_subscription(
                    user=user,
                    plan_type=plan_type,
                    payment_method='chariow',
                    transaction_id=f"CHARIOW-{uuid.uuid4().hex[:10].upper()}"
                )
                return {
                    'success': True,
                    'step': 'completed',
                    'message': 'Abonnement activé immédiatement.',
                    'subscription_id': sub.id
                }

            return {
                'success': False,
                'error': 'Impossible de récupérer l\'URL de paiement Chariow.'
            }

        # Enregistrer une transaction en attente (pending)
        plan_amount = SubscriptionService.get_plan_amount(plan_type)
        pending_tx_id = f"CHARIOW-INIT-{uuid.uuid4().hex[:10].upper()}"
        Payment.objects.create(
            user=user,
            subscription=None,
            payment_method='chariow',
            amount=plan_amount,
            currency='XOF',
            status='pending',
            transaction_id=pending_tx_id,
        )

        return {
            'success': True,
            'step': 'payment',
            'checkout_url': checkout_url,
            'transaction_id': pending_tx_id,
            'plan_type': plan_type,
            'amount': plan_amount,
        }

    @staticmethod
    def verify_webhook_signature(raw_body_bytes, signature_header):
        """
        Valide la signature HMAC-SHA256 envoyée dans l'en-tête 'x-chariow-signature'.
        Format attendu : sha256=<hex_digest> ou <hex_digest>
        """
        secret = getattr(settings, 'CHARIOW_WEBHOOK_SECRET', '')
        if not secret:
            logger.error("CHARIOW_WEBHOOK_SECRET non configuré.")
            return False

        if not signature_header:
            return False

        expected_sig = hmac.new(
            secret.encode('utf-8'),
            raw_body_bytes,
            hashlib.sha256
        ).hexdigest()

        given_sig = signature_header.strip()
        if given_sig.startswith('sha256='):
            given_sig = given_sig[len('sha256='):]

        return hmac.compare_digest(expected_sig, given_sig)

    @classmethod
    def process_webhook_event(cls, raw_body_bytes, signature_header, delivery_id=None, event_header=None):
        """
        Traite un événement de Webhook Chariow (Pulse).
        Vérifie la signature et applique l'idempotence avec delivery_id.
        Active l'abonnement si l'événement est 'successful.sale'.
        """
        # 1. Vérification de la signature
        if not cls.verify_webhook_signature(raw_body_bytes, signature_header):
            logger.warning("Rejet de webhook Chariow : signature HMAC invalide.")
            return False, "Signature invalide.", 401

        # 2. Vérification de l'idempotence via delivery_id
        if delivery_id and Payment.objects.filter(pulse_delivery_id=delivery_id).exists():
            logger.info(f"Webhook Chariow déjà traité pour la livraison : {delivery_id}")
            return True, "Événement déjà traité (idempotent).", 200

        # 3. Décodage du corps JSON
        try:
            payload = json.loads(raw_body_bytes.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            return False, "Corps JSON invalide.", 400

        event = payload.get('event') or event_header

        # 4. Traitement de la vente réussie (successful.sale)
        if event in ('successful.sale', 'sale.completed'):
            sale = payload.get('sale') or {}
            custom_metadata = payload.get('custom_metadata') or sale.get('custom_metadata') or {}
            customer = payload.get('customer') or {}

            user_id = custom_metadata.get('user_id')
            plan_type = custom_metadata.get('plan_type') or 'monthly'

            user = None
            if user_id:
                user = User.objects.filter(id=user_id).first()
            if not user and customer.get('email'):
                user = User.objects.filter(email=customer.get('email')).first()

            if not user:
                logger.error(f"Utilisateur introuvable pour la vente Chariow : user_id={user_id}, email={customer.get('email')}")
                return False, "Utilisateur introuvable pour ce paiement.", 404

            sale_id = str(sale.get('id') or sale.get('reference') or uuid.uuid4().hex[:10])
            tx_id = f"CHARIOW-{sale_id}"

            # Vérifier si ce paiement précis a déjà été enregistré
            existing_payment = Payment.objects.filter(transaction_id=tx_id).first()
            if existing_payment and existing_payment.status == 'completed':
                if delivery_id and not existing_payment.pulse_delivery_id:
                    existing_payment.pulse_delivery_id = delivery_id
                    existing_payment.save(update_fields=['pulse_delivery_id'])
                return True, "Paiement déjà validé.", 200

            # Activer l'abonnement
            subscription, payment = SubscriptionService.activate_subscription(
                user=user,
                plan_type=plan_type,
                payment_method='chariow',
                transaction_id=tx_id,
                phone_number=customer.get('phone', '') if isinstance(customer.get('phone'), str) else ''
            )

            # Associer l'ID de livraison du Pulse pour l'idempotence
            if delivery_id:
                payment.pulse_delivery_id = delivery_id
                payment.save(update_fields=['pulse_delivery_id'])

            logger.info(f"Abonnement Chariow activé avec succès pour {user.email} (plan={plan_type}, tx={tx_id})")
            return True, "Abonnement activé avec succès.", 200

        # Événement ignoré mais accusé de réception
        logger.info(f"Événement Chariow ignoré : {event}")
        return True, f"Événement '{event}' reçu et ignoré.", 200
