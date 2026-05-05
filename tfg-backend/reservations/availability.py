"""
Lógica de búsqueda de mesas disponibles y validación de disponibilidad.
"""
from datetime import datetime, timedelta

from django.utils import timezone

from restaurants.models import Table, OpeningHours


def is_restaurant_open(restaurant, dt):
    """
    Comprueba si el restaurante está abierto en el datetime `dt`.
    """
    weekday = dt.weekday()  # lunes=0, domingo=6
    target_time = dt.time()

    schedules = OpeningHours.objects.filter(
        restaurant=restaurant,
        day_of_week=weekday,
    )

    for schedule in schedules:
        if schedule.opening_time <= target_time <= schedule.closing_time:
            return True
    return False


def find_available_table(restaurant, start_dt, party_size, exclude_reservation_id=None):
    """
    Devuelve la mesa más PEQUEÑA del restaurante que:
      - Esté activa
      - Tenga capacidad suficiente para `party_size`
      - No tenga reservas activas que se solapen con [start_dt, end_dt]

    Devuelve None si no hay ninguna disponible.
    """
    from .models import Reservation  # import diferido para evitar circular

    duration = timedelta(minutes=restaurant.average_reservation_duration)
    end_dt = start_dt + duration

    candidate_tables = Table.objects.filter(
        restaurant=restaurant,
        is_active=True,
        capacity__gte=party_size,
    ).order_by('capacity', 'number')

    for table in candidate_tables:
        overlapping = Reservation.objects.filter(
            table=table,
            status__in=Reservation.ACTIVE_STATUSES,
            reservation_datetime__lt=end_dt,
        )
        if exclude_reservation_id:
            overlapping = overlapping.exclude(pk=exclude_reservation_id)

        has_overlap = False
        for r in overlapping:
            r_end = r.reservation_datetime + duration
            if r_end > start_dt:
                has_overlap = True
                break

        if not has_overlap:
            return table

    return None


def get_available_slots(restaurant, date, party_size, slot_minutes=30):
    """
    Devuelve la lista de slots horarios disponibles para una fecha concreta.
    """
    weekday = date.weekday()
    schedules = OpeningHours.objects.filter(
        restaurant=restaurant,
        day_of_week=weekday,
    ).order_by('opening_time')

    if not schedules.exists():
        return []

    duration = timedelta(minutes=restaurant.average_reservation_duration)
    available = []
    now = timezone.now()

    for schedule in schedules:
        current = timezone.make_aware(
            datetime.combine(date, schedule.opening_time)
        )
        last_start = timezone.make_aware(
            datetime.combine(date, schedule.closing_time)
        ) - duration

        while current <= last_start:
            if current > now:
                table = find_available_table(restaurant, current, party_size)
                if table is not None:
                    available.append({
                        'datetime': current,
                        'table_id': table.id,
                        'table_capacity': table.capacity,
                    })
            current += timedelta(minutes=slot_minutes)

    return available