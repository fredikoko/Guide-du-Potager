from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Part, Chapter, AboutPage
from .serializers import PartSerializer, ChapterListSerializer, ChapterDetailSerializer, AboutPageSerializer

class PartListView(generics.ListAPIView):
    queryset = Part.objects.prefetch_related('chapters')
    serializer_class = PartSerializer
    permission_classes = [permissions.AllowAny]

class PartDetailView(generics.RetrieveAPIView):
    queryset = Part.objects.prefetch_related('chapters')
    serializer_class = PartSerializer
    permission_classes = [permissions.AllowAny]

class ChapterListView(generics.ListAPIView):
    queryset = Chapter.objects.select_related('part')
    serializer_class = ChapterListSerializer
    permission_classes = [permissions.AllowAny]

class ChapterDetailView(generics.RetrieveAPIView):
    queryset = Chapter.objects.select_related('part').prefetch_related('images')
    serializer_class = ChapterDetailSerializer
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        chapter = self.get_object()
        user = request.user

        # Check premium restriction
        is_locked = (chapter.is_premium or chapter.part.is_premium)
        has_access = False

        if not is_locked:
            has_access = True
        elif user and user.is_authenticated and hasattr(user, 'profile') and user.profile.is_premium:
            has_access = True

        serializer = self.get_serializer(chapter)
        data = serializer.data

        if not has_access:
            # Mask content and images for non-subscribed users accessing premium content
            data['is_locked'] = True
            data['content'] = (
                f"<h1>🔒 {chapter.title}</h1>"
                "<p>Ce chapitre est réservé aux abonnés du Guide du Potager Tropical.</p>"
                "<p>Abonnez-vous pour débloquer l'accès complet à tous les chapitres, outils avancés, et fiches maladies & insectes !</p>"
            )
            data['images'] = []
        else:
            data['is_locked'] = False

        return Response(data)


class AboutPageView(generics.RetrieveAPIView):
    """Renvoie le contenu éditable de la page À Propos pour le web et le mobile."""
    serializer_class = AboutPageSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return AboutPage.get_solo()

