from rest_framework import serializers
from .models import Disease, Insect
from apps.glossary.serializers import VegetableSerializer

class DiseaseSerializer(serializers.ModelSerializer):
    affected_vegetables_details = VegetableSerializer(source='affected_vegetables', many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Disease
        fields = [
            'id', 'name', 'symptoms', 'treatment', 'prevention',
            'favorable_season', 'tropical_organic_treatment',
            'affected_vegetables', 'affected_vegetables_details', 'image', 'is_premium'
        ]

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class InsectSerializer(serializers.ModelSerializer):
    affected_vegetables_details = VegetableSerializer(source='affected_vegetables', many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Insect
        fields = [
            'id', 'name', 'description', 'damage', 'solution',
            'favorable_season', 'tropical_bio_control', 'prevention_tips',
            'affected_vegetables', 'affected_vegetables_details', 'image', 'is_premium'
        ]

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
