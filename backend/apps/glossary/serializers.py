from rest_framework import serializers
from .models import Tool, PlantFamily, Vegetable

class ToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = ['id', 'name', 'description', 'usage_tips', 'image', 'category', 'is_premium']

class VegetableSerializer(serializers.ModelSerializer):
    family_name = serializers.CharField(source='family.name', read_only=True)

    class Meta:
        model = Vegetable
        fields = [
            'id', 'name', 'family', 'family_name', 'scientific_name',
            'sowing_period', 'harvest_period', 'care_tips', 'image', 'is_premium'
        ]

class PlantFamilySerializer(serializers.ModelSerializer):
    vegetables = VegetableSerializer(many=True, read_only=True)

    class Meta:
        model = PlantFamily
        fields = ['id', 'name', 'description', 'characteristics', 'image', 'is_premium', 'vegetables']
