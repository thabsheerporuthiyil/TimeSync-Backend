from rest_framework import serializers
from .models import User
from orders.serializers import OrderSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'full_name', 'password')

    def create(self, validated_data):
        validated_data['role'] = 'user'
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "role",
            "orders",
        ]


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed("INVALID_CREDENTIALS")

        # Check if blocked
        if not user.is_active:
            raise AuthenticationFailed("ACCOUNT_BLOCKED")

        # Check password
        if not user.check_password(password):
            raise AuthenticationFailed("INVALID_CREDENTIALS")

        # Generate token
        data = super().validate(attrs)

        data["user"] = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        }

        return data
    
