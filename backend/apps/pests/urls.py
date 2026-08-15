from django.urls import path
from .views import DiseaseListView, DiseaseDetailView, InsectListView, InsectDetailView

urlpatterns = [
    path('diseases/', DiseaseListView.as_view(), name='disease_list'),
    path('diseases/<int:pk>/', DiseaseDetailView.as_view(), name='disease_detail'),
    path('insects/', InsectListView.as_view(), name='insect_list'),
    path('insects/<int:pk>/', InsectDetailView.as_view(), name='insect_detail'),
]
