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

    class Meta:
        model = Chapter
        fields = ['id', 'part', 'title', 'content', 'order', 'is_premium', 'estimated_reading_time', 'images', 'created_at', 'updated_at']

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

