from django.contrib import admin
from .models import Disease, Insect

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_premium')
    list_filter = ('is_premium',)
    search_fields = ('name', 'symptoms', 'treatment', 'prevention')

@admin.register(Insect)
class InsectAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_premium')
    list_filter = ('is_premium',)
    search_fields = ('name', 'description', 'damage', 'solution')
