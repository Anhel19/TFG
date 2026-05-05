from django.utils import timezone
from rest_framework import serializers

from .models import Reservation
from .availability import is_restaurant_open, find_available_table


class ReservationSerializer(serializers.ModelSerializer):
    table_number = serializers.IntegerField(source='table.number', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    end_datetime = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id', 'restaurant', 'restaurant_name',
            'table', 'table_number',
            'user',
            'guest_name', 'guest_email', 'guest_phone',
            'reservation_datetime', 'end_datetime',
            'party_size', 'notes',
            'status',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'table', 'user', 'status',
            'created_at', 'updated_at',
        ]

    def validate_reservation_datetime(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError(
                'La reserva debe ser en una fecha y hora futuras.'
            )
        return value

    def validate(self, attrs):
        restaurant = attrs.get('restaurant') or getattr(self.instance, 'restaurant', None)
        dt = attrs.get('reservation_datetime') or getattr(self.instance, 'reservation_datetime', None)
        party_size = attrs.get('party_size') or getattr(self.instance, 'party_size', None)

        if not (restaurant and dt and party_size):
            return attrs

        if not restaurant.is_active:
            raise serializers.ValidationError(
                {'restaurant': 'Este restaurante no está disponible.'}
            )

        if not is_restaurant_open(restaurant, dt):
            raise serializers.ValidationError(
                {'reservation_datetime': 'El restaurante está cerrado a esa hora.'}
            )

        exclude_id = self.instance.pk if self.instance else None
        table = find_available_table(
            restaurant, dt, party_size, exclude_reservation_id=exclude_id,
        )
        if table is None:
            raise serializers.ValidationError(
                {'party_size': 'No hay mesas disponibles para esa hora y nº de comensales.'}
            )

        self.context['assigned_table'] = table
        return attrs

    def create(self, validated_data):
        table = self.context.get('assigned_table')
        validated_data['table'] = table

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user

        return super().create(validated_data)