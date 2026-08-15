from rest_framework import serializers
from .models import Disease, Insect
from apps.glossary.serializers import VegetableSerializer

class DiseaseSerializer(serializers.ModelSerializer):
    affected_vegetables_details = VegetableSerializer(source='affected_vegetables', many=True, read_only=True)

    class Meta:
        model = Disease
        fields = [
            'id', 'name', 'symptoms', 'treatment', 'prevention',
            'affected_vegetables', 'affected_vegetables_details', 'image', 'is_premium'
        ]

class InsectSerializer(serializers.ModelSerializer):
    affected_vegetables_details = VegetableSerializer(source='affected_vegetables', many=True, read_only=True)

    class Meta:
        model = Insect
        fields = [
            'id', 'name', 'description', 'damage', 'solution',
            'affected_vegetables', 'affected_vegetables_details', 'image', 'is_premium'
        ]
