# TFG Backend — API de Reservas de Restaurantes

API REST desarrollada con **Django 6** y **Django REST Framework** para la gestión de reservas de restaurantes.

---

## Tecnologías

- Python 3.11+
- Django 6
- Django REST Framework
- JWT (djangorestframework-simplejwt)
- PostgreSQL (producción) / SQLite (desarrollo)
- drf-spectacular (documentación OpenAPI)
- Gunicorn + WhiteNoise (despliegue)

---

## Instalación local

### 1. Clonar el repositorio y entrar al directorio del backend

```bash
git clone <url-del-repo>
cd tfg-backend
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Crear el archivo `.env`

Crea un archivo `.env` en la raíz del backend con estas variables:

```env
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

> En producción cambia `DEBUG=False` y usa una base de datos PostgreSQL en `DATABASE_URL`.

### 5. Aplicar migraciones y crear superusuario

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Arrancar el servidor de desarrollo

```bash
python manage.py runserver
```

La API estará disponible en `http://localhost:8000/api/`

---

## Endpoints principales

| Método | URL | Descripción | Acceso |
|--------|-----|-------------|--------|
| POST | `/api/auth/register/` | Registro de usuario | Público |
| POST | `/api/auth/login/` | Login (devuelve JWT) | Público |
| POST | `/api/auth/token/refresh/` | Refresca el token | Autenticado |
| GET | `/api/restaurants/` | Listar restaurantes | Público |
| POST | `/api/restaurants/` | Crear restaurante | OWNER |
| GET | `/api/restaurants/mine/` | Mis restaurantes | OWNER |
| GET | `/api/restaurants/{id}/` | Detalle restaurante | Público |
| GET | `/api/tables/?restaurant={id}` | Mesas de un restaurante | Público |
| GET | `/api/opening-hours/?restaurant={id}` | Horarios | Público |
| POST | `/api/reservations/` | Crear reserva | Público |
| GET | `/api/reservations/` | Mis reservas | Autenticado |
| POST | `/api/reservations/{id}/cancel/` | Cancelar reserva | Cliente/Owner |

---

## Documentación interactiva (Swagger)

Con el servidor arrancado, accede a:

- Swagger UI: `http://localhost:8000/api/schema/swagger-ui/`
- ReDoc: `http://localhost:8000/api/schema/redoc/`

---

## Roles de usuario

| Rol | Descripción |
|-----|-------------|
| `CUSTOMER` | Cliente que realiza reservas |
| `OWNER` | Dueño de restaurante, gestiona sus locales y reservas |
| `ADMIN` | Administrador con acceso total |

---

## Estructura del proyecto

```
tfg-backend/
├── core/               # Configuración Django (settings, urls, wsgi)
├── users/              # Modelo de usuario personalizado y autenticación
├── restaurants/        # Modelos Restaurant, Table, OpeningHours
├── reservations/       # Modelo Reservation y lógica de disponibilidad
├── manage.py
├── requirements.txt
└── README.md
```

---

## Despliegue en Render

El proyecto incluye `render.yaml` y `build.sh` para despliegue automático en Render.com.
Variables de entorno necesarias en producción: `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `DEBUG=False`.
