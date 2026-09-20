from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('auth_register')
        self.login_url = reverse('auth_login')
        self.user_data = {
            'email': 'testuser@potager.fr',
            'username': 'TestJardinier',
            'password': 'Password123!',
            'password_confirm': 'Password123!'
        }

    def test_register_user_sends_code(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get('requires_verification'))
        user = User.objects.get(email='testuser@potager.fr')
        self.assertFalse(user.is_active)

    def test_verify_registration_flow(self):
        from apps.accounts.models import EmailVerificationCode
        self.client.post(self.register_url, self.user_data)
        code_record = EmailVerificationCode.objects.filter(
            email='testuser@potager.fr',
            purpose='registration',
            is_used=False
        ).first()
        self.assertIsNotNone(code_record)

        verify_url = reverse('auth_verify_registration')
        # Bad code fails
        bad_res = self.client.post(verify_url, {'email': 'testuser@potager.fr', 'code': '000000'})
        self.assertEqual(bad_res.status_code, status.HTTP_400_BAD_REQUEST)

        # Correct code activates user and returns tokens
        res = self.client.post(verify_url, {'email': 'testuser@potager.fr', 'code': code_record.code})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        user = User.objects.get(email='testuser@potager.fr')
        self.assertTrue(user.is_active)

    def test_resend_verification_code(self):
        from apps.accounts.models import EmailVerificationCode
        self.client.post(self.register_url, self.user_data)
        first_code = EmailVerificationCode.objects.get(email='testuser@potager.fr', purpose='registration', is_used=False).code

        resend_url = reverse('auth_resend_code')
        res = self.client.post(resend_url, {'email': 'testuser@potager.fr', 'purpose': 'registration'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        new_code_rec = EmailVerificationCode.objects.filter(email='testuser@potager.fr', purpose='registration', is_used=False).first()
        self.assertIsNotNone(new_code_rec)

    def test_email_change_flow(self):
        from apps.accounts.models import EmailVerificationCode
        user = User.objects.create_user(
            email='initial@potager.com',
            username='jardinier_init',
            password='Password123!'
        )
        self.client.force_authenticate(user=user)

        # 1. Update profile with new email initiates verification
        profile_url = reverse('user_profile')
        res = self.client.put(profile_url, {'email': 'modifie@potager.com', 'username': 'jardinier_init'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data.get('email_change_pending'))
        user.refresh_from_db()
        self.assertEqual(user.email, 'initial@potager.com')  # Pas encore changé

        # Code exists in DB
        code_record = EmailVerificationCode.objects.filter(
            email='modifie@potager.com',
            purpose='email_change',
            is_used=False
        ).first()
        self.assertIsNotNone(code_record)

        # 2. Confirm email change with correct code
        confirm_url = reverse('user_confirm_email_change')
        bad_confirm = self.client.post(confirm_url, {'new_email': 'modifie@potager.com', 'code': '999999'})
        self.assertEqual(bad_confirm.status_code, status.HTTP_400_BAD_REQUEST)

        good_confirm = self.client.post(confirm_url, {'new_email': 'modifie@potager.com', 'code': code_record.code})
        self.assertEqual(good_confirm.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.email, 'modifie@potager.com')  # Email confirmé et modifié !

        # 3. Duplicate email request fails
        User.objects.create_user(
            email='autre@potager.com',
            username='autre_user',
            password='Password123!'
        )
        res_dup = self.client.put(profile_url, {'email': 'autre@potager.com'})
        self.assertEqual(res_dup.status_code, status.HTTP_400_BAD_REQUEST)
