from django.contrib import admin
from .models import Tool, PlantFamily, Vegetable, CalendarEntry

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_premium')
    list_filter = ('category', 'is_premium')
    search_fields = ('name', 'description')

@admin.register(PlantFamily)
class PlantFamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_premium')
    search_fields = ('name', 'description')

class CalendarEntryInline(admin.TabularInline):
    model = CalendarEntry
    extra = 1
    fields = ('action', 'month', 'notes', 'is_active')

@admin.register(Vegetable)
class VegetableAdmin(admin.ModelAdmin):
    list_display = ('name', 'family', 'scientific_name', 'is_premium')
    list_filter = ('family', 'is_premium', 'tropical_season')
    search_fields = ('name', 'scientific_name', 'care_tips')
    inlines = [CalendarEntryInline]

@admin.register(CalendarEntry)
class CalendarEntryAdmin(admin.ModelAdmin):
    list_display = ('vegetable', 'action', 'month_display', 'notes', 'is_active')
    list_editable = ('action', 'is_active')
    list_filter = ('action', 'month', 'is_active', 'vegetable__family')
    search_fields = ('vegetable__name', 'notes')
    autocomplete_fields = ['vegetable']

    def month_display(self, obj):
        return obj.get_month_display()
    month_display.short_description = "Mois"

