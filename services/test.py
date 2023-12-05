import asyncio
import atexit
import uuid

from playwright.async_api import async_playwright

COLLECTORS = []


def close_collectors():
    async def _close():
        for collector in COLLECTORS:
            await collector.browser.close()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_close())


atexit.register(close_collectors)


class WebsiteDataCollector:
    def __init__(self):
        self._page = None
        self._browser = None
        self._id = str(uuid.uuid4())

    async def main(self):
        await self._page.goto("http://google.com")

        content = await self._page.content()
        print("get data: ", content, " id: ", self.id)
        await asyncio.sleep(0.5)

    async def run(self):
        async with async_playwright() as playwright:
            chromium = playwright.chromium
            self._browser = await chromium.launch()
            self._page = await self._browser.new_page()

            while True:
                await self.main()

    @property
    def browser(self):
        return self._browser

    @property
    def id(self):
        return self._id


if __name__ == "__main__":
    COLLECTORS = [WebsiteDataCollector() for _ in range(10)]
    loop = asyncio.get_event_loop()
    for collector in COLLECTORS:
        loop.create_task(collector.run())
    loop.run_forever()
    print("running")
