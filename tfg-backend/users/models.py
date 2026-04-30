from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Usuario personalizado del sistema de reservas.
    Hereda de AbstractUser (username, email, password, first_name, last_name...)
    y añade campos específicos del dominio.
    """

    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'Cliente'
        OWNER = 'OWNER', 'Dueño de restaurante'
        ADMIN = 'ADMIN', 'Administrador'

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Usaremos el email como identificador principal para login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # username sigue siendo obligatorio

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
# Modelo de usuario personalizado
AUTH_USER_MODEL = 'users.User'