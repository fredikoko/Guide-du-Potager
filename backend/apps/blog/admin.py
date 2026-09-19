from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Post, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'is_published', 'views_count', 'created_at', 'cover_image_preview')
    list_filter = ('is_published', 'category', 'created_at')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CommentInline]
    readonly_fields = ('cover_image_preview', 'views_count', 'created_at', 'updated_at')

    def cover_image_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height: 80px; max-width: 120px; border-radius: 4px;" />', obj.cover_image.url)
        return "Pas d'image"
    cover_image_preview.short_description = "Image de couverture"

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'author', 'is_published')
        }),
        ('Média & Aperçu', {
            'fields': ('cover_image', 'cover_image_preview')
        }),
        ('Contenu de l\'Article', {
            'fields': ('excerpt', 'content'),
            'description': (
                '<div style="background-color: #e8f5e9; border-left: 4px solid #2e7d32; padding: 12px; margin-bottom: 15px; border-radius: 4px;">'
                '<strong>💡 Astuce Rédaction :</strong><br/>'
                'Utilisez des balises HTML standard (<code>&lt;p&gt;</code>, <code>&lt;h2&gt;</code>, <code>&lt;b&gt;</code>, <code>&lt;img src="..."/&gt;</code>) pour formater votre article. '
                'Les images insérées s\'afficheront de manière fluide dans l\'application mobile.'
                '</div>'
            )
        }),
        ('Statistiques & Dates', {
            'fields': ('views_count', 'created_at', 'updated_at')
        }),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('content', 'author__username', 'post__title')
