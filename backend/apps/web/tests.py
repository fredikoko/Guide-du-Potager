from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.content.models import Part, Chapter
from apps.glossary.models import PlantFamily, Vegetable, Tool, CalendarEntry
from apps.pests.models import Disease, Insect
from apps.blog.models import Category, Post
from apps.subscriptions.models import SubscriptionPlan, Subscription
from apps.accounts.models import UserProfile

User = get_user_model()

class WebAppTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Utilisateur gratuit
        self.free_user = User.objects.create_user(
            username='jardinier_gratuit',
            email='gratuit@potager.com',
            password='Password123!'
        )

        # Utilisateur abonné (Premium)
        self.premium_user = User.objects.create_user(
            username='jardinier_abonne',
            email='abonne@potager.com',
            password='Password123!'
        )
        self.premium_profile = self.premium_user.profile
        self.premium_profile.subscription_active = True
        self.premium_profile.subscription_end_date = timezone.now() + timedelta(days=90)
        self.premium_profile.save()

        # Données de test
        self.part = Part.objects.create(title="Partie 1 : Sol Vivant", order=1, is_premium=False)
        self.free_chapter = Chapter.objects.create(
            part=self.part, title="Chapitre 1 : Compostage", content="<p>Texte compostage</p>", order=1, is_premium=False
        )
        self.premium_chapter = Chapter.objects.create(
            part=self.part, title="Chapitre 2 : Biopesticides", content="<p>Recette secrète</p>", order=2, is_premium=True
        )

        self.family = PlantFamily.objects.create(name="Solanacées", description="Famille de la tomate")
        self.vegetable = Vegetable.objects.create(
            family=self.family, name="Tomate Mongal F1", sowing_period="Octobre", harvest_period="Janvier", care_tips="Arrosage régulier"
        )
        self.calendar_entry = CalendarEntry.objects.create(
            vegetable=self.vegetable, action='semis', month=10, notes="Semer en pépinière ombragée"
        )

        self.tool_free = Tool.objects.create(name="Râteau maraîcher", description="Nivellement", is_premium=False)
        self.tool_prem = Tool.objects.create(name="Grelinette 5 dents", description="Aération sol", is_premium=True)

        self.disease_prem = Disease.objects.create(
            name="Mildiou de la Tomate", symptoms="Taches brunes", treatment="Bouillie bordelaise", prevention="Aération", is_premium=True
        )
        self.insect_prem = Insect.objects.create(
            name="Mouche Blanche", description="Aleurode", damage="Pique les feuilles", solution="Savon noir", is_premium=True
        )

        self.category = Category.objects.create(name="Astuces Bio", slug="astuces-bio")
        self.post = Post.objects.create(
            category=self.category, title="Préparer le sol en saison sèche", excerpt="Résumé", content="<p>Détail</p>", is_published=True
        )

        self.plan = SubscriptionPlan.objects.create(
            plan_type='seasonal', name='Pass Saison (3 Mois)', price=5000.00, currency='XOF', duration_days=90
        )

    def test_home_view(self):
        response = self.client.get(reverse('web:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Guide du Potager")
        self.assertContains(response, "Partie 1 : Sol Vivant")
        self.assertContains(response, "Chapitre 1 : Compostage")

    def test_free_chapter_accessible_to_all(self):
        response = self.client.get(reverse('web:chapter_detail', args=[self.free_chapter.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Texte compostage")
        self.assertNotContains(response, "Débloquez ce guide avec votre Pass Potager")

    def test_premium_chapter_paywall_for_free_user(self):
        # Visiteur anonyme
        response = self.client.get(reverse('web:chapter_detail', args=[self.premium_chapter.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Débloquez ce guide avec votre Pass Potager")

        # Utilisateur gratuit connecté
        self.client.login(username='gratuit@potager.com', password='Password123!')
        response = self.client.get(reverse('web:chapter_detail', args=[self.premium_chapter.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Débloquez ce guide avec votre Pass Potager")

    def test_premium_chapter_accessible_to_premium_user(self):
        self.client.login(username='abonne@potager.com', password='Password123!')
        response = self.client.get(reverse('web:chapter_detail', args=[self.premium_chapter.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recette secrète")
        self.assertNotContains(response, "Débloquez ce guide avec votre Pass Potager")

    def test_vegetables_views(self):
        resp_list = self.client.get(reverse('web:vegetables_list'))
        self.assertEqual(resp_list.status_code, 200)
        self.assertContains(resp_list, "Tomate Mongal F1")

        resp_detail = self.client.get(reverse('web:vegetable_detail', args=[self.vegetable.id]))
        self.assertEqual(resp_detail.status_code, 200)
        self.assertContains(resp_detail, "Solanacées")
        self.assertContains(resp_detail, "Arrosage régulier")

    def test_calendar_view(self):
        response = self.client.get(reverse('web:calendar') + '?month=10')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tomate Mongal F1")
        self.assertContains(response, "Semer en pépinière ombragée")

    def test_tools_views_and_paywall(self):
        # Liste
        resp_list = self.client.get(reverse('web:tools_list'))
        self.assertEqual(resp_list.status_code, 200)
        self.assertContains(resp_list, "Grelinette 5 dents")

        # Gratuit -> Paywall sur outil premium
        resp_prem = self.client.get(reverse('web:tool_detail', args=[self.tool_prem.id]))
        self.assertEqual(resp_prem.status_code, 200)
        self.assertContains(resp_prem, "Débloquez ce guide avec votre Pass Potager")

        # Abonné -> Accès libre
        self.client.login(username='abonne@potager.com', password='Password123!')
        resp_prem_auth = self.client.get(reverse('web:tool_detail', args=[self.tool_prem.id]))
        self.assertEqual(resp_prem_auth.status_code, 200)
        self.assertContains(resp_prem_auth, "Aération sol")

    def test_diseases_paywall(self):
        response = self.client.get(reverse('web:disease_detail', args=[self.disease_prem.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Débloquez ce guide avec votre Pass Potager")

        self.client.login(username='abonne@potager.com', password='Password123!')
        response_auth = self.client.get(reverse('web:disease_detail', args=[self.disease_prem.id]))
        self.assertEqual(response_auth.status_code, 200)
        self.assertContains(response_auth, "Bouillie bordelaise")

    def test_insects_paywall(self):
        response = self.client.get(reverse('web:insect_detail', args=[self.insect_prem.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Débloquez ce guide avec votre Pass Potager")

        self.client.login(username='abonne@potager.com', password='Password123!')
        response_auth = self.client.get(reverse('web:insect_detail', args=[self.insect_prem.id]))
        self.assertEqual(response_auth.status_code, 200)
        self.assertContains(response_auth, "Savon noir")

    def test_blog_views(self):
        resp_list = self.client.get(reverse('web:blog_list'))
        self.assertEqual(resp_list.status_code, 200)
        self.assertContains(resp_list, "Préparer le sol en saison sèche")

        resp_detail = self.client.get(reverse('web:blog_detail', args=[self.post.slug]))
        self.assertEqual(resp_detail.status_code, 200)
        self.assertContains(resp_detail, "Astuces Bio")

    def test_subscription_view(self):
        response = self.client.get(reverse('web:subscription'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pass Saison (3 Mois)")
        self.assertContains(response, "5 000")

    def test_auth_workflow(self):
        # Connexion avec email
        login_resp = self.client.post(reverse('web:login'), {
            'login': 'gratuit@potager.com',
            'password': 'Password123!'
        })
        self.assertEqual(login_resp.status_code, 302)

        # Accès profil
        prof_resp = self.client.get(reverse('web:profile'))
        self.assertEqual(prof_resp.status_code, 200)
        self.assertContains(prof_resp, "gratuit@potager.com")

        # Déconnexion
        logout_resp = self.client.get(reverse('web:logout'))
        self.assertEqual(logout_resp.status_code, 302)

    def test_about_view(self):
        response = self.client.get(reverse('web:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Notre Mission")
