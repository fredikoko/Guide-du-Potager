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
