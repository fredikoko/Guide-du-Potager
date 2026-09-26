from rest_framework import serializers
from .models import Tool, PlantFamily, Vegetable, CalendarEntry

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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        user = request.user if request else None
        has_access = not instance.is_premium or (user and user.is_authenticated and hasattr(user, 'profile') and user.profile.is_premium)
        if not has_access:
            data['is_locked'] = True
            data['usage_tips'] = "🔒 Contenu réservé : Abonnez-vous pour débloquer les conseils d'utilisation."
            data['tropical_tips'] = "🔒 Contenu réservé : Abonnez-vous pour accéder aux astuces en climat tropical."
        else:
            data['is_locked'] = False
        return data

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

class CalendarEntrySerializer(serializers.ModelSerializer):
    vegetable_id = serializers.IntegerField(source='vegetable.id', read_only=True)
    vegetable_name = serializers.CharField(source='vegetable.name', read_only=True)
    scientific_name = serializers.CharField(source='vegetable.scientific_name', read_only=True)
    family_name = serializers.CharField(source='vegetable.family.name', read_only=True)
    vegetable_image = serializers.SerializerMethodField()
    sowing_period = serializers.CharField(source='vegetable.sowing_period', read_only=True)
    harvest_period = serializers.CharField(source='vegetable.harvest_period', read_only=True)
    care_tips = serializers.CharField(source='vegetable.care_tips', read_only=True)
    tropical_season_display = serializers.CharField(source='vegetable.get_tropical_season_display', read_only=True)
    cycle_duration_days = serializers.IntegerField(source='vegetable.cycle_duration_days', read_only=True)
    is_premium = serializers.BooleanField(source='vegetable.is_premium', read_only=True)
    month_display = serializers.CharField(source='get_month_display', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = CalendarEntry
        fields = [
            'id', 'vegetable_id', 'vegetable_name', 'scientific_name', 'family_name',
            'vegetable_image', 'action', 'action_display', 'month', 'month_display',
            'notes', 'sowing_period', 'harvest_period', 'care_tips',
            'tropical_season_display', 'cycle_duration_days', 'is_premium'
        ]

    def get_vegetable_image(self, obj):
        request = self.context.get('request')
        if obj.vegetable.image:
            if request:
                return request.build_absolute_uri(obj.vegetable.image.url)
            return obj.vegetable.image.url
        return None
