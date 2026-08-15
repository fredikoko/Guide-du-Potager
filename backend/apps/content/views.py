from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Part, Chapter
from .serializers import PartSerializer, ChapterListSerializer, ChapterDetailSerializer

class PartListView(generics.ListAPIView):
    queryset = Part.objects.all()
    serializer_class = PartSerializer
    permission_classes = [permissions.AllowAny]

class PartDetailView(generics.RetrieveAPIView):
    queryset = Part.objects.all()
    serializer_class = PartSerializer
    permission_classes = [permissions.AllowAny]

class ChapterListView(generics.ListAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterListSerializer
    permission_classes = [permissions.AllowAny]

class ChapterDetailView(generics.RetrieveAPIView):
    queryset = Chapter.objects.all()
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
        elif user and user.is_authenticated and hasattr(user, 'profile') and user.profile.subscription_active:
            has_access = True

        serializer = self.get_serializer(chapter)
        data = serializer.data

        if not has_access:
            # Mask content and images for non-subscribed users accessing premium content
            data['is_locked'] = True
            data['content'] = (
                f"<h1>🔒 {chapter.title} (Premium)</h1>"
                "<p>Ce chapitre est réservé aux abonnés Premium du Guide du Potager.</p>"
                "<p>Abonnez-vous pour débloquer l'accès complet à tous les chapitres, outils avancés, et fiches maladies & insectes !</p>"
            )
            data['images'] = []
        else:
            data['is_locked'] = False

        return Response(data)
