from functools import lru_cache

from redis import Redis

from common.redis import RedisStore
from scraper import settings


@lru_cache
def get_redis_store() -> RedisStore:
    return RedisStore(conn=Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT))


redis_store = get_redis_store()
