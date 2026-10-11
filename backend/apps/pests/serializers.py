from rest_framework import serializers
from .models import Disease, Insect
from apps.glossary.serializers import VegetableSerializer

class DiseaseSerializer(serializers.ModelSerializer):
    affected_vegetables_details = VegetableSerializer(source='affected_vegetables', many=True, read_only=True)
    image = serializers.SerializerMethodField()
    rendered_symptoms = serializers.CharField(read_only=True)
    rendered_treatment = serializers.CharField(read_only=True)
    rendered_prevention = serializers.CharField(read_only=True)
    rendered_tropical_organic_treatment = serializers.CharField(read_only=True)

    class Meta:
        model = Disease
        fields = [
            'id', 'name', 'symptoms', 'rendered_symptoms',
            'treatment', 'rendered_treatment',
            'prevention', 'rendered_prevention',
            'favorable_season', 'tropical_organic_treatment', 'rendered_tropical_organic_treatment',
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
            msg_sym = "🔒 Contenu réservé : Abonnez-vous pour consulter les symptômes détaillés."
            data['symptoms'] = msg_sym
            data['rendered_symptoms'] = f"<p>{msg_sym}</p>"
            msg_trt = "🔒 Contenu réservé : Abonnez-vous pour débloquer les traitements."
            data['treatment'] = msg_trt
            data['rendered_treatment'] = f"<p>{msg_trt}</p>"
            msg_prev = "🔒 Contenu réservé : Abonnez-vous pour accéder aux conseils de prévention."
            data['prevention'] = msg_prev
            data['rendered_prevention'] = f"<p>{msg_prev}</p>"
            msg_bio = "🔒 Contenu réservé : Abonnez-vous pour accéder aux recettes de traitement bio tropical."
            data['tropical_organic_treatment'] = msg_bio
            data['rendered_tropical_organic_treatment'] = f"<p>{msg_bio}</p>"
            data['favorable_season'] = "🔒 Contenu réservé"
        else:
            data['is_locked'] = False
        return data

class InsectSerializer(serializers.ModelSerializer):
    affected_vegetables_details = VegetableSerializer(source='affected_vegetables', many=True, read_only=True)
    image = serializers.SerializerMethodField()
    rendered_description = serializers.CharField(read_only=True)
    rendered_damage = serializers.CharField(read_only=True)
    rendered_solution = serializers.CharField(read_only=True)
    rendered_tropical_bio_control = serializers.CharField(read_only=True)
    rendered_prevention_tips = serializers.CharField(read_only=True)

    class Meta:
        model = Insect
        fields = [
            'id', 'name', 'description', 'rendered_description',
            'damage', 'rendered_damage',
            'solution', 'rendered_solution',
            'favorable_season', 'tropical_bio_control', 'rendered_tropical_bio_control',
            'prevention_tips', 'rendered_prevention_tips',
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
            msg_desc = "🔒 Contenu réservé : Abonnez-vous pour consulter la description complète."
            data['description'] = msg_desc
            data['rendered_description'] = f"<p>{msg_desc}</p>"
            msg_dmg = "🔒 Contenu réservé : Abonnez-vous pour voir les dégâts constatés."
            data['damage'] = msg_dmg
            data['rendered_damage'] = f"<p>{msg_dmg}</p>"
            msg_sol = "🔒 Contenu réservé : Abonnez-vous pour accéder aux solutions bio et traitements."
            data['solution'] = msg_sol
            data['rendered_solution'] = f"<p>{msg_sol}</p>"
            msg_bio = "🔒 Contenu réservé : Abonnez-vous pour débloquer les méthodes de biocontrôle."
            data['tropical_bio_control'] = msg_bio
            data['rendered_tropical_bio_control'] = f"<p>{msg_bio}</p>"
            msg_prev = "🔒 Contenu réservé : Abonnez-vous pour accéder aux conseils de prévention."
            data['prevention_tips'] = msg_prev
            data['rendered_prevention_tips'] = f"<p>{msg_prev}</p>"
            data['favorable_season'] = "🔒 Contenu réservé"
        else:
            data['is_locked'] = False
        return data
