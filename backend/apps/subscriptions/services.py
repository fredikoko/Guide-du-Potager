import uuid
from datetime import timedelta
from django.utils import timezone
from .models import Subscription, Payment

class SubscriptionService:
    @staticmethod
    def calculate_end_date(plan_type):
        now = timezone.now()
        if plan_type == 'yearly':
            return now + timedelta(days=365)
        return now + timedelta(days=30)

    @staticmethod
    def get_plan_amount(plan_type):
        if plan_type == 'yearly':
            return 20000.00  # XOF
        return 2500.00  # XOF

    @classmethod
    def activate_subscription(cls, user, plan_type, payment_method, transaction_id, phone_number=''):
        amount = cls.get_plan_amount(plan_type)
        end_date = cls.calculate_end_date(plan_type)

        # Deactivate previous active subscriptions if any
        Subscription.objects.filter(user=user, status='active').update(status='expired')

        # Create new subscription
        subscription = Subscription.objects.create(
            user=user,
            plan_type=plan_type,
            amount=amount,
            status='active',
            end_date=end_date
        )

        # Record payment
        payment = Payment.objects.create(
            user=user,
            subscription=subscription,
            payment_method=payment_method,
            amount=amount,
            currency='XOF',
            status='completed',
            transaction_id=transaction_id or f"TX-{uuid.uuid4().hex[:10].upper()}",
            phone_number=phone_number
        )

        # Update User Profile
        profile = user.profile
        profile.subscription_active = True
        profile.subscription_end_date = end_date
        profile.save()

        return subscription, payment

class MobilePaymentService:
    """
    Simulation / Wrapper for Orange Money, Wave & MTN Mobile Money API integrations.
    """
    @staticmethod
    def process_mobile_payment(user, plan_type, provider, phone_number):
        amount = SubscriptionService.get_plan_amount(plan_type)
        tx_id = f"{provider.upper()[:2]}-{uuid.uuid4().hex[:8].upper()}"

        # In production, call provider REST API (Orange Money WebPay API / Wave Checkout API)
        # Here we simulate immediate successful confirmation:
        subscription, payment = SubscriptionService.activate_subscription(
            user=user,
            plan_type=plan_type,
            payment_method=provider,
            transaction_id=tx_id,
            phone_number=phone_number
        )

        return {
            'success': True,
            'message': f"Paiement {provider.replace('_', ' ').title()} réussi !",
            'transaction_id': tx_id,
            'amount': amount,
            'currency': 'XOF',
            'subscription_end_date': subscription.end_date
        }
