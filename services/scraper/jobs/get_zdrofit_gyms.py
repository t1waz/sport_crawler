from common import constants
from scraper.services import ScrapJobService, SpiderConnector
from scraper.exceptions import (
    SpiderNotFinished,
    SpiderNetworkException,
    SpiderTimeoutException,
    SpiderParseDataException,
)


SPIDER_NAME = "zdrofit_gym"


def get_zdrofit_gyms():
    print("start get_zdrofit_gyms job")  # TODO: logger
    spider_connector = SpiderConnector(spider_name=SPIDER_NAME)
    job_service = ScrapJobService.create_new(spider_name=SPIDER_NAME)

    status = constants.ScrapJobStatus.RUNNING
    try:
        spider_connector.trigger_spider(
            job_id=job_service.scrap_job.id, start_url="https://zdrofit.pl/grafik-zajec"
        )
    except SpiderNetworkException:
        status = constants.ScrapJobStatus.NETWORK_ERROR
    except SpiderNotFinished:
        status = constants.ScrapJobStatus.SPIDER_NOT_FINISHED
    except SpiderTimeoutException:
        status = constants.ScrapJobStatus.NETWORK_ERROR
    except SpiderParseDataException:
        status = constants.ScrapJobStatus.CONTENT_ERROR

    if status != constants.ScrapJobStatus.RUNNING:
        is_finished = True
    else:
        is_finished = False

    if is_finished:
        job_service.update_status(status=status, is_finished=is_finished)

    data = spider_connector.fetch_data()
    job_service.update_status(status=constants.ScrapJobStatus.FINISH, is_finished=True)

    print(data, "DATA !!!!")
