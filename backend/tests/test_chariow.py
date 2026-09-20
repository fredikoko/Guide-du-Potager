import json
import hmac
import hashlib
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.subscriptions.models import Subscription, Payment

User = get_user_model()

@override_settings(
    CHARIOW_API_KEY='test_api_key_123',
    CHARIOW_WEBHOOK_SECRET='test_secret_key_456',
    CHARIOW_BASE_URL='https://api.chariow.com/v1',
    CHARIOW_PRODUCT_MONTHLY_ID='prd_test_monthly',
    CHARIOW_PRODUCT_YEARLY_ID='prd_test_yearly'
)
class ChariowIntegrationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='chariow_user@potager.fr',
            username='chariow_user',
            password='Password123!'
        )
        self.client.force_authenticate(user=self.user)
        self.checkout_url = reverse('chariow_checkout')
        self.webhook_url = reverse('chariow_webhook')

    @patch('requests.post')
    def test_checkout_initiation_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"success": true}'
        mock_response.json.return_value = {
            'step': 'payment',
            'data': {
                'payment': {
                    'checkout_url': 'https://checkout.chariow.com/pay/session_abc123'
                }
            }
        }
        mock_post.return_value = mock_response

        response = self.client.post(self.checkout_url, {
            'plan_type': 'monthly',
            'redirect_url': 'https://potager.app/payment-success'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['checkout_url'], 'https://checkout.chariow.com/pay/session_abc123')

        # Check pending payment created
        pending = Payment.objects.filter(user=self.user, payment_method='chariow', status='pending').first()
        self.assertIsNotNone(pending)
        self.assertEqual(pending.amount, 2500.00)

    def test_checkout_invalid_plan(self):
        response = self.client.post(self.checkout_url, {
            'plan_type': 'invalid_plan'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(CHARIOW_API_KEY='')
    def test_checkout_unconfigured_api_key(self):
        response = self.client.post(self.checkout_url, {
            'plan_type': 'monthly'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_webhook_rejects_invalid_signature(self):
        payload = json.dumps({'event': 'successful.sale'}).encode('utf-8')
        response = self.client.post(
            self.webhook_url,
            data=payload,
            content_type='application/json',
            HTTP_X_CHARIOW_SIGNATURE='sha256=invalid_signature'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])

    def test_webhook_successful_sale_activates_subscription(self):
        secret = 'test_secret_key_456'
        body_dict = {
            'event': 'successful.sale',
            'sale': {
                'id': 'sale_test_999',
                'amount': 2500,
                'currency': 'XOF'
            },
            'customer': {
                'email': self.user.email,
                'phone': '+221771234567'
            },
            'custom_metadata': {
                'user_id': str(self.user.id),
                'plan_type': 'monthly'
            }
        }
        body_bytes = json.dumps(body_dict).encode('utf-8')
        valid_signature = hmac.new(secret.encode('utf-8'), body_bytes, hashlib.sha256).hexdigest()

        response = self.client.post(
            self.webhook_url,
            data=body_bytes,
            content_type='application/json',
            HTTP_X_CHARIOW_SIGNATURE=f"sha256={valid_signature}",
            HTTP_X_PULSE_DELIVERY_ID="del_uuid_1001"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

        # Verify profile is active
        self.user.refresh_from_db()
        self.assertTrue(self.user.profile.subscription_active)
        self.assertIsNotNone(self.user.profile.subscription_end_date)

        # Verify active subscription
        sub = Subscription.objects.filter(user=self.user, status='active').first()
        self.assertIsNotNone(sub)
        self.assertEqual(sub.plan_type, 'monthly')

        # Verify payment marked completed
        payment = Payment.objects.filter(user=self.user, payment_method='chariow', status='completed').first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.pulse_delivery_id, "del_uuid_1001")
        self.assertEqual(payment.transaction_id, "CHARIOW-sale_test_999")

    def test_webhook_idempotency(self):
        secret = 'test_secret_key_456'
        body_dict = {
            'event': 'successful.sale',
            'sale': {
                'id': 'sale_test_idempotent',
                'amount': 20000,
                'currency': 'XOF'
            },
            'custom_metadata': {
                'user_id': str(self.user.id),
                'plan_type': 'yearly'
            }
        }
        body_bytes = json.dumps(body_dict).encode('utf-8')
        signature = f"sha256={hmac.new(secret.encode('utf-8'), body_bytes, hashlib.sha256).hexdigest()}"

        # First delivery
        res1 = self.client.post(
            self.webhook_url,
            data=body_bytes,
            content_type='application/json',
            HTTP_X_CHARIOW_SIGNATURE=signature,
            HTTP_X_PULSE_DELIVERY_ID="del_uuid_idempotent_1"
        )
        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        # Second delivery with same delivery ID
        res2 = self.client.post(
            self.webhook_url,
            data=body_bytes,
            content_type='application/json',
            HTTP_X_CHARIOW_SIGNATURE=signature,
            HTTP_X_PULSE_DELIVERY_ID="del_uuid_idempotent_1"
        )
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertIn("déjà traité", res2.data['message'])

        # Check only 1 active subscription exists
        self.assertEqual(Subscription.objects.filter(user=self.user, status='active').count(), 1)

    def test_subscription_plans_endpoint_and_custom_admin_price(self):
        from apps.subscriptions.models import SubscriptionPlan
        plans_url = reverse('subscription_plans')
        res = self.client.get(plans_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        plans = res.data.get('results', res.data)
        self.assertEqual(len(plans), 2)

        # Modifier le prix depuis l'admin (en DB)
        plan_monthly = SubscriptionPlan.objects.get(plan_type='monthly')
        plan_monthly.price = 3000.00
        plan_monthly.approx_eur = '~4.50€'
        plan_monthly.save()

        # Vérifier que l'API renvoie immédiatement le nouveau prix
        res2 = self.client.get(plans_url)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        plans2 = res2.data.get('results', res2.data)
        monthly_data = next(p for p in plans2 if p['plan_type'] == 'monthly')
        self.assertEqual(float(monthly_data['price']), 3000.00)
        self.assertIn('3 000', monthly_data['formatted_price'])
        self.assertIn('~4.50€', monthly_data['display_button_text'])
