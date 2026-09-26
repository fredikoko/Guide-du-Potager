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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        user = request.user if request else None
        has_access = not instance.is_premium or (user and user.is_authenticated and hasattr(user, 'profile') and user.profile.is_premium)
        if not has_access:
            data['is_locked'] = True
            data['symptoms'] = "🔒 Contenu réservé : Abonnez-vous pour consulter les symptômes détaillés."
            data['treatment'] = "🔒 Contenu réservé : Abonnez-vous pour débloquer les traitements."
            data['prevention'] = "🔒 Contenu réservé : Abonnez-vous pour accéder aux conseils de prévention."
            data['tropical_organic_treatment'] = "🔒 Contenu réservé : Abonnez-vous pour accéder aux recettes de traitement bio tropical."
            data['favorable_season'] = "🔒 Contenu réservé"
        else:
            data['is_locked'] = False
        return data

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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        user = request.user if request else None
        has_access = not instance.is_premium or (user and user.is_authenticated and hasattr(user, 'profile') and user.profile.is_premium)
        if not has_access:
            data['is_locked'] = True
            data['description'] = "🔒 Contenu réservé : Abonnez-vous pour consulter la description complète."
            data['damage'] = "🔒 Contenu réservé : Abonnez-vous pour voir les dégâts constatés."
            data['solution'] = "🔒 Contenu réservé : Abonnez-vous pour accéder aux solutions bio et traitements."
            data['tropical_bio_control'] = "🔒 Contenu réservé : Abonnez-vous pour débloquer les méthodes de biocontrôle."
            data['prevention_tips'] = "🔒 Contenu réservé : Abonnez-vous pour accéder aux conseils de prévention."
            data['favorable_season'] = "🔒 Contenu réservé"
        else:
            data['is_locked'] = False
        return data
