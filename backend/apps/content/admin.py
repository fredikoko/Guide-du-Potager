from django.contrib import admin
from .models import Part, Chapter, ChapterImage

class ChapterImageInline(admin.TabularInline):
    model = ChapterImage
    extra = 1

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

@admin.register(ChapterImage)
class ChapterImageAdmin(admin.ModelAdmin):
    list_display = ('chapter', 'caption', 'order')
