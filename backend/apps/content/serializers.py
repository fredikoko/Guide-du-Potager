from rest_framework import serializers
from .models import Part, Chapter, ChapterImage, AboutPage

class ChapterImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ChapterImage
        fields = ['id', 'image', 'caption', 'order']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class ChapterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'part', 'title', 'order', 'is_premium', 'estimated_reading_time']

class ChapterDetailSerializer(serializers.ModelSerializer):
    images = ChapterImageSerializer(many=True, read_only=True)
    rendered_content = serializers.CharField(read_only=True)
    is_locked = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = [
            'id', 'part', 'title', 'content', 'rendered_content', 'order',
            'is_premium', 'estimated_reading_time', 'images', 'is_locked',
            'created_at', 'updated_at'
        ]

    def get_is_locked(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        is_premium_content = bool(obj.is_premium or (obj.part and obj.part.is_premium))
        if not is_premium_content:
            return False
        if user and user.is_authenticated and hasattr(user, 'profile') and user.profile.is_premium:
            return False
        return True

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get('is_locked'):
            lock_msg = (
                f"<h1>🔒 {instance.title}</h1>"
                "<p>Ce chapitre est réservé aux abonnés du Guide du Potager Tropical.</p>"
                "<p>Abonnez-vous pour débloquer l'accès complet à tous les chapitres, outils avancés, et fiches maladies & insectes !</p>"
            )
            data['content'] = lock_msg
            data['rendered_content'] = lock_msg
            data['images'] = []
        return data

class PartSerializer(serializers.ModelSerializer):
    chapters = ChapterListSerializer(many=True, read_only=True)

    class Meta:
        model = Part
        fields = ['id', 'title', 'description', 'order', 'is_premium', 'icon', 'chapters']


class AboutPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutPage
        fields = [
            'id', 'title', 'subtitle', 'mission_title', 'mission_text',
            'pillar_1_title', 'pillar_1_desc',
            'pillar_2_title', 'pillar_2_desc',
            'pillar_3_title', 'pillar_3_desc',
            'contact_title', 'contact_text', 'contact_email', 'contact_phone',
            'app_version', 'updated_at'
        ]

