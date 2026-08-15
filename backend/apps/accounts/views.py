from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import UserProfile
from .serializers import (
    RegisterSerializer, UserSerializer, UserProfileSerializer,
    ChangePasswordSerializer, PasswordResetSerializer
)

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
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
        user_serializer = UserSerializer(user)
        return Response({
            'message': 'Compte créé avec succès',
            'user': user_serializer.data
        }, status=status.HTTP_201_CREATED)

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
                # In production, send reset email here.
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

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        profile_data = request.data.get('profile', {})
        if 'username' in request.data:
            user.username = request.data['username']
            user.save()
        
        profile = user.profile
        if 'phone_number' in profile_data:
            profile.phone_number = profile_data['phone_number']
        if 'preferences' in profile_data:
            profile.preferences = profile_data['preferences']
        profile.save()

        serializer = self.get_serializer(user)
        return Response(serializer.data)

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
            # Keep unique items, newest first
            history = [h for h in history if h.get('id') != item.get('id') or h.get('type') != item.get('type')]
            history.insert(0, item)
            profile.history = history[:50]  # Store last 50 items
            profile.save()
        return Response({'history': profile.history})
