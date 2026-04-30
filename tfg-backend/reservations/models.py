from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


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

    # Restaurante donde se hace la reserva
    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.CASCADE,
        related_name='reservations',
    )

    # Usuario registrado (opcional: si es null, es un invitado)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservations',
        help_text='Usuario registrado. Si está vacío, es una reserva de invitado.',
    )

    # Datos del cliente (siempre obligatorios; si hay user, se replican
    # para que la reserva sea autocontenida y se pueda contactar fácilmente)
    guest_name = models.CharField(max_length=150)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20)

    # Datos de la reserva
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