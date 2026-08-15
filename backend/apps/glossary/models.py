from django.db import models

TOOL_CATEGORIES = (
    ('travail_du_sol', 'Travail du Sol'),
    ('semis_plantation', 'Semis & Plantation'),
    ('entretien_arrosage', 'Entretien & Arrosage'),
    ('recolte', 'Récolte'),
    ('protection', 'Protection & Serre'),
)

class Tool(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    usage_tips = models.TextField(blank=True)
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
    sowing_period = models.CharField(max_length=200)
    harvest_period = models.CharField(max_length=200)
    care_tips = models.TextField()
    image = models.ImageField(upload_to='vegetables/', null=True, blank=True)
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.name
