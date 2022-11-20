import redis
from aiogram import Bot, Dispatcher
from redis import Redis
from rq import Queue

from core import config

bot = Bot(config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

users_db = redis.StrictRedis(host='localhost', port=6379, db=1)

queue = Queue(connection=Redis.from_url(config.REDIS_URL), name="high") if config.REDIS_URL else None
