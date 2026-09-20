from rest_framework import status, generics, permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import UserProfile
from .validators import validate_server_email
from .services import send_verification_email, verify_email_code
from .serializers import (
    RegisterSerializer, UserSerializer, UserProfileSerializer,
    ChangePasswordSerializer, PasswordResetSerializer
)

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)

    def validate(self, attrs):
        user_input = attrs.get('email') or attrs.get('username') or self.initial_data.get('email') or self.initial_data.get('username')
        if not user_input:
            raise serializers.ValidationError({'email': 'Email ou nom d\'utilisateur obligatoire.'})

        if '@' in user_input:
            attrs['email'] = user_input
        else:
            try:
                user_obj = User.objects.get(username__iexact=user_input)
                attrs['email'] = user_obj.email
            except User.DoesNotExist:
                attrs['email'] = user_input

        data = super().validate(attrs)
        user_serializer = UserSerializer(self.user)
        data['user'] = user_serializer.data
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        try:
            send_verification_email(user.email, purpose='registration', user=user)
        except Exception as e:
            user.delete()
            return Response(
                {'error': f"Échec de l'envoi de l'e-mail de confirmation : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'message': 'Un code de confirmation à 6 chiffres a été envoyé à votre adresse e-mail.',
            'email': user.email,
            'requires_verification': True
        }, status=status.HTTP_201_CREATED)

