from scrapy.crawler import CrawlerProcess

from crawler.spiders.zdrofit_class import ZdrofitClassSpider
from crawler import settings


settings = {
    "SPIDER_MIDDLEWARES": settings.SPIDER_MIDDLEWARES,
}

process = CrawlerProcess(settings=settings)
process.crawl(
    ZdrofitClassSpider,
    start_url="https://zdrofit.pl/kluby-fitness/bialystok-wroclawska/grafik-zajec",
    job_id="1",
)
process.crawl(
    ZdrofitClassSpider,
    start_url="https://zdrofit.pl/kluby-fitness/czestochowa-piastowska/grafik-zajec",
    job_id="2",
)
process.crawl(
    ZdrofitClassSpider,
    start_url="https://zdrofit.pl/kluby-fitness/gdansk-alchemia/grafik-zajec",
    job_id="3",
)
process.start()
