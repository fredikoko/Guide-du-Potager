from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Tool, PlantFamily, Vegetable, CalendarEntry
from .serializers import ToolSerializer, PlantFamilySerializer, VegetableSerializer, CalendarEntrySerializer

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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        has_access = not instance.is_premium or (user and user.is_authenticated and hasattr(user, 'profile') and user.profile.is_premium)

        serializer = self.get_serializer(instance)
        data = serializer.data

        if not has_access:
            data['is_locked'] = True
            data['description'] = "🔒 Contenu réservé : Abonnez-vous pour consulter la description complète."
            data['usage_tips'] = "🔒 Contenu réservé : Abonnez-vous pour débloquer les conseils d'utilisation."
            data['tropical_tips'] = "🔒 Contenu réservé : Abonnez-vous pour accéder aux spécificités en climat tropical."
        else:
            data['is_locked'] = False

        return Response(data)

class PlantFamilyListView(generics.ListAPIView):
    queryset = PlantFamily.objects.prefetch_related('vegetables__family')
    serializer_class = PlantFamilySerializer
    permission_classes = [permissions.AllowAny]

class PlantFamilyDetailView(generics.RetrieveAPIView):
    queryset = PlantFamily.objects.prefetch_related('vegetables__family')
    serializer_class = PlantFamilySerializer
    permission_classes = [permissions.AllowAny]

class VegetableListView(generics.ListAPIView):
    queryset = Vegetable.objects.select_related('family')
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
    queryset = Vegetable.objects.select_related('family')
    serializer_class = VegetableSerializer
    permission_classes = [permissions.AllowAny]

class CalendarEntryListView(generics.ListAPIView):
    queryset = CalendarEntry.objects.filter(is_active=True).select_related('vegetable__family')
    serializer_class = CalendarEntrySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        action = self.request.query_params.get('action', None)
        month = self.request.query_params.get('month', None)
        vegetable_id = self.request.query_params.get('vegetable', None)

        if action:
            queryset = queryset.filter(action=action)
        if month:
            queryset = queryset.filter(month=month)
        if vegetable_id:
            queryset = queryset.filter(vegetable_id=vegetable_id)
        return queryset

