from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import F, Q
from .models import Category, Post, Comment
from .serializers import CategorySerializer, PostListSerializer, PostDetailSerializer, CommentSerializer

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class PostListView(generics.ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Post.objects.filter(is_published=True)
        category_id = self.request.query_params.get('category')
        search = self.request.query_params.get('search')

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(excerpt__icontains=search) |
                Q(content__icontains=search)
            )

        return queryset

class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.filter(is_published=True)
    serializer_class = PostDetailSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        Post.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class AddCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk, is_published=True)
        except Post.DoesNotExist:
            return Response({'error': 'Article non trouvé.'}, status=status.HTTP_404_NOT_FOUND)

        content = request.data.get('content')
        if not content:
            return Response({'error': 'Le commentaire ne peut pas être vide.'}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content
        )
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
