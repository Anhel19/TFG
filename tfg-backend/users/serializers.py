from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de nuevos clientes.
    El password se valida con los validadores de Django y se hashea automáticamente.
    Nota: el role siempre se fija a CUSTOMER en el registro público.
    Los OWNER se crean desde el admin de Django.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'phone',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {'password_confirm': 'Las contraseñas no coinciden.'}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        # En el registro público siempre se crea como CUSTOMER
        user = User.objects.create_user(
            **validated_data,
            password=password,
            role=User.Role.CUSTOMER,
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer de lectura para mostrar datos del usuario.
    No incluye campos sensibles como password.
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'phone',
            'role',
            'role_display',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'email', 'role', 'is_active', 'created_at']


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para cambiar la contraseña del usuario autenticado.
    """
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
    )

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('La contraseña actual no es correcta.')
        return value