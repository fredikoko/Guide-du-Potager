from django.contrib import admin
from django.utils.html import format_html
from .models import Part, Chapter, ChapterImage

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
    list_display = ('order', 'title', 'part', 'is_premium', 'estimated_reading_time')
    list_filter = ('part', 'is_premium')
    search_fields = ('title', 'content')
    inlines = [ChapterImageInline]
    ordering = ('part', 'order')
    fieldsets = (
        (None, {
            'fields': ('part', 'title', 'order', 'is_premium', 'estimated_reading_time')
        }),
        ('Contenu du Chapitre', {
            'fields': ('content',),
            'description': (
                '<div style="background-color: #e8f5e9; border-left: 4px solid #2e7d32; padding: 12px; margin-bottom: 15px; border-radius: 4px;">'
                '<strong>💡 Astuce Administrateur - Insertion d\'images dans le texte :</strong><br/>'
                '1. Ajoutez vos images dans la section <em>"Images associées"</em> ci-dessous puis sauvegardez.<br/>'
                '2. Copiez le code HTML généré dans la colonne <code>Code HTML à insérer</code>.<br/>'
                '3. Collez ce code n\'importe où dans le champ <strong>Contenu</strong> ci-dessus pour afficher l\'image directement à cet endroit dans le texte !'
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
