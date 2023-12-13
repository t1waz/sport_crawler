from __future__ import annotations

import asyncio
import pickle
import time
import uuid
from typing import Any
from typing import Optional

from playwright.async_api import async_playwright
from redis.asyncio import Redis
import random
import datetime
import logging


# Configure logging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
]


class StreamMaster:
    def __init__(self, client: Redis, stream_key: str) -> None:
        self._client = client
        self._stream_key = stream_key

    def get_data(self, data: dict, id: Optional[str] = None) -> Any:
        msg_id = id or str(uuid.uuid4())

        self._client.xadd(name=self._stream_key, fields={"id": msg_id, **data})

        x = 0
        data = None
        time.sleep(1)
        while x < 100:
            data = self._client.get(name=msg_id)
            if data:
                data = pickle.loads(data)
                break

            x += 1
            time.sleep(0.1)

        return data


class StreamWorker:
    def __init__(self, client: Redis, stream_key: str, group_name: str) -> None:
        self._client = client
        self._id = str(uuid.uuid4())
        self._group_name = group_name
        self._stream_key = stream_key

    async def consume(self) -> Any:
        data = await self._client.xreadgroup(
            count=1,  # WTF spend so many hours
            noack=True,
            consumername=self.id,
            groupname=self._group_name,
            streams={self._stream_key: ">"},
        )
        if data:
            msg_id = data[0][1][0][0]
            await self._client.xdel(self._stream_key, msg_id.decode())
            raw_data = data[0][1][0][1]
            return {k.decode(): v.decode() for k, v in raw_data.items()}

        return None

    async def send(self, id: str, data: Any) -> None:
        await self._client.set(name=id.strip(), value=pickle.dumps(data))

    @property
    def id(self):
        return self._id


class WebsiteDataCollector:
    BROWSER_RESTART_PERIOD = 15 * 60  # seconds

    def __init__(self, stream_worker: StreamWorker) -> None:
        self._p = None
        self._id = str(uuid.uuid4())
        self._stream_worker = stream_worker
        self._restart_timestamp = datetime.datetime.now()

    @classmethod
    def create(
        cls, group_name: str, stream_key: str, redis_host: str, redis_port: int
    ) -> WebsiteDataCollector:
        return cls(
            stream_worker=StreamWorker(
                group_name=group_name,
                stream_key=stream_key,
                client=Redis(host=redis_host, port=redis_port),
            )
        )

    async def main(self, data: dict) -> None:
        async with async_playwright() as playwright:
            chromium = playwright.chromium
            browser = await chromium.launch()
            context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
            page = await context.new_page()
            await page.evaluate(
                "() => Object.defineProperty("
                "navigator, 'webdriver', {get: () => undefined})"
            )

            await page.goto(data["url"])
            content = await page.content()
            await self._stream_worker.send(id=data["id"], data={"content": content})

            await page.close()
            await context.close()
            await browser.close()

    async def run(self) -> None:
        logger.info(f"collector id: {self.id} started")
        try:
            while True:
                data = await self._stream_worker.consume()
                if data:
                    await self.main(data=data)
                    await asyncio.sleep(0.25)
        except Exception as exc:
            logger.error(f"Exception encountered: {exc}")
            pass

    @property
    def browser(self):
        return self._browser

    @property
    def id(self):
        return self._id
