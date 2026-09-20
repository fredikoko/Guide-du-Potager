from django.db import models

TOOL_CATEGORIES = (
    ('travail_du_sol', 'Travail du Sol & Préparation des Planches'),
    ('semis_plantation', 'Semis & Pépinière Tropicale'),
    ('entretien_arrosage', 'Irrigation & Paillage Protecteur'),
    ('recolte', 'Récolte'),
    ('protection', 'Ombrières & Filets Anti-insectes'),
)

TROPICAL_SEASON_CHOICES = (
    ('toute_annee', 'Toute l\'année (avec irrigation)'),
    ('saison_seche_fraiche', 'Saison sèche fraîche (Octobre - Février)'),
    ('saison_seche_chaude', 'Saison sèche chaude (Mars - Mai)'),
    ('hivernage', 'Saison des pluies / Hivernage (Juin - Septembre)'),
)

HEAT_TOLERANCE_CHOICES = (
    ('faible', 'Faible (< 28°C, sensible à la chaleur)'),
    ('moyenne', 'Moyenne (28°C - 34°C)'),
    ('haute', 'Excellente (> 35°C, forte résistance sahélienne)'),
)

WATER_CHOICES = (
    ('faible', 'Faible (tolère les stress hydriques)'),
    ('modere', 'Modéré'),
    ('eleve', 'Élevé (arrosage régulier / paillage obligatoire)'),
)

SUN_EXPOSURE_CHOICES = (
    ('plein_soleil', 'Plein soleil tropical'),
    ('mi_ombre', 'Mi-ombre / Ombrière 30-50% conseillée'),
    ('ombre', 'Ombragé sous canopée'),
)

class Tool(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    usage_tips = models.TextField(blank=True)
    tropical_tips = models.TextField(blank=True, verbose_name="Astuces en climat tropical/sahélien")
    image = models.ImageField(upload_to='tools/', null=True, blank=True)
    category = models.CharField(max_length=50, choices=TOOL_CATEGORIES, default='travail_du_sol')
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class PlantFamily(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    characteristics = models.TextField(blank=True)
    image = models.ImageField(upload_to='families/', null=True, blank=True)
    is_premium = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Plant Families"

    def __str__(self):
        return self.name

class Vegetable(models.Model):
    name = models.CharField(max_length=100)
    family = models.ForeignKey(PlantFamily, on_delete=models.CASCADE, related_name='vegetables')
    scientific_name = models.CharField(max_length=200, blank=True)
    sowing_period = models.CharField(max_length=200, verbose_name="Période de semis")
    harvest_period = models.CharField(max_length=200, verbose_name="Période de récolte")
    care_tips = models.TextField(verbose_name="Conseils de culture & d'entretien")

    # Champs spécifiques au maraîchage tropical
    tropical_season = models.CharField(
        max_length=50,
        choices=TROPICAL_SEASON_CHOICES,
        default='toute_annee',
        verbose_name="Saison tropicale optimale"
    )
    heat_tolerance = models.CharField(
        max_length=30,
        choices=HEAT_TOLERANCE_CHOICES,
        default='moyenne',
        verbose_name="Tolérance thermique"
    )
    water_requirement = models.CharField(
        max_length=30,
        choices=WATER_CHOICES,
        default='modere',
        verbose_name="Besoins en eau / irrigation"
    )
    sun_exposure = models.CharField(
        max_length=30,
        choices=SUN_EXPOSURE_CHOICES,
        default='plein_soleil',
        verbose_name="Exposition au soleil tropical"
    )
    tropical_varieties = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Variétés tropicales adaptées",
        help_text="Ex: Mongal F1, Nadira F1, Clemson Spineless, Habanero..."
    )
    cycle_duration_days = models.PositiveIntegerField(
        default=90,
        verbose_name="Durée du cycle de culture (jours)"
    )

    image = models.ImageField(upload_to='vegetables/', null=True, blank=True)
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.name
