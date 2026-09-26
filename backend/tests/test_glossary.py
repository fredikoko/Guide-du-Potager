from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.glossary.models import Tool, PlantFamily, Vegetable, CalendarEntry

class GlossaryAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Tools
        self.tool1 = Tool.objects.create(
            name="Grelinette",
            category="travail_sol",
            description="Aérofourche pour ameublir sans retourner.",
            is_premium=False
        )
        self.tool2 = Tool.objects.create(
            name="Semoir de Précision",
            category="semis",
            description="Semoir pour petites graines maraîchères.",
            is_premium=True
        )

        # Families & Vegetables
        self.family_solanacees = PlantFamily.objects.create(
            name="Solanacées",
            description="Famille de la tomate, piment et aubergine."
        )
        self.family_cucurbitacees = PlantFamily.objects.create(
            name="Cucurbitacées",
            description="Famille de la courge, concombre et pastèque."
        )

        self.veg_tomate = Vegetable.objects.create(
            name="Tomate Cerise Tropicale",
            scientific_name="Solanum lycopersicum",
            family=self.family_solanacees,
            sowing_period="Octobre à Mars",
            harvest_period="Décembre à Mai",
            is_premium=False
        )
        self.veg_aubergine = Vegetable.objects.create(
            name="Aubergine Africaine (Diakhatou)",
            scientific_name="Solanum aethiopicum",
            family=self.family_solanacees,
            sowing_period="Toute l'année",
            harvest_period="Toute l'année",
            is_premium=False
        )
        self.veg_gombo = Vegetable.objects.create(
            name="Gombo Tropical",
            scientific_name="Abelmoschus esculentus",
            family=self.family_cucurbitacees,
            sowing_period="Juin à Septembre",
            harvest_period="Août à Novembre",
            is_premium=True
        )

        # Calendar Entries
        self.cal_semis_tomate = CalendarEntry.objects.create(
            vegetable=self.veg_tomate,
            action="semis",
            month=10,
            notes="Semis sous abri ou en pépinière ombragée."
        )
        self.cal_recolte_aubergine = CalendarEntry.objects.create(
            vegetable=self.veg_aubergine,
            action="recolte",
            month=3,
            notes="Récolte des premiers fruits bien formés."
        )

    def test_list_tools(self):
        url = reverse('tool_list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data.get('results', res.data)
        self.assertEqual(len(results), 2)

    def test_filter_tools_by_category(self):
        url = reverse('tool_list')
        res = self.client.get(url, {'category': 'semis'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data.get('results', res.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "Semoir de Précision")

    def test_list_plant_families(self):
        url = reverse('plantfamily_list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data.get('results', res.data)
        self.assertEqual(len(results), 2)
        # Vérifie l'ordre alphabétique : "Cucurbitacées" avant "Solanacées"
        self.assertEqual(results[0]['name'], "Cucurbitacées")
        self.assertEqual(results[1]['name'], "Solanacées")

    def test_list_vegetables_and_search(self):
        url = reverse('vegetable_list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data.get('results', res.data)
        self.assertEqual(len(results), 3)
        # Vérifie l'ordre alphabétique : Aubergine, Gombo, Tomate Cerise
        self.assertEqual(results[0]['name'], "Aubergine Africaine (Diakhatou)")
        self.assertEqual(results[1]['name'], "Gombo Tropical")
        self.assertEqual(results[2]['name'], "Tomate Cerise Tropicale")

        # Test de recherche
        res_search = self.client.get(url, {'search': 'Diakhatou'})
        self.assertEqual(res_search.status_code, status.HTTP_200_OK)
        results_search = res_search.data.get('results', res_search.data)
        self.assertEqual(len(results_search), 1)
        self.assertEqual(results_search[0]['id'], self.veg_aubergine.id)

    def test_filter_vegetables_by_family(self):
        url = reverse('vegetable_list')
        res = self.client.get(url, {'family': self.family_solanacees.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data.get('results', res.data)
        self.assertEqual(len(results), 2)
        # Vérifie l'ordre alphabétique dans la famille Solanacées : Aubergine avant Tomate
        self.assertEqual(results[0]['name'], "Aubergine Africaine (Diakhatou)")
        self.assertEqual(results[1]['name'], "Tomate Cerise Tropicale")

    def test_list_calendar_entries(self):
        url = reverse('calendar_entry_list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data.get('results', res.data)
        self.assertEqual(len(results), 2)

        # Filtre par action 'semis' et mois 10 (Octobre)
        res_semis = self.client.get(url, {'action': 'semis', 'month': 10})
        self.assertEqual(res_semis.status_code, status.HTTP_200_OK)
        results_semis = res_semis.data.get('results', res_semis.data)
        self.assertEqual(len(results_semis), 1)
        self.assertEqual(results_semis[0]['vegetable_name'], "Tomate Cerise Tropicale")
        self.assertEqual(results_semis[0]['month'], 10)

    def test_tool_detail_locked_for_unsubscribed(self):
        url = reverse('tool_detail', kwargs={'pk': self.tool2.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data.get('is_locked'))
        self.assertIn("Contenu réservé", res.data['usage_tips'])

    def test_tool_detail_unlocked_for_subscribed(self):
        from django.contrib.auth import get_user_model
        from django.utils import timezone
        from datetime import timedelta
        User = get_user_model()
        user = User.objects.create_user(email='prem_tool@test.com', username='prem_tool', password='password123')
        user.profile.subscription_active = True
        user.profile.subscription_end_date = timezone.now() + timedelta(days=30)
        user.profile.save()
        self.client.force_authenticate(user=user)

        url = reverse('tool_detail', kwargs={'pk': self.tool2.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data.get('is_locked'))

