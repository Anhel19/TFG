from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from restaurants.models import OpeningHours, Restaurant, Table

from .models import Reservation


class ReservationListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listar reservas."""
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    table_number = serializers.IntegerField(source='table.number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id',
            'restaurant',
            'restaurant_name',
            'table',
            'table_number',
            'guest_name',
            'reservation_datetime',
            'party_size',
            'status',
            'status_display',
        ]


class ReservationDetailSerializer(serializers.ModelSerializer):
    """Serializer completo de una reserva."""
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    table_number = serializers.IntegerField(source='table.number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    end_datetime = serializers.DateTimeField(read_only=True)
    is_guest_reservation = serializers.BooleanField(read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id',
            'restaurant',
            'restaurant_name',
            'table',
            'table_number',
            'user',
            'guest_name',
            'guest_email',
            'guest_phone',
            'reservation_datetime',
            'end_datetime',
            'party_size',
            'notes',
            'status',
            'status_display',
            'is_guest_reservation',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'table',
            'created_at',
            'updated_at',
            'end_datetime',
            'is_guest_reservation',
        ]


class ReservationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear reservas.
    El cliente NO elige la mesa: se asigna automáticamente la mesa más pequeña
    que tenga capacidad suficiente y esté libre en ese horario.

    Validaciones:
      1. Fecha futura
      2. Restaurante activo
      3. Restaurante abierto en ese horario (OpeningHours)
      4. Existe alguna mesa con capacidad >= party_size y libre
    """

    table_number = serializers.IntegerField(source='table.number', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id',
            'restaurant',
            'restaurant_name',
            'table_number',
            'guest_name',
            'guest_email',
            'guest_phone',
            'reservation_datetime',
            'party_size',
            'notes',
        ]
        read_only_fields = ['id', 'restaurant_name', 'table_number']

    # ---------- Validaciones de campo ----------
    def validate_reservation_datetime(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError(
                'La fecha y hora de la reserva debe ser futura.'
            )
        # No permitir reservar con más de 6 meses de antelación
        if value > timezone.now() + timedelta(days=180):
            raise serializers.ValidationError(
                'No se puede reservar con más de 6 meses de antelación.'
            )
        return value

    def validate_party_size(self, value):
        if value < 1:
            raise serializers.ValidationError('El número de comensales debe ser al menos 1.')
        if value > 50:
            raise serializers.ValidationError(
                'Para grupos de más de 50 personas, contacta directamente con el restaurante.'
            )
        return value

    # ---------- Validación general ----------
    def validate(self, attrs):
        restaurant: Restaurant = attrs['restaurant']
        reservation_dt = attrs['reservation_datetime']
        party_size = attrs['party_size']

        # 1. Restaurante activo
        if not restaurant.is_active:
            raise serializers.ValidationError(
                {'restaurant': 'Este restaurante no admite reservas en este momento.'}
            )

        # 2. Restaurante abierto en ese horario
        weekday = reservation_dt.weekday()  # 0=Lunes ... 6=Domingo
        reservation_time = reservation_dt.time()
        reservation_end = (
            reservation_dt + timedelta(minutes=restaurant.average_reservation_duration)
        ).time()

        opening_hours = restaurant.opening_hours.filter(day_of_week=weekday)

        if not opening_hours.exists():
            raise serializers.ValidationError(
                {'reservation_datetime': 'El restaurante está cerrado ese día.'}
            )

        # La reserva (inicio Y fin) debe caber dentro de algún tramo de apertura
        fits_in_schedule = any(
            oh.opening_time <= reservation_time and reservation_end <= oh.closing_time
            for oh in opening_hours
        )
        if not fits_in_schedule:
            raise serializers.ValidationError({
                'reservation_datetime': (
                    'El restaurante no está abierto en ese horario completo. '
                    f'La reserva dura {restaurant.average_reservation_duration} minutos.'
                )
            })

        # 3. Buscar una mesa libre con capacidad suficiente
        available_table = self._find_available_table(restaurant, reservation_dt, party_size)
        if available_table is None:
            raise serializers.ValidationError({
                'reservation_datetime': (
                    'No hay mesas disponibles para ese horario y número de comensales. '
                    'Prueba con otra hora o reduce el grupo.'
                )
            })

        # Guardamos la mesa elegida para usarla en create()
        attrs['_assigned_table'] = available_table
        return attrs

    def _find_available_table(self, restaurant, reservation_dt, party_size):
        """
        Busca la mesa más pequeña con capacidad >= party_size que no tenga
        reservas activas solapadas con el rango [reservation_dt, reservation_end].
        """
        duration = timedelta(minutes=restaurant.average_reservation_duration)
        new_start = reservation_dt
        new_end = reservation_dt + duration

        # Mesas candidatas: del restaurante, activas, capacidad suficiente, ordenadas
        candidate_tables = restaurant.tables.filter(
            is_active=True,
            capacity__gte=party_size,
        ).order_by('capacity', 'number')

        for table in candidate_tables:
            # ¿Tiene esta mesa alguna reserva activa que solape?
            # Dos rangos [a1, a2] y [b1, b2] solapan si a1 < b2 AND b1 < a2
            conflicting = Reservation.objects.filter(
                table=table,
                status__in=Reservation.ACTIVE_STATUSES,
                reservation_datetime__lt=new_end,  # reserva existente empieza antes de que termine la nueva
            ).exclude(pk=getattr(self.instance, 'pk', None))

            # Filtramos en Python el otro lado de la condición (necesita end_datetime)
            has_conflict = False
            for existing in conflicting:
                existing_end = existing.reservation_datetime + duration
                if existing_end > new_start:
                    has_conflict = True
                    break

            if not has_conflict:
                return table

        return None

    def create(self, validated_data):
        table = validated_data.pop('_assigned_table')
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None

        reservation = Reservation.objects.create(
            table=table,
            user=user,
            **validated_data,
        )
        return reservation


class ReservationCancelSerializer(serializers.Serializer):
    """Serializer vacío para la acción de cancelar (solo cambia el status)."""
    pass