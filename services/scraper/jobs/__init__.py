import dramatiq
from dramatiq.brokers.redis import RedisBroker


redis_broker = RedisBroker(url="redis://redis:6379/0")  # TODO move to settings
dramatiq.set_broker(redis_broker)


from .get_zdrofit_gyms import *
from .get_zdrofit_classes import *
from .get_zdrofit_class import *
