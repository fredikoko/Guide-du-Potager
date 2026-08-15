from django.urls import path
from .views import (
    ToolListView, ToolDetailView,
    PlantFamilyListView, PlantFamilyDetailView,
    VegetableListView, VegetableDetailView
)

urlpatterns = [
    path('tools/', ToolListView.as_view(), name='tool_list'),
    path('tools/<int:pk>/', ToolDetailView.as_view(), name='tool_detail'),
    path('families/', PlantFamilyListView.as_view(), name='plantfamily_list'),
    path('families/<int:pk>/', PlantFamilyDetailView.as_view(), name='plantfamily_detail'),
    path('vegetables/', VegetableListView.as_view(), name='vegetable_list'),
    path('vegetables/<int:pk>/', VegetableDetailView.as_view(), name='vegetable_detail'),
]
