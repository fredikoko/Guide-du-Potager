from rest_framework import serializers
from .models import Category, Post, PostImage, Comment, PostFAQ

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']

class PostFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostFAQ
        fields = ['id', 'question', 'answer', 'order']

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
    is_scheduled = serializers.BooleanField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'category', 'category_name',
            'author_name', 'excerpt', 'cover_image', 'is_premium',
            'is_scheduled', 'views_count', 'published_at', 'created_at'
        ]

    def get_cover_image(self, obj):
        request = self.context.get('request')
        if obj.cover_image:
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url
        first_img = obj.images.first()
        if first_img and first_img.image:
            if request:
                return request.build_absolute_uri(first_img.image.url)
            return first_img.image.url
        return None

class PostDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    cover_image = serializers.SerializerMethodField()
    images = PostImageSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    faqs = PostFAQSerializer(many=True, read_only=True)
    rendered_content = serializers.CharField(read_only=True)
    is_locked = serializers.BooleanField(default=False, read_only=True)
    is_scheduled = serializers.BooleanField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'category', 'category_name',
            'author_name', 'excerpt', 'content', 'rendered_content', 'cover_image', 'images',
            'is_premium', 'is_locked', 'is_scheduled', 'views_count', 'published_at', 'created_at', 'updated_at',
            'comments', 'faqs'
        ]

    def get_cover_image(self, obj):
        request = self.context.get('request')
        if obj.cover_image:
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url
        first_img = obj.images.first()
        if first_img and first_img.image:
            if request:
                return request.build_absolute_uri(first_img.image.url)
            return first_img.image.url
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        user = request.user if request else None
        is_subscribed = user and user.is_authenticated and hasattr(user, 'profile') and user.profile.is_premium

        if instance.is_premium and not is_subscribed:
            data['is_locked'] = True
            lock_html = (
                f"<p><i>{instance.excerpt}</i></p>"
                "<hr/>"
                "<div style='background-color: #fff3cd; padding: 15px; border-radius: 6px; text-align: center; color: #856404;'>"
                "<b>🔒 Article Réservé aux Membres Abonnés</b><br/>"
                "Abonnez-vous dès aujourd'hui pour débloquer cet article exclusif, l'intégralité du guide et toutes les fiches d'experts !"
                "</div>"
            )
            data['content'] = lock_html
            data['rendered_content'] = lock_html
            data['images'] = []
        else:
            data['is_locked'] = False

        return data
