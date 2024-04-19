import uvicorn

from mealie.app import settings
from mealie.core.logger.config import log_config


def main():
    uvicorn.run(
        "app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level=settings.LOG_LEVEL.lower(),
        log_config=log_config(),
        workers=1,
        forwarded_allow_ips=settings.HOST_IP,
    )


if __name__ == "__main__":
    main()
