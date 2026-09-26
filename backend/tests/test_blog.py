from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.blog.models import Category, Post, Comment

User = get_user_model()

class BlogAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author = User.objects.create_user(
            email='author@potager.fr',
            username='redacteur',
            password='Password123!'
        )
        self.free_user = User.objects.create_user(
            email='free@potager.fr',
            username='user_free',
            password='Password123!'
        )
        self.premium_user = User.objects.create_user(
            email='subscriber@potager.fr',
            username='user_premium',
            password='Password123!'
        )
        self.premium_user.profile.subscription_active = True
        self.premium_user.profile.subscription_end_date = timezone.now() + timedelta(days=30)
        self.premium_user.profile.save()

        self.category = Category.objects.create(
            name="Permaculture Tropicale",
            slug="permaculture-tropicale",
            description="Techniques de permaculture adaptées au climat chaud."
        )

        self.post_free = Post.objects.create(
            title="Comment fabriquer du compost tropical",
            slug="compost-tropical",
            author=self.author,
            category=self.category,
            excerpt="Guide simple pour recycler la matière organique.",
            content="<p>Voici les étapes détaillées pour faire un super compost tropical.</p>",
            is_published=True,
            is_premium=False
        )

        self.post_premium = Post.objects.create(
            title="Stratégies secrètes contre la sécheresse sahélienne",
            slug="strategies-secheresse",
            author=self.author,
            category=self.category,
            excerpt="Méthodes avancées de rétention d'eau.",
            content="<p>Voici le secret des ollas et du paillage dense de 20cm.</p>",
            is_published=True,
            is_premium=True
        )

    def test_list_published_posts(self):
        url = reverse('blog_post_list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data.get('results', res.data)
        self.assertEqual(len(results), 2)

    def test_filter_posts_by_search(self):
        url = reverse('blog_post_list')
        res = self.client.get(url, {'search': 'sécheresse'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data.get('results', res.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], self.post_premium.id)

    def test_free_post_accessible_unauthenticated(self):
        url = reverse('blog_post_detail', kwargs={'pk': self.post_free.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data.get('is_locked'))
        self.assertIn("super compost tropical", res.data['content'])

    def test_premium_post_locked_for_free_user(self):
        self.client.force_authenticate(user=self.free_user)
        url = reverse('blog_post_detail', kwargs={'pk': self.post_premium.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data.get('is_locked'))
        self.assertIn("Réservé aux Membres", res.data['content'])
        self.assertNotIn("secret des ollas", res.data['content'])

    def test_premium_post_unlocked_for_premium_user(self):
        self.client.force_authenticate(user=self.premium_user)
        url = reverse('blog_post_detail', kwargs={'pk': self.post_premium.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data.get('is_locked'))
        self.assertIn("secret des ollas", res.data['content'])

    def test_premium_post_locked_if_subscription_expired(self):
        # Even if subscription_active is True in DB, if end date is in the past, user is locked
        expired_user = User.objects.create_user(
            email='expired@potager.fr',
            username='user_expired',
            password='Password123!'
        )
        expired_user.profile.subscription_active = True
        expired_user.profile.subscription_end_date = timezone.now() - timedelta(days=2)
        expired_user.profile.save()

        self.client.force_authenticate(user=expired_user)
        url = reverse('blog_post_detail', kwargs={'pk': self.post_premium.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data.get('is_locked'))
        self.assertIn("Réservé aux Membres", res.data['content'])

    def test_add_comment_flow(self):
        url = reverse('blog_add_comment', kwargs={'pk': self.post_free.pk})

        # Unauthenticated request fails
        res_anon = self.client.post(url, {'content': 'Super article !'})
        self.assertEqual(res_anon.status_code, status.HTTP_401_UNAUTHORIZED)

        # Authenticated user succeeds
        self.client.force_authenticate(user=self.free_user)
        res_auth = self.client.post(url, {'content': 'Merci pour cette fiche compost !'})
        self.assertEqual(res_auth.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.filter(post=self.post_free).count(), 1)
