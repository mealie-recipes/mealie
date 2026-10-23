import asyncio
import os
import time
from pathlib import Path

from mealie.core import root_logger
from mealie.core.config import get_app_settings

try:
    import fcntl
except ImportError:  # pragma: py-not-win32
    # Windows has no fcntl; multi-worker startup coordination is unavailable there and
    # every worker behaves as if it were alone (the pre-existing behavior).
    fcntl = None  # type: ignore[assignment]

logger = root_logger.get_logger()

LEADER_LOCK_FILENAME = "startup.leader.lock"
READY_LOCK_FILENAME = "startup.ready.lock"

PUBLISH_READY_ATTEMPTS = 100
PUBLISH_READY_RETRY_SECONDS = 0.1


class ProcessFileLock:
    """
    An advisory, exclusive lock on a file, acquired with flock(2).

    The lock is tied to the open file description, so the kernel releases it when the
    owning process exits - even if it is killed outright. That is what makes this safe
    to use for electing a worker at startup: a worker that dies mid-migration cannot
    leave the lock behind and block everyone else.

    File locks work identically for SQLite and PostgreSQL setups because all uvicorn
    workers of a deployment share the same data directory.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self._fd: int | None = None

    @property
    def is_acquired(self) -> bool:
        return self._fd is not None

    def try_acquire(self) -> bool:
        """Try to take the lock without blocking; return False if another process holds it."""
        if fcntl is None:  # pragma: py-not-win32
            # No real lock is possible; report success so callers proceed as a lone process.
            return True

        if self._fd is not None:
            raise RuntimeError(f"Lock is already held by this process: {self.path}")

        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.path, os.O_CREAT | os.O_RDWR, 0o644)

        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(fd)
            return False

        self._fd = fd
        return True

    def release(self) -> None:
        if self._fd is None:
            return

        fcntl.flock(self._fd, fcntl.LOCK_UN)
        os.close(self._fd)
        self._fd = None


class WorkerStartupCoordinator:
    """
    Elects a single worker process to run one-time startup duties when multiple uvicorn
    workers are configured (`UVICORN_WORKERS` / `WORKER_PER_CORE` > 1).

    Every uvicorn worker is a separate process that runs the full application lifespan,
    so without coordination each worker would run `alembic upgrade head` and the initial
    database seed concurrently, and each would start its own copy of the background
    scheduler - firing scheduled tasks and webhooks once per worker.

    Two lock files in the data directory coordinate the workers:

    - `startup.leader.lock`: grabbed without blocking at startup. The first worker to
      get it becomes the leader and keeps the lock for its whole process lifetime, which
      both guarantees migrations/seeding run exactly once and marks the worker that must
      own the scheduler.
    - `startup.ready.lock`: taken by the leader once database initialization has fully
      finished. Every other worker waits for it before serving traffic, so no worker
      answers requests against a half-migrated or half-seeded database.

    If the leader dies before it is ready, the kernel releases its locks and the next
    worker takes over as leader and retries initialization. With a single worker, the
    lock is uncontended and startup behaves exactly as before.
    """

    def __init__(self, data_dir: Path, poll_interval: float = 0.5) -> None:
        self._leader_lock = ProcessFileLock(data_dir / LEADER_LOCK_FILENAME)
        self._ready_lock = ProcessFileLock(data_dir / READY_LOCK_FILENAME)
        self._poll_interval = poll_interval

    async def elect(self) -> bool:
        """
        Block until this process's startup role is decided.

        Returns True if this process is the leader and must run database initialization
        and the scheduler; returns False once another worker has finished
        initialization, meaning this process should serve traffic without the scheduler.
        """
        if fcntl is None:  # pragma: py-not-win32
            if get_app_settings().WORKERS > 1:
                logger.warning(
                    "File locks are not available on this platform; startup duties cannot be "
                    "limited to a single worker and will run in every worker"
                )
            return True

        while True:
            if self._leader_lock.try_acquire():
                self._write_leader_pid()
                logger.info(f"Worker (pid {os.getpid()}) elected startup leader")
                return True

            # Another worker is the leader; wait for it to publish readiness. Probing
            # acquires the lock momentarily only to test it, so release it immediately.
            if self._ready_lock.try_acquire():
                self._ready_lock.release()
                await asyncio.sleep(self._poll_interval)
                continue

            leader_pid = self._read_leader_pid()
            logger.info(
                f"Worker (pid {os.getpid()}) following startup leader (pid {leader_pid}); "
                "skipping database initialization and scheduler"
            )
            return False

    def publish_ready(self) -> None:
        """
        Signal waiting workers that database initialization has completed.

        The lock is kept until the process exits, both to avoid flapping readiness and
        because its holder - the leader - is the worker that owns the scheduler.
        """
        # A readiness probe by another worker may briefly hold the lock, so retry a few
        # times instead of giving up on the first try.
        for _ in range(PUBLISH_READY_ATTEMPTS):
            if self._ready_lock.try_acquire():
                return
            time.sleep(PUBLISH_READY_RETRY_SECONDS)

        raise RuntimeError(f"Failed to acquire startup readiness lock: {self._ready_lock.path}")

    def _write_leader_pid(self) -> None:
        try:
            with open(self._leader_lock.path, "w") as f:
                f.write(str(os.getpid()))
        except OSError:
            logger.debug(f"Could not write leader pid to {self._leader_lock.path}")

    def _read_leader_pid(self) -> str | None:
        try:
            return self._leader_lock.path.read_text().strip() or None
        except OSError:
            return None
