from django.db import models
from apps.glossary.models import Vegetable

class Disease(models.Model):
    name = models.CharField(max_length=200)
    symptoms = models.TextField(verbose_name="Symptômes observés")
    treatment = models.TextField(verbose_name="Traitement général")
    prevention = models.TextField(verbose_name="Mesures préventives")

    # Adaptations tropicales
    favorable_season = models.CharField(
        max_length=150,
        blank=True,
        default="Saison des pluies / Forte hygrométrie",
        verbose_name="Période tropicale à haut risque"
    )
    tropical_organic_treatment = models.TextField(
        blank=True,
        verbose_name="Recettes & Traitements bio tropicaux",
        help_text="Ex: macération de feuilles de neem, cendre de bois tamisée, purin de moringa..."
    )

    affected_vegetables = models.ManyToManyField(Vegetable, related_name='diseases', blank=True)
    image = models.ImageField(upload_to='diseases/', null=True, blank=True)
    is_premium = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Insect(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(verbose_name="Description du ravageur")
    damage = models.TextField(verbose_name="Dégâts causés aux cultures")
    solution = models.TextField(verbose_name="Solutions curatives")

    # Adaptations tropicales
    favorable_season = models.CharField(
        max_length=150,
        blank=True,
        default="Saison sèche chaude & périodes de transition",
        verbose_name="Saison de forte pullulation"
    )
    tropical_bio_control = models.TextField(
        blank=True,
        verbose_name="Biocontrôle & Répulsifs naturels locaux",
        help_text="Ex: macération piment-ail-savon noir, huile de neem pressée à froid..."
    )
    prevention_tips = models.TextField(
        blank=True,
        verbose_name="Prévention physique & agro-écologique",
        help_text="Ex: toiles moustiquaires/anti-insectes 50 mesh, cultures pièges..."
    )

    affected_vegetables = models.ManyToManyField(Vegetable, related_name='insects', blank=True)
    image = models.ImageField(upload_to='insects/', null=True, blank=True)
    is_premium = models.BooleanField(default=True)

    def __str__(self):
        return self.name
