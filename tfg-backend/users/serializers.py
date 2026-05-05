from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Lectura de perfil. Se anida en otros serializers (ej. reservas)."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'role',
                  'first_name', 'last_name']
        read_only_fields = ['id', 'role']  # el rol solo lo cambia un admin


class UserRegisterSerializer(serializers.ModelSerializer):
    """Registro con validación de contraseña y confirmación."""
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm',
                  'phone', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {'password': 'Las contraseñas no coinciden.'}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Añade email y rol al JWT, y devuelve el usuario en el login."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data