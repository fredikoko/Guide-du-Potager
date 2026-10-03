from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Catégorie de blog"
        verbose_name_plural = "Catégories de blog"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class PostQuerySet(models.QuerySet):
    def published(self):
        """Articles actifs dont l'échéance de publication est atteinte."""
        return self.filter(
            is_published=True,
            published_at__lte=timezone.now()
        )

    def scheduled(self):
        """Articles planifiés pour une publication future."""
        return self.filter(
            is_published=True,
            published_at__gt=timezone.now()
        )

    def drafts(self):
        """Articles en brouillon."""
        return self.filter(is_published=False)

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='blog_posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    excerpt = models.TextField(help_text="Extrait court affiché dans la liste des articles")
    content = models.TextField(help_text="Contenu de l'article (supporte simultanément Markdown, HTML riche et Texte brut)")
    cover_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    is_premium = models.BooleanField(default=False, help_text="Définir si cet article est réservé aux abonnés Premium")
    is_published = models.BooleanField(default=True, verbose_name="Publier l'article", help_text="Décocher pour conserver sous forme de brouillon.")
    published_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Date et heure de publication",
        help_text="Date et heure de publication. Si fixée dans le futur, l'article sera automatiquement planifié et restera invisible au public jusqu'à cette échéance."
    )
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        verbose_name = "Article de blog"
        verbose_name_plural = "Articles de blog"
        ordering = ['-published_at', '-created_at']

    @property
    def is_scheduled(self):
        """Indique si l'article est planifié pour une parution future."""
        return bool(self.is_published and self.published_at and self.published_at > timezone.now())

    @property
    def is_visible(self):
        """Indique si l'article est visible par le grand public."""
        return bool(self.is_published and self.published_at and self.published_at <= timezone.now())

    @property
    def publication_status(self):
        if not self.is_published:
            return "draft"
        if self.is_scheduled:
            return "scheduled"
        return "published"

    @property
    def rendered_content(self):
        from apps.content.rendering import render_content
        return render_content(self.content)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='blog/images/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Image d'article"
        verbose_name_plural = "Images d'article"
        ordering = ['order']

    def __str__(self):
        return f"Image pour {self.post.title} ({self.caption or self.id})"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_comments')
    content = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ['-created_at']

    def __str__(self):
        return f"Commentaire de {self.author.username} sur {self.post.title}"

class PostFAQ(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=300, verbose_name="Question")
    answer = models.TextField(verbose_name="Réponse")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Question / Réponse (FAQ)"
        verbose_name_plural = "Foire Aux Questions (FAQ)"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.question[:60]} ({self.post.title})"
