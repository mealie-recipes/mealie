from mealie.core.config import get_app_settings

mealie_settings = get_app_settings()

SECRET_KEY = mealie_settings.SESSION_SECRET
DEBUG = False

# Local pilot only; extend explicitly when deploying.
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", "testserver"]

INSTALLED_APPS = ["rest_framework"]
MIDDLEWARE = []

ROOT_URLCONF = "mealie.drf_api.urls"
ASGI_APPLICATION = "mealie.drf_api.asgi.application"

# Mealie continues using SQLAlchemy and Alembic.
DATABASES = {}

USE_TZ = True
TIME_ZONE = "UTC"
APPEND_SLASH = False

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "UNAUTHENTICATED_USER": None,
}
