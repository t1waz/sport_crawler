import uuid
from dataclasses import asdict

from sqlalchemy.orm import Session

from common import constants
from common.tables import ProviderTable, GymTable
from scraper.db import engine
from scraper.exceptions import (
    SpiderNotFinished,
    SpiderNetworkException,
    SpiderTimeoutException,
    SpiderParseDataException,
)
from scraper.services import ScrapJobService, SpiderConnector

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
        return

    try:
        data = spider_connector.fetch_data()
        status = constants.ScrapJobStatus.FINISH
    except SpiderNotFinished:
        data = None
        status = constants.ScrapJobStatus.SPIDER_NOT_FINISHED

    job_service.update_status(status=status, is_finished=True)

    if data:
        gym_data = data["gyms"]

        with Session(engine) as session:
            zdrofit_provider = session.query(ProviderTable).filter_by(name="zdrofit").first()
            if not zdrofit_provider:
                zdrofit_provider = ProviderTable(id=str(uuid.uuid4()), name="zdrofit")
                session.add(zdrofit_provider)

                existing_gym_names = session.query(GymTable.name).filter(GymTable.provider == zdrofit_provider)
                new_gyms = [d for d in gym_data if d.name not in existing_gym_names]
                session.add_all([
                    GymTable(is_active=True, provider_id=zdrofit_provider.id, **{k: v for k, v in asdict(d).items() if k != "provider"}) for d in new_gyms
                ])
                not_active_gyms = session.query(GymTable).populate_existing().with_for_update().filter(GymTable.name.not_in([d.name for d in new_gyms]))
                for not_active_gym in not_active_gyms:
                    not_active_gym.is_active = False

                session.add_all(not_active_gyms)

            session.commit()
