from django.urls import path
from .views import CategoryListView, PostListView, PostDetailView, AddCommentView

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='blog_category_list'),
    path('posts/', PostListView.as_view(), name='blog_post_list'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='blog_post_detail'),
    path('posts/<int:pk>/comments/', AddCommentView.as_view(), name='blog_add_comment'),
]
