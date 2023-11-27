from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.routing import Mount
from piccolo.apps.user.tables import BaseUser
from piccolo.engine import engine_finder
from piccolo.table import create_db_tables
from piccolo_admin.endpoints import create_admin
from piccolo_api.session_auth.tables import SessionsBase

from common.tables import Gym, GymClass, GymClassBook, Provider


TABLES = [Gym, GymClass, GymClassBook, BaseUser, SessionsBase, Provider]


@asynccontextmanager
async def lifespan(_: FastAPI):
    engine = engine_finder()
    await engine.start_connnection_pool()
    await create_db_tables(*TABLES, if_not_exists=True)

    yield

    await engine.close_connnection_pool()


app = FastAPI(
    lifespan=lifespan,
    routes=[
        Mount(
            path="/admin/",
            app=create_admin(
                tables=TABLES,
                auth_table=BaseUser,
                session_table=SessionsBase,
                site_name="Sport Spotter Admin",
            ),
        ),
    ],
)