class VerifyRegistrationView(APIView):
    """
    Valide le code de confirmation à 6 chiffres pour activer un compte nouvellement créé.
    Renvoie les jetons JWT et connecte automatiquement l'utilisateur.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        code = request.data.get('code', '').strip()

        if not email or not code:
            return Response(
                {'error': "L'adresse email et le code sont obligatoires."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            verify_email_code(email, code, purpose='registration')
        except DjangoValidationError as e:
            err_msg = e.message if hasattr(e, 'message') else str(e)
            return Response({'error': err_msg}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({'error': "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = True
        user.save(update_fields=['is_active'])

        refresh = RefreshToken.for_user(user)
        user_serializer = UserSerializer(user)

        return Response({
            'message': "Compte confirmé et activé avec succès !",
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)

class ResendVerificationCodeView(APIView):
    """
    Renvoie un nouveau code de confirmation pour l'inscription ou le changement d'email.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        purpose = request.data.get('purpose', 'registration')

        if not email:
            return Response({'error': "L'adresse email est obligatoire."}, status=status.HTTP_400_BAD_REQUEST)

        user = None
        if purpose == 'registration':
            user = User.objects.filter(email__iexact=email).first()
            if not user:
                return Response({'error': "Aucun compte trouvé pour cet email."}, status=status.HTTP_404_NOT_FOUND)
            if user.is_active:
                return Response({'error': "Ce compte est déjà actif. Vous pouvez vous connecter."}, status=status.HTTP_400_BAD_REQUEST)
        elif purpose == 'email_change':
            if not request.user or not request.user.is_authenticated:
                return Response({'error': "Authentification requise pour le changement d'email."}, status=status.HTTP_401_UNAUTHORIZED)
            user = request.user

        try:
            send_verification_email(email, purpose=purpose, user=user)
            return Response({
                'message': "Un nouveau code de confirmation a été envoyé à votre adresse email.",
                'email': email
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f"Échec de l'envoi de l'e-mail : {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': ['Mot de passe actuel incorrect.']}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Mot de passe modifié avec succès.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                return Response({'message': f'Un email de réinitialisation a été envoyé à {email}.'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'message': 'Si cet email existe, un message a été envoyé.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AccountDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({'message': 'Compte supprimé avec succès.'}, status=status.HTTP_204_NO_CONTENT)

class ValidateEmailView(APIView):
    """
    Vérifie la validité et la disponibilité d'une adresse email côté serveur.
    Accepte {"email": "...", "mode": "register" | "update"}.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '')
        mode = request.data.get('mode', 'register')
        user_to_exclude = request.user if (mode == 'update' and request.user and request.user.is_authenticated) else None

        try:
            valid_email = validate_server_email(email, user=user_to_exclude)
            return Response({
                'valid': True,
                'email': valid_email,
                'message': 'Adresse email valide et disponible.'
            }, status=status.HTTP_200_OK)
        except DjangoValidationError as e:
            err_msg = e.message if hasattr(e, 'message') else str(e)
            return Response({
                'valid': False,
                'error': err_msg
            }, status=status.HTTP_400_BAD_REQUEST)

class RequestEmailChangeView(APIView):
    """
    Initie une demande de changement d'adresse e-mail.
    Vérifie la validité et la disponibilité du nouvel e-mail, puis envoie le code à 6 chiffres.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        new_email = request.data.get('new_email', '').strip()
        if not new_email:
            return Response({'error': "La nouvelle adresse email est requise."}, status=status.HTTP_400_BAD_REQUEST)

        if new_email.lower() == request.user.email.lower():
            return Response({'error': "La nouvelle adresse email est identique à l'actuelle."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validated_email = validate_server_email(new_email, user=request.user)
        except DjangoValidationError as e:
            err_msg = e.message if hasattr(e, 'message') else str(e)
            return Response({'error': err_msg}, status=status.HTTP_400_BAD_REQUEST)

        try:
            send_verification_email(validated_email, purpose='email_change', user=request.user)
            return Response({
                'message': f"Un code de confirmation a été envoyé à {validated_email}.",
                'pending_email': validated_email,
                'email_change_pending': True
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f"Échec de l'envoi de l'e-mail : {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ConfirmEmailChangeView(APIView):
    """
    Confirme le changement d'adresse e-mail avec le code à 6 chiffres reçu sur la nouvelle adresse.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        new_email = request.data.get('new_email', '').strip()
        code = request.data.get('code', '').strip()

        if not new_email or not code:
            return Response(
                {'error': "La nouvelle adresse email et le code sont obligatoires."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_server_email(new_email, user=request.user)
            verify_email_code(new_email, code, purpose='email_change', user=request.user)
        except DjangoValidationError as e:
            err_msg = e.message if hasattr(e, 'message') else str(e)
            return Response({'error': err_msg}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user.email = new_email.lower()
        user.save(update_fields=['email'])

        serializer = UserSerializer(user)
        return Response({
            'message': "Adresse email modifiée avec succès !",
            'user': serializer.data
        }, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        profile_data = request.data.get('profile', {})
        email_change_pending = False
        pending_email = None

        if 'email' in request.data and request.data['email']:
            new_email = request.data['email'].strip()
            if new_email.lower() != user.email.lower():
                try:
                    validated_email = validate_server_email(new_email, user=user)
                    send_verification_email(validated_email, purpose='email_change', user=user)
                    email_change_pending = True
                    pending_email = validated_email
                except DjangoValidationError as e:
                    err_msg = e.message if hasattr(e, 'message') else str(e)
                    return Response({'error': err_msg, 'email': [err_msg]}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error': f"Échec de l'envoi du code de confirmation : {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if 'username' in request.data and request.data['username']:
            user.username = request.data['username']
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
        user.save()

        profile = user.profile
        if 'phone_number' in profile_data:
            profile.phone_number = profile_data['phone_number']
        elif 'phone_number' in request.data:
            profile.phone_number = request.data['phone_number']

        if 'preferences' in profile_data:
            profile.preferences = profile_data['preferences']
        elif 'preferences' in request.data:
            profile.preferences = request.data['preferences']

        if 'country' in profile_data:
            profile.country = profile_data['country']
        elif 'country' in request.data:
            profile.country = request.data['country']

        if 'climate_zone' in profile_data:
            profile.climate_zone = profile_data['climate_zone']
        elif 'climate_zone' in request.data:
            profile.climate_zone = request.data['climate_zone']

        if 'garden_type' in profile_data:
            profile.garden_type = profile_data['garden_type']
        elif 'garden_type' in request.data:
            profile.garden_type = request.data['garden_type']

        profile.save()

        serializer = self.get_serializer(user)
        resp_data = serializer.data
        if email_change_pending:
            resp_data['email_change_pending'] = True
            resp_data['pending_email'] = pending_email
            resp_data['message'] = f"Un code de confirmation a été envoyé à {pending_email} pour valider ce changement."
        return Response(resp_data)

class UserHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        return Response({'history': profile.history})

    def post(self, request):
        profile = request.user.profile
        item = request.data.get('item')
        if item:
            history = profile.history or []
            history = [h for h in history if h.get('id') != item.get('id') or h.get('type') != item.get('type')]
            history.insert(0, item)
            profile.history = history[:50]
            profile.save()
        return Response({'history': profile.history})
