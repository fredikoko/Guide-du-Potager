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

    def test_register_user(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='testuser@potager.fr').exists())

    def test_login_user(self):
        User.objects.create_user(
            email='testuser@potager.fr',
            username='TestJardinier',
            password='Password123!'
        )
        response = self.client.post(self.login_url, {
            'email': 'testuser@potager.fr',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('user', response.data)

    def test_register_with_disposable_email_fails(self):
        data = self.user_data.copy()
        data['email'] = 'spammer@yopmail.com'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_with_invalid_email_syntax_fails(self):
        data = self.user_data.copy()
        data['email'] = 'invalid-email-without-domain'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validate_email_endpoint(self):
        validate_url = reverse('auth_validate_email')
        # Valid email
        res = self.client.post(validate_url, {'email': 'nouveau@potager.com', 'mode': 'register'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['valid'])

        # Disposable email
        res = self.client.post(validate_url, {'email': 'temp@tempmail.com', 'mode': 'register'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(res.data['valid'])

    def test_update_user_email(self):
        user = User.objects.create_user(
            email='initial@potager.com',
            username='jardinier_init',
            password='Password123!'
        )
        self.client.force_authenticate(user=user)
        profile_url = reverse('user_profile')

        # Successful email update
        res = self.client.put(profile_url, {'email': 'modifie@potager.com', 'username': 'jardinier_init'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.email, 'modifie@potager.com')

        # Duplicate email update fails
        User.objects.create_user(
            email='autre@potager.com',
            username='autre_user',
            password='Password123!'
        )
        res_dup = self.client.put(profile_url, {'email': 'autre@potager.com'})
        self.assertEqual(res_dup.status_code, status.HTTP_400_BAD_REQUEST)
