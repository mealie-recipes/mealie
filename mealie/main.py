import uvicorn

from mealie.app import settings
from mealie.core.logger.config import log_config


def main():
    uvicorn.run(
        "mealie.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level=settings.LOG_LEVEL.lower(),
        log_config=log_config(),
        workers=settings.WORKERS,
        forwarded_allow_ips=settings.HOST_IP,
        ssl_keyfile=settings.TLS_PRIVATE_KEY_PATH,
        ssl_certfile=settings.TLS_CERTIFICATE_PATH,
    )


if __name__ == "__main__":
    main()
