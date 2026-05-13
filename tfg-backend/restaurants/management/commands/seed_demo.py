from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from restaurants.models import OpeningHours, Restaurant, Table


User = get_user_model()


RESTAURANTS_DATA = [
    {
        "name": "Trattoria San Marco",
        "description": (
            "Auténtica cocina italiana con pasta fresca elaborada cada día "
            "y una cuidada selección de vinos de la Toscana."
        ),
        "address": "Calle del Olivar, 12",
        "city": "Madrid",
        "phone": "+34 911 234 567",
        "email": "info@trattoriasanmarco.es",
    },
    {
        "name": "Sakura Sushi Bar",
        "description": (
            "Sushi tradicional japonés en barra. Pescado fresco del Mercado "
            "Central de Madrid y arroz cocinado al estilo Edo."
        ),
        "address": "Calle de Eloy Gonzalo, 27",
        "city": "Madrid",
        "phone": "+34 912 345 678",
        "email": "reservas@sakurasushibar.es",
    },
    {
        "name": "El Tucán",
        "description": (
            "Cocina mexicana de autor: tacos al pastor, mole poblano y una "
            "carta de mezcales artesanales."
        ),
        "address": "Calle de la Palma, 45",
        "city": "Madrid",
        "phone": "+34 913 456 789",
        "email": "hola@eltucan.es",
    },
]

# 6 mesas por restaurante: 2x2p, 2x4p, 1x6p, 1x8p
TABLES_LAYOUT = [
    (1, 2), (2, 2),
    (3, 4), (4, 4),
    (5, 6),
    (6, 8),
]

# Martes a domingo, dos tramos. Lunes cerrado.
OPENING_HOURS_LAYOUT = [
    (1, "13:00", "16:00"), (1, "20:00", "23:30"),  # Martes
    (2, "13:00", "16:00"), (2, "20:00", "23:30"),  # Miercoles
    (3, "13:00", "16:00"), (3, "20:00", "23:30"),  # Jueves
    (4, "13:00", "16:00"), (4, "20:00", "23:30"),  # Viernes
    (5, "13:00", "16:00"), (5, "20:00", "23:30"),  # Sabado
    (6, "13:00", "16:00"), (6, "20:00", "23:30"),  # Domingo
]


class Command(BaseCommand):
    help = (
        "Siembra datos de demo: 3 restaurantes internacionales con mesas y "
        "horarios. Idempotente: se puede ejecutar varias veces sin duplicar."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        # 1. Owner unico para los 3 restaurantes
        owner, created = User.objects.get_or_create(
            email="owner.demo@truetable.com",
            defaults={
                "username": "owner_demo",
                "role": User.Role.OWNER,
                "first_name": "Demo",
                "last_name": "Owner",
            },
        )
        if created:
            owner.set_unusable_password()
            owner.save()
            self.stdout.write(self.style.SUCCESS(
                f"Owner creado: {owner.email}"
            ))
        else:
            self.stdout.write(f"Owner ya existia: {owner.email}")

        # 2. Restaurantes + mesas + horarios
        for data in RESTAURANTS_DATA:
            defaults = {k: v for k, v in data.items() if k != "name"}
            defaults["owner"] = owner

            restaurant, r_created = Restaurant.objects.get_or_create(
                name=data["name"],
                defaults=defaults,
            )
            if r_created:
                self.stdout.write(self.style.SUCCESS(
                    f"Restaurante creado: {restaurant.name}"
                ))
            else:
                self.stdout.write(f"Restaurante ya existia: {restaurant.name}")

            # Mesas
            for number, capacity in TABLES_LAYOUT:
                _, t_created = Table.objects.get_or_create(
                    restaurant=restaurant,
                    number=number,
                    defaults={"capacity": capacity},
                )
                if t_created:
                    self.stdout.write(f"  + Mesa {number} ({capacity}p)")

            # Horarios
            for weekday, opening, closing in OPENING_HOURS_LAYOUT:
                _, h_created = OpeningHours.objects.get_or_create(
                    restaurant=restaurant,
                    day_of_week=weekday,
                    opening_time=opening,
                    defaults={"closing_time": closing},
                )
                if h_created:
                    label = OpeningHours.Weekday(weekday).label
                    self.stdout.write(f"  + {label} {opening}-{closing}")

        self.stdout.write(self.style.SUCCESS("\nSeed completado."))