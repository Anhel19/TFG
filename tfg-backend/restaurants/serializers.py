from rest_framework import serializers

from users.models import User

from .models import OpeningHours, Restaurant, Table


class TableSerializer(serializers.ModelSerializer):
    """Serializer de mesas. Las mesas se gestionan dentro de un restaurante."""

    class Meta:
        model = Table
        fields = ['id', 'restaurant', 'number', 'capacity', 'is_active']
        read_only_fields = ['id']

    def validate(self, attrs):
        # Validar que el restaurante pertenece al usuario que crea la mesa
        # (excepto si es admin). Lo refinaremos con permisos en los ViewSets.
        request = self.context.get('request')
        restaurant = attrs.get('restaurant') or getattr(self.instance, 'restaurant', None)

        if request and restaurant and not request.user.is_staff:
            if restaurant.owner_id != request.user.id:
                raise serializers.ValidationError(
                    'No puedes gestionar mesas de un restaurante que no es tuyo.'
                )
        return attrs


class OpeningHoursSerializer(serializers.ModelSerializer):
    """Serializer de horarios de apertura."""
    day_of_week_display = serializers.CharField(
        source='get_day_of_week_display',
        read_only=True,
    )

    class Meta:
        model = OpeningHours
        fields = [
            'id',
            'restaurant',
            'day_of_week',
            'day_of_week_display',
            'opening_time',
            'closing_time',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        opening = attrs.get('opening_time') or getattr(self.instance, 'opening_time', None)
        closing = attrs.get('closing_time') or getattr(self.instance, 'closing_time', None)

        if opening and closing and opening >= closing:
            raise serializers.ValidationError(
                'La hora de apertura debe ser anterior a la hora de cierre.'
            )

        # Mismo check de propiedad del restaurante que en TableSerializer
        request = self.context.get('request')
        restaurant = attrs.get('restaurant') or getattr(self.instance, 'restaurant', None)

        if request and restaurant and not request.user.is_staff:
            if restaurant.owner_id != request.user.id:
                raise serializers.ValidationError(
                    'No puedes gestionar horarios de un restaurante que no es tuyo.'
                )
        return attrs


class RestaurantListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listado público de restaurantes."""

    class Meta:
        model = Restaurant
        fields = [
            'id',
            'name',
            'description',
            'city',
            'address',
            'phone',
            'is_active',
        ]


class RestaurantDetailSerializer(serializers.ModelSerializer):
    """Serializer completo con mesas y horarios anidados (solo lectura)."""
    tables = TableSerializer(many=True, read_only=True)
    opening_hours = OpeningHoursSerializer(many=True, read_only=True)
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            'id',
            'owner',
            'owner_email',
            'name',
            'description',
            'address',
            'city',
            'phone',
            'email',
            'average_reservation_duration',
            'is_active',
            'created_at',
            'updated_at',
            'tables',
            'opening_hours',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class RestaurantWriteSerializer(serializers.ModelSerializer):
    """Serializer para crear/editar restaurantes. El owner se asigna desde la vista."""

    class Meta:
        model = Restaurant
        fields = [
            'id',
            'name',
            'description',
            'address',
            'city',
            'phone',
            'email',
            'average_reservation_duration',
            'is_active',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        request = self.context.get('request')
        # Solo OWNER o ADMIN pueden crear restaurantes
        if request and not request.user.is_staff:
            if request.user.role not in [User.Role.OWNER, User.Role.ADMIN]:
                raise serializers.ValidationError(
                    'Solo los usuarios con rol OWNER pueden crear restaurantes.'
                )
        return attrs