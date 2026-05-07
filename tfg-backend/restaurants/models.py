from django.conf import settings
from django.core.validators import MinValueValidator
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

    # Duración media de reserva (los horarios viven en OpeningHours)
    average_reservation_duration = models.PositiveIntegerField(
        default=90,
        validators=[MinValueValidator(15)],
        help_text='Duración media de una reserva en minutos',
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Restaurante'
        verbose_name_plural = 'Restaurantes'
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.city})"


class Table(models.Model):
    """
    Mesa individual de un restaurante.
    Cada mesa tiene su propio número y capacidad.
    """
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='tables',
    )
    number = models.PositiveIntegerField(
        help_text='Número identificador de la mesa dentro del restaurante',
    )
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Número de comensales que admite la mesa',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['restaurant', 'number']
        verbose_name = 'Mesa'
        verbose_name_plural = 'Mesas'
        constraints = [
            models.UniqueConstraint(
                fields=['restaurant', 'number'],
                name='unique_table_number_per_restaurant',
            ),
        ]

    def __str__(self):
        return f"Mesa {self.number} ({self.restaurant.name})"


class OpeningHours(models.Model):
    """
    Horario de apertura de un restaurante para un día concreto de la semana.
    Si un día no tiene OpeningHours, se considera cerrado.
    Permite varios tramos por día (ej: 13:00-16:00 y 20:00-23:30).
    """

    class Weekday(models.IntegerChoices):
        MONDAY = 0, 'Lunes'
        TUESDAY = 1, 'Martes'
        WEDNESDAY = 2, 'Miércoles'
        THURSDAY = 3, 'Jueves'
        FRIDAY = 4, 'Viernes'
        SATURDAY = 5, 'Sábado'
        SUNDAY = 6, 'Domingo'

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='opening_hours',
    )
    day_of_week = models.IntegerField(choices=Weekday.choices)
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    class Meta:
        ordering = ['restaurant', 'day_of_week', 'opening_time']
        verbose_name = 'Horario de apertura'
        verbose_name_plural = 'Horarios de apertura'
        indexes = [
            models.Index(fields=['restaurant', 'day_of_week']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(opening_time__lt=models.F('closing_time')),
                name='opening_before_closing',
            ),
        ]

    def __str__(self):
        return (
            f"{self.restaurant.name} - "
            f"{self.get_day_of_week_display()} "
            f"{self.opening_time}-{self.closing_time}"
        )