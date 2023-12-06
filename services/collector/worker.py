import asyncio
import atexit
import uuid

from redis.asyncio import Redis

from collector import settings
from collector.services import WebsiteDataCollector


GROUP_NAME = "test"
STREAM_KEY = "input_collector"
COLLECTORS = []


def close_collectors():
    async def _close():
        for c in COLLECTORS:
            await c.browser.close()

    lp = asyncio.get_event_loop()
    lp.run_until_complete(_close())


atexit.register(close_collectors)


async def create_group(redis_conn: Redis, name: str, stream_key: str) -> None:
    try:
        await redis_conn.xgroup_create(
            name=stream_key, groupname=name, id=0, mkstream=True
        )
    except Exception as _:  # noqa
        pass


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    redis_conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

    loop.run_until_complete(
        create_group(redis_conn=redis_conn, name=GROUP_NAME, stream_key=STREAM_KEY)
    )

    COLLECTORS = [
        WebsiteDataCollector.create(
            group_name=GROUP_NAME,
            stream_key=STREAM_KEY,
            redis_host=settings.REDIS_HOST,
            redis_port=settings.REDIS_PORT,
        )
        for _ in range(10)
    ]

    for collector in COLLECTORS:
        loop.create_task(collector.run())

    print("worker started")  # TODO: logger
    loop.run_forever()
