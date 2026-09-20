from rest_framework import status, generics, permissions, serializers
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
            history = [h for h in history if h.get('id') != item.get('id') or h.get('type') != item.get('type')]
            history.insert(0, item)
            profile.history = history[:50]
            profile.save()
        return Response({'history': profile.history})
