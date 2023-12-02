import asyncio
import uuid
from dataclasses import asdict
from typing import Any

import dramatiq
from scrapy.crawler import CrawlerProcess
from sqlalchemy.orm import Session

from common import constants
from common.tables import ProviderTable, GymTable
from scraper.db import engine
from scraper.services import ScrapJobService, SpiderDataConnector
from scraper.spiders import ZdrofitGymSpider
import scrapy
import scrapy.crawler as crawler
from scrapy.utils.log import configure_logging
from multiprocessing import Process, Queue
from twisted.internet import reactor


xxx = {
    "SPIDER_MIDDLEWARES": {"scraper.spiders.middlewares.CrawlerSpiderMiddleware": 543},
}


def process_data(data: Any) -> None:
    data = data["gyms"]

    with Session(engine) as session:
        zdrofit_provider = (
            session.query(ProviderTable).filter_by(name="zdrofit").first()
        )
        if not zdrofit_provider:
            zdrofit_provider = ProviderTable(id=str(uuid.uuid4()), name="zdrofit")
            session.add(zdrofit_provider)

            existing_gym_names = session.query(GymTable.name).filter(
                GymTable.provider == zdrofit_provider
            )
            new_gyms = [d for d in data if d.name not in existing_gym_names]
            session.add_all(
                [
                    GymTable(
                        is_active=True,
                        provider_id=zdrofit_provider.id,
                        **{k: v for k, v in asdict(d).items() if k != "provider"},
                    )
                    for d in new_gyms
                ]
            )
            not_active_gyms = (
                session.query(GymTable)
                .populate_existing()
                .with_for_update()
                .filter(GymTable.name.not_in([d.name for d in new_gyms]))
            )
            for not_active_gym in not_active_gyms:
                not_active_gym.is_active = False

            session.add_all(not_active_gyms)

        session.commit()


async def run(*methods):
    results = await asyncio.gather(*[m() for m in methods])

    return results


def run_spider(spider, **kwargs):
    def f(q):
        try:
            runner = crawler.CrawlerRunner(settings=xxx)
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


@dramatiq.actor
def get_zdrofit_gyms():
    print("start get_zdrofit_gyms")  # TODO move to logger

    service = ScrapJobService.create_new(spider_name="zdrofit_gym")
    connector = SpiderDataConnector(
        spider_name="zdrofit_gym", job_id=service.scrap_job.id
    )

    status = constants.ScrapJobStatus.RUNNING

    run_spider(
        spider=ZdrofitGymSpider,
        job_id=service.scrap_job.id,
        start_url="https://zdrofit.pl/grafik-zajec",
    )

    service.update_status(status=status)

    datas = asyncio.run(run(connector.fetch_data))

    process_data(data=datas[0])
