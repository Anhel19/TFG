from datetime import timedelta

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Reservation(models.Model):
    """
    Reserva en un restaurante. Puede ser de un usuario CUSTOMER registrado
    o de un invitado anónimo (con nombre, email y teléfono).
    La mesa se asigna automáticamente.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        CONFIRMED = 'CONFIRMED', 'Confirmada'
        CANCELLED = 'CANCELLED', 'Cancelada'

    # Estados que ocupan mesa (se cuentan para conflictos de disponibilidad)
    ACTIVE_STATUSES = [Status.PENDING, Status.CONFIRMED]

    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.CASCADE,
        related_name='reservations',
    )
    table = models.ForeignKey(
        'restaurants.Table',
        on_delete=models.PROTECT,
        related_name='reservations',
        help_text='Mesa asignada automáticamente.',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservations',
        help_text='Usuario registrado. Vacío si es reserva de invitado.',
    )

    guest_name = models.CharField(max_length=150)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20)

    reservation_datetime = models.DateTimeField(
        help_text='Fecha y hora de inicio de la reserva',
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
        default=Status.CONFIRMED,
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
            models.Index(fields=['table', 'status', 'reservation_datetime']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return (
            f"{self.guest_name} - {self.restaurant.name} - "
            f"{self.reservation_datetime:%d/%m/%Y %H:%M}"
        )

    @property
    def is_guest_reservation(self):
        return self.user is None

    @property
    def start_datetime(self):
        """Alias semántico para legibilidad en queries de solapamiento."""
        return self.reservation_datetime

    @property
    def end_datetime(self):
        """Hora de fin calculada con la duración media del restaurante."""
        duration = self.restaurant.average_reservation_duration
        return self.reservation_datetime + timedelta(minutes=duration)