import asyncio
import os
import sys
from multiprocessing import Event, Process, Queue
from pathlib import Path

import pytest

from mealie.core.startup_coordinator import (
    LEADER_LOCK_FILENAME,
    READY_LOCK_FILENAME,
    ProcessFileLock,
    WorkerStartupCoordinator,
)

pytestmark = pytest.mark.skipif(sys.platform != "linux", reason="worker file locks require fcntl")


def test_try_acquire_is_exclusive(tmp_path: Path):
    lock = ProcessFileLock(tmp_path / "test.lock")

    assert lock.try_acquire() is True

    # A second lock object on the same file must not be able to take it, whether it
    # represents another thread of the same process or another process entirely.
    contender = ProcessFileLock(tmp_path / "test.lock")
    assert contender.try_acquire() is False

    lock.release()
    assert contender.try_acquire() is True


@pytest.mark.asyncio
async def test_elect_elects_one_leader_and_gates_followers_on_ready(tmp_path: Path):
    leader = WorkerStartupCoordinator(tmp_path, poll_interval=0.01)
    follower = WorkerStartupCoordinator(tmp_path, poll_interval=0.01)

    assert await leader.elect() is True
    assert (tmp_path / LEADER_LOCK_FILENAME).read_text() == str(os.getpid())

    # The follower cannot finish election while the leader is initializing (the ready
    # lock is not published yet).
    follower_election = asyncio.create_task(follower.elect())
    await asyncio.sleep(0.1)
    assert not follower_election.done()

    leader.publish_ready()

    assert await asyncio.wait_for(follower_election, timeout=2) is False


@pytest.mark.asyncio
async def test_elect_returns_immediately_when_leader_already_ready(tmp_path: Path):
    leader = WorkerStartupCoordinator(tmp_path, poll_interval=0.01)
    assert await leader.elect() is True
    leader.publish_ready()

    late_worker = WorkerStartupCoordinator(tmp_path, poll_interval=0.01)
    assert await late_worker.elect() is False


def _leader_process(lock_dir: str, elected: Queue, die_now: Event, publish_ready: bool) -> None:
    coordinator = WorkerStartupCoordinator(Path(lock_dir), poll_interval=0.01)
    assert asyncio.run(coordinator.elect()) is True
    if publish_ready:
        coordinator.publish_ready()
    elected.put(os.getpid())

    die_now.wait(10)
    # Exit abruptly without running cleanup, the way a killed worker would; the kernel
    # must release the held locks.
    os._exit(0)


@pytest.mark.parametrize("published_ready", [False, True])
def test_elect_takes_over_when_leader_dies(tmp_path: Path, published_ready: bool):
    lock_dir = str(tmp_path)
    elected: Queue = Queue()
    die_now: Event = Event()

    process = Process(target=_leader_process, args=(lock_dir, elected, die_now, published_ready))
    process.start()

    try:
        assert elected.get(timeout=10)

        # While the leader process is alive, another worker cannot take the leader lock.
        contender = ProcessFileLock(tmp_path / LEADER_LOCK_FILENAME)
        assert contender.try_acquire() is False
    finally:
        die_now.set()
        process.join(timeout=10)
        assert process.exitcode == 0

    replacement = WorkerStartupCoordinator(tmp_path, poll_interval=0.01)
    assert asyncio.run(replacement.elect()) is True


@pytest.mark.asyncio
async def test_ready_lock_is_held_after_publish_ready(tmp_path: Path):
    coordinator = WorkerStartupCoordinator(tmp_path, poll_interval=0.01)
    assert await coordinator.elect() is True

    # Another worker's readiness probe momentarily holds the ready lock, but the leader
    # must still end up publishing readiness.
    probe = ProcessFileLock(tmp_path / READY_LOCK_FILENAME)
    assert probe.try_acquire() is True
    probe.release()

    coordinator.publish_ready()
    assert probe.try_acquire() is False
