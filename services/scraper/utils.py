import asyncio
from multiprocessing import Process, Queue

import scrapy.crawler as crawler
from twisted.internet import reactor


async def run_parallel(*methods):
    results = await asyncio.gather(*[m() for m in methods])

    return results


def run_spider(spider, **kwargs):
    run_spider_settings = {
        "SPIDER_MIDDLEWARES": {
            "scraper.spiders.middlewares.CrawlerSpiderMiddleware": 543
        },
    }

    def f(q):
        try:
            runner = crawler.CrawlerRunner(settings=run_spider_settings)
            deferred = runner.crawl(spider, **kwargs)
            deferred.addBoth(lambda _: reactor.stop())
            reactor.run()
            q.put(None)
        except Exception as e:
            q.put(e)

    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result
