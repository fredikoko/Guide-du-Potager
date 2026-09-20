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

    def test_password_reset_flow(self):
        from apps.accounts.models import EmailVerificationCode
        user = User.objects.create_user(
            email='reset_target@potager.fr',
            username='reset_user',
            password='OldPassword123!'
        )

        reset_req_url = reverse('auth_password_reset')
        # 1. Request password reset (anti-enumeration message)
        res = self.client.post(reset_req_url, {'email': 'reset_target@potager.fr'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('Si cette adresse email', res.data['message'])

        code_rec = EmailVerificationCode.objects.filter(
            email='reset_target@potager.fr',
            purpose='password_reset',
            is_used=False
        ).first()
        self.assertIsNotNone(code_rec)

        # 2. Confirm password reset with bad code
        confirm_url = reverse('auth_password_reset_confirm')
        res_bad = self.client.post(confirm_url, {
            'email': 'reset_target@potager.fr',
            'code': '000000',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!'
        })
        self.assertEqual(res_bad.status_code, status.HTTP_400_BAD_REQUEST)

        # 3. Confirm password reset with valid code
        res_good = self.client.post(confirm_url, {
            'email': 'reset_target@potager.fr',
            'code': code_rec.code,
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!'
        })
        self.assertEqual(res_good.status_code, status.HTTP_200_OK)

        # 4. Login succeeds with new password
        user.refresh_from_db()
        self.assertTrue(user.check_password('NewPassword123!'))

    def test_otp_max_failed_attempts(self):
        from apps.accounts.models import EmailVerificationCode
        from apps.accounts.services import send_verification_email, verify_email_code
        from django.core.exceptions import ValidationError

        email = 'brute_force@potager.fr'
        send_verification_email(email, purpose='registration')

        code_rec = EmailVerificationCode.objects.get(email=email, purpose='registration', is_used=False)

        # 5 consecutive bad guesses
        for i in range(4):
            with self.assertRaises(ValidationError):
                verify_email_code(email, f"99999{i}", purpose='registration')

        # 5th attempt invalidates code
        with self.assertRaises(ValidationError) as cm:
            verify_email_code(email, "999999", purpose='registration')
        self.assertIn("Nombre maximal", str(cm.exception))

        code_rec.refresh_from_db()
        self.assertTrue(code_rec.is_used)
