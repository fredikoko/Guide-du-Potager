from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.glossary.models import Tool, PlantFamily, Vegetable

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
