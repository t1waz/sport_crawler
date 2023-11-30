from functools import lru_cache

from sqlalchemy import create_engine


@lru_cache
def get_engine():
    return create_engine("postgresql+psycopg2://postgres:postgres@db:5432/postgres")


engine = get_engine()
