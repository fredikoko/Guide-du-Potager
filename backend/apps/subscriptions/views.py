from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import Subscription, Payment
from .serializers import (
    SubscriptionSerializer, PaymentSerializer,
    ChariowCheckoutRequestSerializer
)
from .services import SubscriptionService
from .chariow_service import ChariowService

class SubscriptionStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = user.profile
        now = timezone.now()

        # Sync subscription state with current date
        is_active = profile.subscription_active and (profile.subscription_end_date and profile.subscription_end_date > now)
        if profile.subscription_active and not is_active:
            profile.subscription_active = False
            profile.save()
            Subscription.objects.filter(user=user, status='active').update(status='expired')

        active_sub = Subscription.objects.filter(user=user, status='active').first()
        sub_data = SubscriptionSerializer(active_sub).data if active_sub else None

        return Response({
            'subscription_active': is_active,
            'subscription_end_date': profile.subscription_end_date,
            'active_subscription': sub_data
        })

class ChariowCheckoutView(APIView):
    """
    Initie une session de paiement Chariow pour l'utilisateur connecté.
    Retourne l'URL de paiement Chariow pour redirection.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChariowCheckoutRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        plan_type = serializer.validated_data['plan_type']
        redirect_url = serializer.validated_data.get('redirect_url')
        customer_ip = request.META.get('REMOTE_ADDR')

        result = ChariowService.create_checkout_session(
            user=request.user,
            plan_type=plan_type,
            redirect_url=redirect_url,
            customer_ip=customer_ip
        )

        if not result.get('success'):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_200_OK)

class ChariowWebhookView(APIView):
    """
    Endpoint public de réception des Webhooks Pulses Chariow.
    Vérifie la signature HMAC-SHA256 (x-chariow-signature) et active l'abonnement.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        signature = request.headers.get('x-chariow-signature') or request.META.get('HTTP_X_CHARIOW_SIGNATURE')
        delivery_id = request.headers.get('x-pulse-delivery-id') or request.META.get('HTTP_X_PULSE_DELIVERY_ID')
        event_header = request.headers.get('x-pulse-event') or request.META.get('HTTP_X_PULSE_EVENT')

        # DRF request.body donne les octets bruts pour la vérification HMAC
        raw_body = request.body

        success, message, status_code = ChariowService.process_webhook_event(
            raw_body_bytes=raw_body,
            signature_header=signature,
            delivery_id=delivery_id,
            event_header=event_header
        )

        return Response({'success': success, 'message': message}, status=status_code)
