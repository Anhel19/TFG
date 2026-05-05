from rest_framework import serializers
from .models import Restaurant, Table, OpeningHours


class OpeningHoursSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(
        source='get_day_of_week_display', read_only=True,
    )

    class Meta:
        model = OpeningHours
        fields = ['id', 'restaurant', 'day_of_week', 'day_name',
                  'opening_time', 'closing_time']

    def validate(self, attrs):
        opening = attrs.get(
            'opening_time',
            getattr(self.instance, 'opening_time', None),
        )
        closing = attrs.get(
            'closing_time',
            getattr(self.instance, 'closing_time', None),
        )
        if opening and closing and opening >= closing:
            raise serializers.ValidationError(
                'La hora de apertura debe ser anterior a la de cierre.'
            )
        return attrs


class TableSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(
        source='restaurant.name', read_only=True,
    )

    class Meta:
        model = Table
        fields = ['id', 'restaurant', 'restaurant_name',
                  'number', 'capacity', 'is_active']

    def validate_capacity(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'La capacidad debe ser al menos 1.'
            )
        return value


class RestaurantListSerializer(serializers.ModelSerializer):
    """Versión ligera para listados."""
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'city', 'address', 'phone', 'is_active']


class RestaurantDetailSerializer(serializers.ModelSerializer):
    """Versión completa con mesas y horarios anidados."""
    tables = TableSerializer(many=True, read_only=True)
    opening_hours = OpeningHoursSerializer(many=True, read_only=True)
    owner_name = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'owner', 'owner_name', 'name', 'description',
                  'address', 'city', 'phone', 'email',
                  'average_reservation_duration',
                  'is_active', 'tables', 'opening_hours',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']