import os

# TODO move to global settings and envs
REDIS_HOST = "redis"
REDIS_PORT = 6379
# TODO move to global settings and envs
CRAWLER_HOST = "crawler"
CRAWLER_PORT = 6800
# TODO move to global settings and envs
MONGO_HOST = "mongo"
MONGO_PORT = 27017
MONGO_DATABASE = "mongo"

SCHEDULE_CONFIG_PATH = "/app/scraper/schedule.yml"

PROXY_SERVER = os.getenv("PROXY_SERVER")
PROXY_USERNAME = os.getenv("PROXY_USERNAME")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")

