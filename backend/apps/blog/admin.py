from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Post, PostImage, Comment

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

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'is_premium', 'is_published', 'views_count', 'created_at', 'cover_image_preview')
    list_filter = ('is_premium', 'is_published', 'category', 'created_at')
    list_editable = ('is_premium', 'is_published')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PostImageInline, CommentInline]
    readonly_fields = ('cover_image_preview', 'views_count', 'created_at', 'updated_at')

    def cover_image_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height: 80px; max-width: 120px; border-radius: 4px;" />', obj.cover_image.url)
        return "Pas d'image"
    cover_image_preview.short_description = "Image de couverture"

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'author', 'is_premium', 'is_published')
        }),
        ('Média & Aperçu', {
            'fields': ('cover_image', 'cover_image_preview')
        }),
        ('Contenu de l\'Article', {
            'fields': ('excerpt', 'content'),
            'description': (
                '<div style="background-color: #e8f5e9; border-left: 4px solid #2e7d32; padding: 12px; margin-bottom: 15px; border-radius: 4px;">'
                '<strong>💡 Astuce Rédaction & Images :</strong><br/>'
                '1. Ajoutez vos images dans la section <em>"Images d\'article"</em> ci-dessous puis sauvegardez l\'article.<br/>'
                '2. Copiez le code HTML généré dans la colonne <code>Code HTML à insérer</code>.<br/>'
                '3. Collez ce code dans le champ <strong>Contenu</strong> pour insérer l\'image directement à cet endroit dans le texte !'
                '</div>'
            )
        }),
        ('Statistiques & Dates', {
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
