from django.urls import path
from .views import PartListView, PartDetailView, ChapterListView, ChapterDetailView

urlpatterns = [
    path('parts/', PartListView.as_view(), name='part_list'),
    path('parts/<int:pk>/', PartDetailView.as_view(), name='part_detail'),
    path('chapters/', ChapterListView.as_view(), name='chapter_list'),
    path('chapters/<int:pk>/', ChapterDetailView.as_view(), name='chapter_detail'),
]
