from rest_framework import serializers
from .models import Part, Chapter, ChapterImage

class ChapterImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChapterImage
        fields = ['id', 'image', 'caption', 'order']

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
