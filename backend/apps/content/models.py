from django.db import models

class Part(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=1)
    is_premium = models.BooleanField(default=False)
    icon = models.CharField(max_length=50, blank=True, default='sprout')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Partie {self.order}: {self.title}"

class Chapter(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=200)
    content = models.TextField()  # HTML or Markdown content
    order = models.IntegerField(default=1)
    is_premium = models.BooleanField(default=False)
    estimated_reading_time = models.IntegerField(default=5)  # minutes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Chapitre {self.order}: {self.title}"

class ChapterImage(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='chapters/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.chapter.title} ({self.caption or self.id})"


class AboutPage(models.Model):
    title = models.CharField("Titre de l'application", max_length=200, default="Guide du Potager Tropical")
    subtitle = models.CharField(
        "Sous-titre / Slogan",
        max_length=300,
        default="Manuel de Maraîchage Tropical : Pratiques Conventionnelles & Agro-écologiques"
    )

    mission_title = models.CharField("Titre de la mission", max_length=200, default="Notre Mission & Approche Maraîchère")
    mission_text = models.TextField(
        "Texte de présentation & Mission",
        default=(
            "Le Guide du Potager Tropical accompagne les maraîchers urbains, périurbains et ruraux "
            "vers une production performante, rentable et résiliente face aux réalités climatiques tropicales.\n\n"
            "Nos articles et fiches techniques intègrent l'ensemble des approches agronomiques : "
            "les itinéraires techniques conventionnels (gestion raisonnée des engrais minéraux NPK, protection "
            "phytosanitaire homologuée et conduite intensive) ainsi que les méthodes agro-écologiques et biologiques "
            "(amendements organiques, biopesticides locaux au neem, santé des sols vivants et paillage protecteur). "
            "Chaque producteur y trouve les protocoles, les dosages rigoureux et les conseils pratiques adaptés "
            "à ses objectifs de rendement."
        ),
        help_text="Prend en charge le formatage texte ou HTML riche (<p>, <strong>, etc.)"
    )

    # 3 Piliers Maraîchers (Conventionnel & Agro-écologique)
    pillar_1_title = models.CharField("Pilier 1 - Titre", max_length=150, default="Gestion de l'Eau & Irrigation")
    pillar_1_desc = models.TextField(
        "Pilier 1 - Description",
        default="Goutte-à-goutte de précision, micro-aspersion, paillage protecteur et pilotage hydrique sous forte évapotranspiration."
    )

    pillar_2_title = models.CharField("Pilier 2 - Titre", max_length=150, default="Nutrition des Sols & Rendements")
    pillar_2_desc = models.TextField(
        "Pilier 2 - Description",
        default="Plans de fertilisation équilibrés combinant apports minéraux raisonnés (NPK, urée) et amendements organiques pour maximiser les récoltes."
    )

    pillar_3_title = models.CharField("Pilier 3 - Titre", max_length=150, default="Protection Raisonnée & Biocontrôle")
    pillar_3_desc = models.TextField(
        "Pilier 3 - Description",
        default="Stratégies de défense des cultures articulant traitements conventionnels homologués, barrières physiques et biopesticides locaux."
    )

    # Assistance, Contact & Version
    contact_title = models.CharField("Titre section contact", max_length=200, default="Assistance & Communauté")
    contact_text = models.TextField(
        "Texte section contact",
        default="Pour toute question agronomique, assistance technique sur vos abonnements ou partenariat d'exploitation, notre équipe est à votre écoute :"
    )
    contact_email = models.EmailField("Email support", default="contact@guidedupotager.com")
    contact_phone = models.CharField("Téléphone / WhatsApp", max_length=50, default="+221 77 000 00 00")

    app_version = models.CharField("Version de l'application", max_length=50, default="1.0.0")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Page À Propos & Mission"
        verbose_name_plural = "Page À Propos & Mission"

    def __str__(self):
        return f"{self.title} (v{self.app_version})"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

