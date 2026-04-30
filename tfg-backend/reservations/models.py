from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Reservation(models.Model):
    """
    Reserva en un restaurante. Puede ser de un usuario registrado
    o de un invitado (sin cuenta).
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        CONFIRMED = 'CONFIRMED', 'Confirmada'
        CANCELLED = 'CANCELLED', 'Cancelada'
        COMPLETED = 'COMPLETED', 'Completada'
        NO_SHOW = 'NO_SHOW', 'No se presentó'

    # Estados que "ocupan" capacidad (los demás liberan plazas)
    ACTIVE_STATUSES = [Status.PENDING, Status.CONFIRMED]

    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.CASCADE,
        related_name='reservations',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservations',
        help_text='Usuario registrado. Si está vacío, es una reserva de invitado.',
    )

    guest_name = models.CharField(max_length=150)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20)

    reservation_datetime = models.DateTimeField(
        help_text='Fecha y hora de la reserva',
    )
    party_size = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Número de comensales',
    )
    notes = models.TextField(
        blank=True,
        help_text='Alergias, peticiones especiales, etc.',
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-reservation_datetime']
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        indexes = [
            models.Index(fields=['restaurant', 'reservation_datetime']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.guest_name} - {self.restaurant.name} - {self.reservation_datetime:%d/%m/%Y %H:%M}"

    @property
    def is_guest_reservation(self):
        """True si la reserva es de un invitado (sin cuenta)."""
        return self.user is None

    @property
    def end_datetime(self):
        """Hora estimada de fin de la reserva, según duración media del restaurante."""
        duration = self.restaurant.average_reservation_duration
        return self.reservation_datetime + timedelta(minutes=duration)

    # ---------- VALIDACIONES DE NEGOCIO ----------

    def clean(self):
        """
        Validaciones a nivel de modelo. Se ejecutan en admin y en formularios.
        También las llamamos manualmente desde save() para que se apliquen
        siempre, incluso cuando se crea por código o vía API.
        """
        super().clean()

        errors = {}

        # 1. La fecha/hora debe ser futura
        if self.reservation_datetime and self.reservation_datetime <= timezone.now():
            errors['reservation_datetime'] = 'La reserva debe ser en una fecha y hora futuras.'

        # 2. La hora debe estar dentro del horario del restaurante
        if self.reservation_datetime and self.restaurant_id:
            reservation_time = self.reservation_datetime.time()
            opening = self.restaurant.opening_time
            closing = self.restaurant.closing_time

            in_schedule = (
                opening <= reservation_time <= closing
                if opening <= closing
                else reservation_time >= opening or reservation_time <= closing
            )
            if not in_schedule:
                errors['reservation_datetime'] = (
                    f'El restaurante atiende de {opening:%H:%M} a {closing:%H:%M}.'
                )

        # 3. Nº de personas no puede superar la capacidad total
        if self.party_size and self.restaurant_id:
            if self.party_size > self.restaurant.capacity:
                errors['party_size'] = (
                    f'El restaurante tiene una capacidad máxima de '
                    f'{self.restaurant.capacity} personas.'
                )

        # 4. La capacidad agregada no puede superarse en la franja horaria
        if (
            self.party_size
            and self.reservation_datetime
            and self.restaurant_id
            and self.status in self.ACTIVE_STATUSES
        ):
            occupied = self._calculate_overlapping_capacity()
            available = self.restaurant.capacity - occupied
            if self.party_size > available:
                errors['party_size'] = (
                    f'No hay capacidad suficiente en esa franja. '
                    f'Disponibles: {available} de {self.restaurant.capacity}.'
                )

        if errors:
            raise ValidationError(errors)

    def _calculate_overlapping_capacity(self):
        """
        Suma las personas de las reservas activas que se solapan
        con la franja horaria de esta reserva.
        Excluye la reserva actual si ya está guardada (para permitir editarla).
        """
        start = self.reservation_datetime
        end = self.end_datetime

        # Buscamos reservas activas del mismo restaurante cuya franja [start, end]
        # se cruce con la nuestra. Dos franjas se solapan si:
        #     existing.start < self.end  Y  existing.end > self.start
        duration = timedelta(minutes=self.restaurant.average_reservation_duration)

        overlapping = Reservation.objects.filter(
            restaurant=self.restaurant,
            status__in=self.ACTIVE_STATUSES,
            reservation_datetime__lt=end,
        ).exclude(pk=self.pk)

        # Filtramos en Python por el otro extremo (no se puede en SQL puro
        # sin un campo end_datetime calculado, pero la query previa ya reduce mucho).
        total = 0
        for r in overlapping:
            r_end = r.reservation_datetime + duration
            if r_end > start:
                total += r.party_size

        return total

    def save(self, *args, **kwargs):
        """Garantiza que clean() se ejecute siempre antes de guardar."""
        self.full_clean()
        super().save(*args, **kwargs)