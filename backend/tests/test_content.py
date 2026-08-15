from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.content.models import Part, Chapter
from django.contrib.auth import get_user_model

User = get_user_model()

class ContentAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.part = Part.objects.create(title="Partie 1", order=1, is_premium=False)
        self.chapter_free = Chapter.objects.create(
            part=self.part, title="Chapitre Gratuit", content="Contenu gratuit", order=1, is_premium=False
        )
        self.chapter_premium = Chapter.objects.create(
            part=self.part, title="Chapitre Premium", content="Contenu secret", order=2, is_premium=True
        )

    def test_list_parts(self):
        url = reverse('part_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_free_chapter_access(self):
        url = reverse('chapter_detail', kwargs={'pk': self.chapter_free.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_locked'])
        self.assertEqual(response.data['content'], "Contenu gratuit")

    def test_premium_chapter_access_unsubscribed(self):
        url = reverse('chapter_detail', kwargs={'pk': self.chapter_premium.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_locked'])
        self.assertIn("abonnés Premium", response.data['content'])
