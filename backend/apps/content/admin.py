from django.contrib import admin
from django.utils.html import format_html
from .models import Part, Chapter, ChapterImage, AboutPage

class ChapterImageInline(admin.TabularInline):
    model = ChapterImage
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
            snippet = f'<img src="{obj.image.url}" alt="{obj.caption or obj.chapter.title}" style="max-width:100%; height:auto;" />'
            return format_html('<code style="background:#f4f4f4; padding:4px 8px; border-radius:3px; display:inline-block; font-size:11px;">{}</code>', snippet)
        return "Enregistrez d'abord l'image"
    html_snippet.short_description = "Code HTML à insérer dans le contenu"

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'is_premium', 'icon')
    list_editable = ('title', 'is_premium', 'icon')
    ordering = ('order',)

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'part', 'is_premium')
    list_filter = ('part', 'is_premium')
    search_fields = ('title', 'content')
    inlines = [ChapterImageInline]
    ordering = ('part', 'order')
    fieldsets = (
        (None, {
            'fields': ('part', 'title', 'order', 'is_premium')
        }),
        ('Contenu du Chapitre', {
            'fields': ('content',),
            'description': (
                '<div style="background-color: #e8f5e9; border-left: 4px solid #2e7d32; padding: 12px; margin-bottom: 15px; border-radius: 4px;">'
                '<strong>💡 Astuce Rédaction & Formatage Universel :</strong><br/>'
                'Ce champ supporte simultanément le <strong>Markdown (.md)</strong>, le <strong>HTML riche</strong> et le <strong>Texte brut</strong>.<br/>'
                '• <em>Markdown :</em> <code>## Titre</code>, <code>**Gras**</code>, <code>*Italique*</code>, <code>- Puce</code>, <code>1. Numéro</code>, <code>[Lien](url)</code>, <code>![Légende](url)</code>, <code>| Tableaux |</code>, <code>&gt; Citation</code>.<br/>'
                '• <em>HTML :</em> <code>&lt;h2&gt;</code>, <code>&lt;strong&gt;</code>, <code>&lt;ul&gt;&lt;li&gt;</code>, <code>&lt;img src="..."&gt;</code>, <code>&lt;div class="..."&gt;</code>.<br/>'
                '• <em>Images associées :</em> Ajoutez vos images ci-dessous, puis insérez le code HTML généré ou la syntaxe Markdown <code>![Légende](/media/...)</code> où vous le souhaitez dans le texte !'
                '</div>'
            )
        }),
    )

@admin.register(ChapterImage)
class ChapterImageAdmin(admin.ModelAdmin):
    list_display = ('chapter', 'image_preview', 'caption', 'order', 'html_snippet')
    readonly_fields = ('image_preview', 'html_snippet')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 150px; border-radius: 4px;" />', obj.image.url)
        return "Pas d'image"
    image_preview.short_description = "Aperçu"

    def html_snippet(self, obj):
        if obj.image:
            snippet = f'<img src="{obj.image.url}" alt="{obj.caption or obj.chapter.title}" style="max-width:100%; height:auto;" />'
            return format_html('<code style="background:#f4f4f4; padding:4px 8px; border-radius:3px;">{}</code>', snippet)
        return "N/A"
    html_snippet.short_description = "Code HTML d'insertion"


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'contact_email', 'contact_phone', 'app_version', 'updated_at')
    fieldsets = (
        ("En-tête de l'Application", {
            'fields': ('title', 'subtitle', 'app_version'),
            'description': 'Informations générales visibles en haut des pages À Propos (Web & Mobile).'
        }),
        ("Présentation & Mission Agro-écologique", {
            'fields': ('mission_title', 'mission_text'),
            'description': (
                '<div style="background-color: #e8f5e9; border-left: 4px solid #2e7d32; padding: 10px; border-radius: 4px;">'
                '💡 Vous pouvez rédiger du texte brut ou inclure des balises HTML (ex: <code>&lt;strong&gt;</code>, <code>&lt;p&gt;</code>, listes).'
                '</div>'
            )
        }),
        ("Trois Piliers Maraîchers (Conventionnel & Agro-écologique)", {
            'fields': (
                ('pillar_1_title', 'pillar_1_desc'),
                ('pillar_2_title', 'pillar_2_desc'),
                ('pillar_3_title', 'pillar_3_desc'),
            ),
            'description': 'Les 3 piliers de la méthode (Irrigation de précision, Nutrition des sols & rendements, Protection raisonnée & biocontrôle).'
        }),
        ("Assistance, Contact & Communauté", {
            'fields': ('contact_title', 'contact_text', 'contact_email', 'contact_phone'),
            'description': 'Coordonnées de support pour les maraîchers (email et numéro WhatsApp).'
        }),
    )

    def has_add_permission(self, request):
        # Un seul enregistrement singleton pour la page À Propos
        if AboutPage.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

