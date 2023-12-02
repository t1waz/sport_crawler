import pickle
from typing import Any

from redis import Redis


class RedisStore:
    STORE_EXPIRE = 3600

    def __init__(self, conn: Redis) -> None:
        self._conn = conn

    def store(self, key: str, data: Any) -> None:
        self._conn.set(name=key, value=pickle.dumps(data), ex=self.STORE_EXPIRE)

    def retrieve(self, key: str) -> Any:
        data = self._conn.get(name=key)
        if data:
            self._conn.delete(key)
            return pickle.loads(data)

        return None
