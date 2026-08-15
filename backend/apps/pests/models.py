from django.db import models
from apps.glossary.models import Vegetable

class Disease(models.Model):
    name = models.CharField(max_length=200)
    symptoms = models.TextField()
    treatment = models.TextField()
    prevention = models.TextField()
    affected_vegetables = models.ManyToManyField(Vegetable, related_name='diseases', blank=True)
    image = models.ImageField(upload_to='diseases/', null=True, blank=True)
    is_premium = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Insect(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    damage = models.TextField()
    solution = models.TextField()  # Lutte biologique ou chimique
    affected_vegetables = models.ManyToManyField(Vegetable, related_name='insects', blank=True)
    image = models.ImageField(upload_to='insects/', null=True, blank=True)
    is_premium = models.BooleanField(default=True)

    def __str__(self):
        return self.name
