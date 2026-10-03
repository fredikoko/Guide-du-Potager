from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Post, PostImage, Comment, PostFAQ

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    readonly_fields = ('image_preview', 'html_snippet')
    fields = ('image', 'image_preview', 'caption', 'order', 'html_snippet')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 80px; max-width: 120px; border-radius: 4px;" />', obj.image.url)
        return "Pas d'image"
    image_preview.short_description = "Aperçu"

    def html_snippet(self, obj):
        if obj.image:
            snippet = f'<img src="{obj.image.url}" alt="{obj.caption or obj.post.title}" style="max-width:100%; height:auto;" />'
            return format_html('<code style="background:#f4f4f4; padding:4px 8px; border-radius:3px; display:inline-block; font-size:11px;">{}</code>', snippet)
        return "Enregistrez d'abord l'image"
    html_snippet.short_description = "Code HTML à insérer dans le texte"

class PostFAQInline(admin.StackedInline):
    model = PostFAQ
    extra = 0
    fields = ('question', 'answer', 'order')
    classes = ('collapse',)

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('created_at',)

class PublicationStatusFilter(admin.SimpleListFilter):
    title = "Statut de publication"
    parameter_name = "pub_status"

    def lookups(self, request, model_admin):
        return (
            ('published', '🟢 En ligne (Actifs)'),
            ('scheduled', '🕒 Planifiés (Futurs)'),
            ('draft', '⚪ Brouillons'),
        )

    def queryset(self, request, queryset):
        from django.utils import timezone
        val = self.value()
        if val == 'published':
            return queryset.filter(is_published=True, published_at__lte=timezone.now())
        elif val == 'scheduled':
            return queryset.filter(is_published=True, published_at__gt=timezone.now())
        elif val == 'draft':
            return queryset.filter(is_published=False)
        return queryset

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status_badge', 'published_at', 'is_premium', 'author', 'views_count', 'cover_image_preview')
    list_filter = (PublicationStatusFilter, 'is_premium', 'category', 'published_at')
    date_hierarchy = 'published_at'
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PostImageInline, PostFAQInline, CommentInline]
    readonly_fields = ('cover_image_preview', 'views_count', 'created_at', 'updated_at')
    actions = ['publish_now', 'unpublish_draft']

    def status_badge(self, obj):
        from django.utils import timezone
        if not obj.is_published:
            return format_html(
                '<span style="background-color: #64748b; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">'
                '⚪ Brouillon</span>'
            )
        elif obj.published_at and obj.published_at > timezone.now():
            return format_html(
                '<span style="background-color: #0284c7; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;" title="Date prévue : {}">'
                '🕒 Planifié ({})</span>',
                obj.published_at.strftime('%d/%m/%Y à %H:%M'),
                obj.published_at.strftime('%d/%m %H:%M')
            )
        else:
            return format_html(
                '<span style="background-color: #16a34a; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">'
                '🟢 En ligne</span>'
            )
    status_badge.short_description = "Statut"

    def cover_image_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height: 80px; max-width: 120px; border-radius: 4px;" />', obj.cover_image.url)
        return "Pas d'image"
    cover_image_preview.short_description = "Image de couverture"

    @admin.action(description="🚀 Publier immédiatement les articles sélectionnés")
    def publish_now(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_published=True, published_at=timezone.now())
        self.message_user(request, f"{updated} article(s) publié(s) immédiatement avec succès.")

    @admin.action(description="📁 Passer en brouillon les articles sélectionnés")
    def unpublish_draft(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"{updated} article(s) basculé(s) en brouillon.")

    fieldsets = (
        ('Informations Générales', {
            'fields': ('title', 'slug', 'category', 'author')
        }),
        ('Paramètres & Calendrier de Publication', {
            'fields': ('is_published', 'published_at', 'is_premium'),
            'description': (
                '<div style="background-color: #e0f2fe; border-left: 4px solid #0284c7; padding: 12px; margin-bottom: 12px; border-radius: 4px;">'
                '<strong>📅 Planification automatique de la publication :</strong><br/>'
                '• <strong>Publication immédiate :</strong> Laissez "Publier l\'article" coché et la date actuelle.<br/>'
                '• <strong>Publication programmée / différée :</strong> Choisissez une date et heure future. '
                'L\'article restera invisible aux visiteurs jusqu\'à cette échéance, puis s\'activera automatiquement en ligne !<br/>'
                '• <strong>Brouillon :</strong> Décochez "Publier l\'article" pour le masquer complètement.'
                '</div>'
            )
        }),
        ('Média & Aperçu', {
            'fields': ('cover_image', 'cover_image_preview')
        }),
        ('Contenu de l\'Article', {
            'fields': ('excerpt', 'content'),
            'description': (
                '<div style="background-color: #e8f5e9; border-left: 4px solid #2e7d32; padding: 12px; margin-bottom: 15px; border-radius: 4px;">'
                '<strong>💡 Astuce Rédaction & Formatage Universel :</strong><br/>'
                'Ce champ supporte simultanément le <strong>Markdown (.md)</strong>, le <strong>HTML riche</strong> et le <strong>Texte brut</strong>.<br/>'
                '• <em>Markdown :</em> <code>## Titre</code>, <code>**Gras**</code>, <code>*Italique*</code>, <code>- Puce</code>, <code>1. Numéro</code>, <code>[Lien](url)</code>, <code>![Légende](url)</code>, <code>| Tableaux |</code>, <code>&gt; Citation</code>.<br/>'
                '• <em>HTML :</em> <code>&lt;h2&gt;</code>, <code>&lt;strong&gt;</code>, <code>&lt;ul&gt;&lt;li&gt;</code>, <code>&lt;img src="..."&gt;</code>, <code>&lt;div class="..."&gt;</code>.<br/>'
                '• <em>Images d\'article :</em> Ajoutez vos images ci-dessous, puis insérez le code HTML généré ou la syntaxe Markdown <code>![Légende](/media/...)</code> où vous le souhaitez dans le texte !'
                '</div>'
            )
        }),
        ('Statistiques & Traçabilité', {
            'fields': ('views_count', 'created_at', 'updated_at')
        }),
    )

@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ('post', 'image_preview', 'caption', 'order', 'html_snippet')
    readonly_fields = ('image_preview', 'html_snippet')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 150px; border-radius: 4px;" />', obj.image.url)
        return "Pas d'image"
    image_preview.short_description = "Aperçu"

    def html_snippet(self, obj):
        if obj.image:
            snippet = f'<img src="{obj.image.url}" alt="{obj.caption or obj.post.title}" style="max-width:100%; height:auto;" />'
            return format_html('<code style="background:#f4f4f4; padding:4px 8px; border-radius:3px;">{}</code>', snippet)
        return "N/A"
    html_snippet.short_description = "Code HTML d'insertion"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('content', 'author__username', 'post__title')

@admin.register(PostFAQ)
class PostFAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'post', 'order', 'created_at')
    list_filter = ('post',)
    search_fields = ('question', 'answer', 'post__title')
    ordering = ('post', 'order')
