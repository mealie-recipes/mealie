import time
from typing import Any


class AuthCache:
    def __init__(self, threshold: int = 500, default_timeout: float = 300):
        self.default_timeout = default_timeout
        self._cache: dict[str, tuple[float, Any]] = {}
        self.clear = self._cache.clear
        self._threshold = threshold

    def _prune(self):
        if len(self._cache) > self._threshold:
            now = time.time()
            toremove = []
            for idx, (key, (expires, _)) in enumerate(self._cache.items()):
                if (expires != 0 and expires <= now) or idx % 3 == 0:
                    toremove.append(key)
            for key in toremove:
                self._cache.pop(key, None)

    def _normalize_timeout(self, timeout: float | None) -> float:
        if timeout is None:
            timeout = self.default_timeout
        if timeout > 0:
            timeout = time.time() + timeout
        return timeout

    async def get(self, key: str) -> Any:
        try:
            expires, value = self._cache[key]
            if expires == 0 or expires > time.time():
                return value
        except KeyError:
            return None

    async def set(self, key: str, value: Any, timeout: float | None = None) -> bool:
        expires = self._normalize_timeout(timeout)
        self._prune()
        self._cache[key] = (expires, value)
        return True

    async def delete(self, key: str) -> bool:
        return self._cache.pop(key, None) is not None

    async def has(self, key: str) -> bool:
        try:
            expires, value = self._cache[key]
            return expires == 0 or expires > time.time()
        except KeyError:
            return False
