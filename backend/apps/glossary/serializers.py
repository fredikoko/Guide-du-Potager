from rest_framework import serializers
from .models import Tool, PlantFamily, Vegetable

class ToolSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Tool
        fields = [
            'id', 'name', 'description', 'usage_tips', 'tropical_tips',
            'image', 'category', 'category_display', 'is_premium'
        ]

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class VegetableSerializer(serializers.ModelSerializer):
    family_name = serializers.CharField(source='family.name', read_only=True)
    image = serializers.SerializerMethodField()
    tropical_season_display = serializers.CharField(source='get_tropical_season_display', read_only=True)
    heat_tolerance_display = serializers.CharField(source='get_heat_tolerance_display', read_only=True)
    water_requirement_display = serializers.CharField(source='get_water_requirement_display', read_only=True)
    sun_exposure_display = serializers.CharField(source='get_sun_exposure_display', read_only=True)

    class Meta:
        model = Vegetable
        fields = [
            'id', 'name', 'family', 'family_name', 'scientific_name',
            'sowing_period', 'harvest_period', 'care_tips',
            'tropical_season', 'tropical_season_display',
            'heat_tolerance', 'heat_tolerance_display',
            'water_requirement', 'water_requirement_display',
            'sun_exposure', 'sun_exposure_display',
            'tropical_varieties', 'cycle_duration_days',
            'image', 'is_premium'
        ]

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class PlantFamilySerializer(serializers.ModelSerializer):
    vegetables = VegetableSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = PlantFamily
        fields = ['id', 'name', 'description', 'characteristics', 'image', 'is_premium', 'vegetables']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
