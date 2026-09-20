from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.pests.models import Disease, Insect

User = get_user_model()

class PestsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.free_user = User.objects.create_user(
            email='free_pest@potager.fr',
            username='user_free_pest',
            password='Password123!'
        )
        self.premium_user = User.objects.create_user(
            email='prem_pest@potager.fr',
            username='user_prem_pest',
            password='Password123!'
        )
        self.premium_user.profile.subscription_active = True
        self.premium_user.profile.subscription_end_date = timezone.now() + timedelta(days=30)
        self.premium_user.profile.save()

        self.disease_free = Disease.objects.create(
            name="Mildiou de la Tomate",
            symptoms="Taches brunes sur feuilles",
            treatment="Bouillie bordelaise ou purin de prêle",
            prevention="Espacer les plants et arroser au pied",
            is_premium=False
        )
        self.disease_premium = Disease.objects.create(
            name="Virose du Flétrissement Bactérien",
            symptoms="Flétrissement subit de la plante",
            treatment="Arrachage immédiat et Solarisation du sol à 60°C",
            prevention="Rotation stricte de 4 ans sans solanacées",
            is_premium=True
        )

        self.insect_free = Insect.objects.create(
            name="Puceron Vert",
            description="Petits insectes suceurs de sève",
            damage="Enroulement des feuilles",
            solution="Savon noir dilué à 5% et purin d'ortie",
            is_premium=False
        )
        self.insect_premium = Insect.objects.create(
            name="Mouche Blanche (Aleurode)",
            description="Minuscules mouches blanches sous les feuilles",
            damage="Transmission de virus TYLCV",
            solution="Pièges chromatiques jaunes et lâchers d'Encarsia",
            is_premium=True
        )

    def test_list_diseases_and_insects(self):
        res_d = self.client.get(reverse('disease_list'))
        self.assertEqual(res_d.status_code, status.HTTP_200_OK)
        results_d = res_d.data.get('results', res_d.data)
        self.assertEqual(len(results_d), 2)

        res_i = self.client.get(reverse('insect_list'))
        self.assertEqual(res_i.status_code, status.HTTP_200_OK)
        results_i = res_i.data.get('results', res_i.data)
        self.assertEqual(len(results_i), 2)

    def test_disease_premium_locked_for_free_user(self):
        self.client.force_authenticate(user=self.free_user)
        url = reverse('disease_detail', kwargs={'pk': self.disease_premium.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data.get('is_locked'))
        self.assertIn("Contenu Premium", res.data['treatment'])
        self.assertNotIn("Solarisation", res.data['treatment'])

    def test_disease_premium_unlocked_for_premium_user(self):
        self.client.force_authenticate(user=self.premium_user)
        url = reverse('disease_detail', kwargs={'pk': self.disease_premium.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data.get('is_locked'))
        self.assertIn("Solarisation du sol", res.data['treatment'])

    def test_insect_premium_locked_for_free_user(self):
        self.client.force_authenticate(user=self.free_user)
        url = reverse('insect_detail', kwargs={'pk': self.insect_premium.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data.get('is_locked'))
        self.assertIn("Contenu Premium", res.data['solution'])
        self.assertNotIn("Encarsia", res.data['solution'])

    def test_insect_premium_unlocked_for_premium_user(self):
        self.client.force_authenticate(user=self.premium_user)
        url = reverse('insect_detail', kwargs={'pk': self.insect_premium.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data.get('is_locked'))
        self.assertIn("Encarsia", res.data['solution'])
