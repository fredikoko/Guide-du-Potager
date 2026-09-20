from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import UserProfile
from .validators import validate_server_email

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    climate_zone_display = serializers.CharField(source='get_climate_zone_display', read_only=True)
    garden_type_display = serializers.CharField(source='get_garden_type_display', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'subscription_active', 'subscription_end_date',
            'country', 'climate_zone', 'climate_zone_display',
            'garden_type', 'garden_type_display',
            'preferences', 'history', 'avatar', 'phone_number'
        ]

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'created_at', 'profile']
        extra_kwargs = {
            'email': {'required': False}
        }

    def validate_email(self, value):
        try:
            return validate_server_email(value, user=self.instance)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message if hasattr(e, 'message') else str(e))

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)
    phone_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm', 'phone_number']

    def validate_email(self, value):
        try:
            return validate_server_email(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message if hasattr(e, 'message') else str(e))

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        phone_number = validated_data.pop('phone_number', '')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            is_active=False
        )
        if phone_number:
            user.profile.phone_number = phone_number
            user.profile.save()
        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
