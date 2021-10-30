# https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/2daa3e3873c837d5781feb4ff6a40a89f791f81b/docker-images/gunicorn_conf.py

import json
import multiprocessing
import os


class GunicornConfig:
    """Configuration to generate the properties for Gunicorn"""

    def __init__(self):

        # Env Variables
        self.host = os.getenv("HOST", "127.0.0.1")
        self.port = os.getenv("PORT", "80")
        self.log_level: str = os.getenv("LOG_LEVEL", "info")
        self.bind: str = os.getenv("BIND", None)
        self.errorlog: str = os.getenv("ERROR_LOG", "-") or None
        self.accesslog: str = os.getenv("ACCESS_LOG", "-") or None
        self.graceful_timeout: int = int(os.getenv("GRACEFUL_TIMEOUT", "120"))
        self.timeout = int(os.getenv("TIMEOUT", "120"))
        self.keepalive = int(os.getenv("KEEP_ALIVE", "5"))
        self.workers_per_core = float(os.getenv("WORKERS_PER_CORE", "1"))
        self.web_concurrency_str: str = os.getenv("WEB_CONCURRENCY", "1")
        self.max_workers_str: str = os.getenv("MAX_WORKERS", "1")

        # Computed Variables
        self.cores = multiprocessing.cpu_count()
        self.default_bind = f"{self.host}:{self.port}"
        self.default_web_concorrency = self.workers_per_core * self.cores
        self.workers = self.get_workers()

    def get_workers(self) -> int:
        if self.web_concurrency_str:
            web_concurrency = int(self.web_concurrency_str)
            assert web_concurrency > 0
        else:
            web_concurrency = max(int(self.default_web_concorrency), 2)
            if self.max_workers_str:
                web_concurrency = min(web_concurrency, int(self.max_workers_str))

        return web_concurrency


gunicorn_conf = GunicornConfig()

# Gunicorn config variables
loglevel = gunicorn_conf.log_level
workers = gunicorn_conf.workers
bind = gunicorn_conf.bind or gunicorn_conf.default_bind
errorlog = gunicorn_conf.errorlog
accesslog = gunicorn_conf.accesslog
graceful_timeout = gunicorn_conf.graceful_timeout
timeout = gunicorn_conf.timeout
keepalive = gunicorn_conf.keepalive


# For debugging and testing
log_data = {
    "loglevel": loglevel,
    "workers": workers,
    "bind": bind,
    "graceful_timeout": graceful_timeout,
    "timeout": timeout,
    "keepalive": keepalive,
    "errorlog": errorlog,
    "accesslog": accesslog,
    # Additional, non-gunicorn variables
    "workers_per_core": gunicorn_conf.workers_per_core,
    "use_max_workers": gunicorn_conf.max_workers_str,
    "host": gunicorn_conf.host,
    "port": gunicorn_conf.port,
}

print("---- Gunicorn Configuration ----", json.dumps(log_data, indent=4))
