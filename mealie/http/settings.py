"""Django hosts HTTP only. SQLAlchemy and Alembic own all application data."""

from mealie.core.config import get_app_settings

MEALIE = get_app_settings()
SECRET_KEY = MEALIE.SESSION_SECRET
DEBUG = False
ALLOWED_HOSTS = ["*"]
ROOT_URLCONF = "mealie.http.urls"
INSTALLED_APPS = ["rest_framework"]
DATABASES: dict[str, object] = {}
USE_TZ = True
TIME_ZONE = "UTC"
APPEND_SLASH = False
DEFAULT_CHARSET = "utf-8"
DATA_UPLOAD_MAX_MEMORY_SIZE = None
DATA_UPLOAD_MAX_NUMBER_FIELDS = None
DATA_UPLOAD_MAX_NUMBER_FILES = None
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024
MIDDLEWARE = [
    "mealie.http.middleware.CORSMiddleware",
    "mealie.http.middleware.MealieGZipMiddleware",
    "mealie.http.middleware.SignedSessionMiddleware",
    "mealie.middleware.locale_context.LocaleContextMiddleware",
]
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
    "UNAUTHENTICATED_USER": None,
    "UNAUTHENTICATED_TOKEN": None,
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": [
        "mealie.http.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "mealie.http.parsers.MultiPartParser",
        "mealie.http.parsers.RawParser",
    ],
    "DEFAULT_CONTENT_NEGOTIATION_CLASS": "mealie.http.negotiation.MealieContentNegotiation",
}
LOGGING_CONFIG = None
