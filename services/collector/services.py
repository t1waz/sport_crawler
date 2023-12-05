from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

from playwright.async_api import async_playwright
from redis.asyncio import Redis
import pickle


class StreamMaster:
    def __init__(self, client: Redis, stream_key: str) -> None:
        self._client = client
        self._stream_key = stream_key

    def get_data(self, data: dict) -> Any:
        msg_id = str(uuid.uuid4())

        self._client.xadd(name=self._stream_key, fields={"id": msg_id, **data})

        x = 0
        data = None
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
            groupname=self._group_name,
            consumername=self.id,
            streams={self._stream_key: ">"},
            noack=True,
        )
        if data:
            raw_data = data[0][1][0][1]
            return {k.decode(): v.decode() for k, v in raw_data.items()}

        return None

    async def send(self, id: str, data: Any) -> None:
        await self._client.set(name=id.strip(), value=pickle.dumps(data))

    @property
    def id(self):
        return self._id


class WebsiteDataCollector:
    def __init__(self, stream_worker: StreamWorker) -> None:
        self._page = None
        self._browser = None
        self._id = str(uuid.uuid4())
        self._stream_worker = stream_worker

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

    async def main(self) -> None:
        data = await self._stream_worker.consume()
        if data:
            await self._page.goto(data["url"])
            content = await self._page.content()
            await self._stream_worker.send(id=data["id"], data={"content": content})

    async def run(self) -> None:
        async with async_playwright() as playwright:
            chromium = playwright.chromium
            self._browser = await chromium.launch()
            self._page = await self._browser.new_page()

            while True:
                await self.main()
                await asyncio.sleep(0.5)

    @property
    def browser(self):
        return self._browser

    @property
    def id(self):
        return self._id
