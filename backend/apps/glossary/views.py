from rest_framework import generics, permissions
from .models import Tool, PlantFamily, Vegetable
from .serializers import ToolSerializer, PlantFamilySerializer, VegetableSerializer

class ToolListView(generics.ListAPIView):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', None)
        search = self.request.query_params.get('search', None)
        if category:
            queryset = queryset.filter(category=category)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

class ToolDetailView(generics.RetrieveAPIView):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
    permission_classes = [permissions.AllowAny]

class PlantFamilyListView(generics.ListAPIView):
    queryset = PlantFamily.objects.all()
    serializer_class = PlantFamilySerializer
    permission_classes = [permissions.AllowAny]

class PlantFamilyDetailView(generics.RetrieveAPIView):
    queryset = PlantFamily.objects.all()
    serializer_class = PlantFamilySerializer
    permission_classes = [permissions.AllowAny]

class VegetableListView(generics.ListAPIView):
    queryset = Vegetable.objects.all()
    serializer_class = VegetableSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        family_id = self.request.query_params.get('family', None)
        search = self.request.query_params.get('search', None)
        if family_id:
            queryset = queryset.filter(family_id=family_id)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

class VegetableDetailView(generics.RetrieveAPIView):
    queryset = Vegetable.objects.all()
    serializer_class = VegetableSerializer
    permission_classes = [permissions.AllowAny]
