from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
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
    serializer_class = ChapterListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        from django.db.models import Q
        qs = Chapter.objects.select_related('part').prefetch_related('images').all()
        part_id = self.request.query_params.get('part')
        if part_id:
            try:
                qs = qs.filter(part_id=int(part_id))
            except ValueError:
                pass
        search = self.request.query_params.get('search') or self.request.query_params.get('q')
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(part__title__icontains=search)
            )
        return qs.order_by('part__order', 'order')

class ChapterDetailView(generics.RetrieveAPIView):
    queryset = Chapter.objects.select_related('part').prefetch_related('images')
    serializer_class = ChapterDetailSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [JWTAuthentication]

    def retrieve(self, request, *args, **kwargs):
        chapter = self.get_object()
        user = request.user

        # Check premium restriction
        is_locked = (chapter.is_premium or chapter.part.is_premium)
        has_access = False

        if not is_locked:
            has_access = True
        elif user and user.is_authenticated:
            from apps.subscriptions.purchase_service import PurchaseService
            is_premium = hasattr(user, 'profile') and user.profile.is_premium
            has_access = is_premium or PurchaseService.user_has_guide_access(user)

        serializer = self.get_serializer(chapter)
        data = serializer.data

        if not has_access:
            # Mask content, rendered_content, and images for non-subscribed users accessing premium content
            lock_msg = (
                f"<h1>🔒 {chapter.title}</h1>"
                "<p>Ce chapitre est réservé aux abonnés du Guide du Potager Tropical ou aux acquéreurs du Guide Complet.</p>"
                "<p>Abonnez-vous ou achetez le guide pour débloquer l'accès complet et télécharger l'Ebook PDF !</p>"
            )
            data['is_locked'] = True
            data['content'] = lock_msg
            data['rendered_content'] = lock_msg
            data['images'] = []
        else:
            data['is_locked'] = False

        return Response(data)


class GuidePDFDownloadAPIView(generics.GenericAPIView):
    """Téléchargement du Guide Complet en PDF pour l'application mobile et l'API."""
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        from apps.subscriptions.purchase_service import PurchaseService
        if not PurchaseService.user_has_guide_access(request.user):
            return Response(
                {'error': "Vous n'avez pas acquis le Guide Complet."},
                status=status.HTTP_403_FORBIDDEN
            )
        from io import BytesIO
        from django.http import FileResponse
        from .pdf_service import generate_guide_pdf
        buf = BytesIO()
        generate_guide_pdf(buf, user=request.user)
        buf.seek(0)
        return FileResponse(buf, as_attachment=True, filename="Guide_Complet_du_Potager_Tropical.pdf", content_type='application/pdf')


class AboutPageView(generics.RetrieveAPIView):
    """Renvoie le contenu éditable de la page À Propos pour le web et le mobile."""
    serializer_class = AboutPageSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return AboutPage.get_solo()

