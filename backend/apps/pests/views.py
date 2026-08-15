from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Disease, Insect
from .serializers import DiseaseSerializer, InsectSerializer

class DiseaseListView(generics.ListAPIView):
    queryset = Disease.objects.all()
    serializer_class = DiseaseSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

class DiseaseDetailView(generics.RetrieveAPIView):
    queryset = Disease.objects.all()
    serializer_class = DiseaseSerializer
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        has_access = not instance.is_premium or (user and user.is_authenticated and hasattr(user, 'profile') and user.profile.subscription_active)

        serializer = self.get_serializer(instance)
        data = serializer.data

        if not has_access:
            data['is_locked'] = True
            data['symptoms'] = "🔒 Contenu Premium : Abonnez-vous pour consulter les symptômes détaillés."
            data['treatment'] = "🔒 Contenu Premium : Abonnez-vous pour débloquer les traitements."
            data['prevention'] = "🔒 Contenu Premium : Abonnez-vous pour accéder aux conseils de prévention."
        else:
            data['is_locked'] = False

        return Response(data)

class InsectListView(generics.ListAPIView):
    queryset = Insect.objects.all()
    serializer_class = InsectSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

class InsectDetailView(generics.RetrieveAPIView):
    queryset = Insect.objects.all()
    serializer_class = InsectSerializer
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        has_access = not instance.is_premium or (user and user.is_authenticated and hasattr(user, 'profile') and user.profile.subscription_active)

        serializer = self.get_serializer(instance)
        data = serializer.data

        if not has_access:
            data['is_locked'] = True
            data['description'] = "🔒 Contenu Premium : Abonnez-vous pour consulter la description complète."
            data['damage'] = "🔒 Contenu Premium : Abonnez-vous pour voir les dégâts constatés."
            data['solution'] = "🔒 Contenu Premium : Abonnez-vous pour accéder aux solutions bio et traitements."
        else:
            data['is_locked'] = False

        return Response(data)
