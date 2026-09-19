from rest_framework import serializers
from .models import Category, Post, PostImage, Comment

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']

class PostImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = PostImage
        fields = ['id', 'image', 'caption', 'order']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_name', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

class PostListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'category', 'category_name',
            'author_name', 'excerpt', 'cover_image', 'is_premium',
            'views_count', 'created_at'
        ]

    def get_cover_image(self, obj):
        request = self.context.get('request')
        if obj.cover_image:
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url
        return None

class PostDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    cover_image = serializers.SerializerMethodField()
    images = PostImageSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    is_locked = serializers.BooleanField(default=False, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'category', 'category_name',
            'author_name', 'excerpt', 'content', 'cover_image', 'images',
            'is_premium', 'is_locked', 'views_count', 'created_at', 'updated_at', 'comments'
        ]

    def get_cover_image(self, obj):
        request = self.context.get('request')
        if obj.cover_image:
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url
        return None
