"""Default Django REST Framework ASGI application."""

import os
import re
import warnings

warnings.filterwarnings(
    "ignore", module=".*pyRdfa", category=SyntaxWarning, message=re.escape("invalid escape sequence '\\-'")
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mealie.http.settings")

from django.core.asgi import get_asgi_application  # noqa: E402

from mealie.core.config import get_app_settings  # noqa: E402
from mealie.http.api import APIRouter  # noqa: E402
from mealie.http.lifecycle import DjangoApplication, lifespan_fn, start_scheduler  # noqa: E402 F401
from mealie.routes import router, spa, utility_routes  # noqa: E402
from mealie.routes.media import media_router  # noqa: E402

settings = get_app_settings()
registry = APIRouter()
registry.include_router(router)
registry.include_router(media_router)
registry.include_router(utility_routes.router)
if settings.PRODUCTION and not settings.TESTING:
    spa.mount_spa(registry)

app = DjangoApplication(get_asgi_application(), registry)


def main() -> None:
    import uvicorn

    uvicorn.run(
        "mealie.http.asgi:application",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=True,
        reload_dirs=["mealie"],
        reload_delay=2,
        log_level="info",
        use_colors=True,
        log_config=None,
        workers=1,
        forwarded_allow_ips="*",
        ws="websockets-sansio",
    )


if __name__ == "__main__":
    main()
