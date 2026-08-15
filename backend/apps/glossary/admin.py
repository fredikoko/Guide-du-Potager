from django.contrib import admin
from .models import Tool, PlantFamily, Vegetable

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_premium')
    list_filter = ('category', 'is_premium')
    search_fields = ('name', 'description')

@admin.register(PlantFamily)
class PlantFamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_premium')
    search_fields = ('name', 'description')

@admin.register(Vegetable)
class VegetableAdmin(admin.ModelAdmin):
    list_display = ('name', 'family', 'scientific_name', 'is_premium')
    list_filter = ('family', 'is_premium')
    search_fields = ('name', 'scientific_name', 'care_tips')
