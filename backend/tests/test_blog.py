from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.blog.models import Category, Post, Comment, PostFAQ

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
        self.assertIn("Réservé aux Membres", res.data['rendered_content'])
        self.assertNotIn("secret des ollas", res.data['rendered_content'])

    def test_premium_post_unlocked_for_premium_user(self):
        self.client.force_authenticate(user=self.premium_user)
        url = reverse('blog_post_detail', kwargs={'pk': self.post_premium.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data.get('is_locked'))
        self.assertIn("secret des ollas", res.data['content'])
        self.assertIn("secret des ollas", res.data['rendered_content'])

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
        self.assertNotIn("secret des ollas", res.data['content'])
        self.assertIn("Réservé aux Membres", res.data['rendered_content'])
        self.assertNotIn("secret des ollas", res.data['rendered_content'])

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

    def test_post_faq_optional_and_serialized(self):
        # 1. An article without FAQs returns an empty list (FAQ is optional)
        url = reverse('blog_post_detail', kwargs={'pk': self.post_free.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('faqs', res.data)
        self.assertEqual(res.data['faqs'], [])

        # 2. Add 2 FAQs with custom ordering
        faq2 = PostFAQ.objects.create(
            post=self.post_free,
            question="Combien de temps faut-il pour obtenir du compost mûr ?",
            answer="En climat tropical, 6 à 8 semaines suffisent grâce à la chaleur.",
            order=2
        )
        faq1 = PostFAQ.objects.create(
            post=self.post_free,
            question="Quels déchets ne pas mettre dans le compost ?",
            answer="Évitez la viande, les produits laitiers et les plantes malades.",
            order=1
        )

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['faqs']), 2)
        # Verify ordering
        self.assertEqual(res.data['faqs'][0]['id'], faq1.id)
        self.assertEqual(res.data['faqs'][0]['question'], "Quels déchets ne pas mettre dans le compost ?")
        self.assertEqual(res.data['faqs'][1]['id'], faq2.id)

    def test_post_faq_web_view(self):
        # Without FAQ: no FAQ section title in HTML
        web_url = reverse('web:blog_detail', kwargs={'slug': self.post_free.slug})
        res = self.client.get(web_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotContains(res, "Foire Aux Questions (FAQ)")

        # With FAQ: section is displayed
        PostFAQ.objects.create(
            post=self.post_free,
            question="Quelle humidité maintenir ?",
            answer="Le compost doit être comme une éponge essorée.",
            order=1
        )
        res = self.client.get(web_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, "Foire Aux Questions (FAQ)")
        self.assertContains(res, "Quelle humidité maintenir ?")
        self.assertContains(res, "Le compost doit être comme une éponge essorée.")

    def test_scheduled_post_hidden_from_public(self):
        future_date = timezone.now() + timedelta(days=7)
        scheduled_post = Post.objects.create(
            title="Les cultures d'avenir sous climat sahélien",
            slug="cultures-avenir-sahel",
            author=self.author,
            category=self.category,
            excerpt="Analyse prospective des cultures résistantes.",
            content="<p>Moringa, niébé et fonio sont les piliers de demain.</p>",
            is_published=True,
            published_at=future_date
        )

        # 1. Vérification des propriétés du modèle
        self.assertTrue(scheduled_post.is_scheduled)
        self.assertFalse(scheduled_post.is_visible)
        self.assertEqual(scheduled_post.publication_status, "scheduled")
        self.assertNotIn(scheduled_post, Post.objects.published())

        # 2. Invisible sur l'API publique (PostListView)
        url_list = reverse('blog_post_list')
        res_list = self.client.get(url_list)
        results = res_list.data.get('results', res_list.data)
        ids = [p['id'] for p in results]
        self.assertNotIn(scheduled_post.id, ids)

        # 3. Invisible sur le détail API pour un utilisateur régulier (404)
        url_detail = reverse('blog_post_detail', kwargs={'pk': scheduled_post.pk})
        res_detail = self.client.get(url_detail)
        self.assertEqual(res_detail.status_code, status.HTTP_404_NOT_FOUND)

        # 4. Invisible sur le site Web pour un visiteur public (404)
        web_url = reverse('web:blog_detail', kwargs={'slug': scheduled_post.slug})
        web_res = self.client.get(web_url)
        self.assertEqual(web_res.status_code, 404)

        # 5. Visible pour un administrateur / staff avec mode prévisualisation
        staff_user = User.objects.create_user(
            email='admin@potager.fr',
            username='admin_staff',
            password='Password123!',
            is_staff=True
        )
        self.client.force_authenticate(user=staff_user)
        self.client.force_login(staff_user)
        res_staff_api = self.client.get(url_detail)
        self.assertEqual(res_staff_api.status_code, status.HTTP_200_OK)
        self.assertTrue(res_staff_api.data.get('is_scheduled'))

        res_staff_web = self.client.get(web_url)
        self.assertEqual(res_staff_web.status_code, 200)
        self.assertContains(res_staff_web, "Mode Prévisualisation Administrateur")
        self.assertContains(res_staff_web, "planifié")

        # 6. Devient accessible dès que la date de publication est échue
        scheduled_post.published_at = timezone.now() - timedelta(minutes=5)
        scheduled_post.save()
        self.assertTrue(scheduled_post.is_visible)
        self.assertFalse(scheduled_post.is_scheduled)
        self.client.force_authenticate(user=None)  # Public visitor
        self.client.logout()
        res_after = self.client.get(url_detail)
        self.assertEqual(res_after.status_code, status.HTTP_200_OK)
        web_res_after = self.client.get(web_url)
        self.assertEqual(web_res_after.status_code, 200)
