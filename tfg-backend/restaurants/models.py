from django.conf import settings
from django.db import models


class Restaurant(models.Model):
    """
    Restaurante registrado en la plataforma.
    Cada restaurante tiene un dueño (User con role=OWNER).
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='restaurants',
        help_text='Usuario dueño del restaurante',
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    # Capacidad y horarios
    capacity = models.PositiveIntegerField(
        help_text='Número máximo de comensales simultáneos',
    )
    opening_time = models.TimeField(help_text='Hora de apertura (ej. 13:00)')
    closing_time = models.TimeField(help_text='Hora de cierre (ej. 23:30)')
    average_reservation_duration = models.PositiveIntegerField(
        default=90,
        help_text='Duración media de una reserva en minutos',
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Restaurante'
        verbose_name_plural = 'Restaurantes'

    def __str__(self):
        return f"{self.name} ({self.city})"