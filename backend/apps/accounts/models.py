from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

CLIMATE_ZONE_CHOICES = (
    ('sahelien', 'Zone Sahélienne (aride, harmattan, saison sèche longue)'),
    ('soudano_sahelien', 'Zone Soudano-Sahélienne (semi-aride)'),
    ('tropical_humide', 'Zone Tropicale Humide / Côtière'),
    ('equatorial', 'Zone Équatoriale / Forêt (forte humidité permanente)'),
    ('insulaire', 'Zone Insulaire Tropicale (Caraïbes / Océan Indien)'),
)

GARDEN_TYPE_CHOICES = (
    ('potager_sol', 'Potager maraîcher en pleine terre'),
    ('hors_sol_bacs', 'Cultures hors-sol / Bacs & Tables maraîchères'),
    ('micro_jardin', 'Micro-jardin urbain / Cour intérieure'),
    ('perirubain', 'Exploitation agro-écologique périurbaine'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    subscription_active = models.BooleanField(default=False)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True, default="Sénégal", verbose_name="Pays / Territoire")
    climate_zone = models.CharField(max_length=50, choices=CLIMATE_ZONE_CHOICES, default='sahelien', verbose_name="Zone agro-climatique")
    garden_type = models.CharField(max_length=50, choices=GARDEN_TYPE_CHOICES, default='potager_sol', verbose_name="Type de potager")
    preferences = models.JSONField(default=dict, blank=True)
    history = models.JSONField(default=list, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Profile of {self.user.email} ({self.get_climate_zone_display()})"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()

VERIFICATION_PURPOSE_CHOICES = (
    ('registration', 'Confirmation d\'inscription'),
    ('email_change', 'Changement d\'adresse email'),
)

class EmailVerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='verification_codes')
    email = models.EmailField(db_index=True, verbose_name="Adresse email destinataire")
    code = models.CharField(max_length=6, verbose_name="Code à 6 chiffres")
    purpose = models.CharField(max_length=25, choices=VERIFICATION_PURPOSE_CHOICES, default='registration')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'purpose', 'is_used']),
        ]

    def __str__(self):
        return f"Code {self.code} ({self.purpose}) pour {self.email}"

