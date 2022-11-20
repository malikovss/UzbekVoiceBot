from os import getenv
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
BASE_DIR: Path = Path(__file__).resolve().parent.parent

WEBHOOK_HOST = getenv('WEBHOOK_HOST')
WEBHOOK_PATH = '/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = '0.0.0.0'  # or ip
WEBAPP_PORT = 80

ADMINS_ID: list = list(map(int, getenv("ADMINS_ID").split()))

REDIS_URL = getenv("REDIS_URL")
DATABASE_URL = getenv("DATABASE_URL")
BOT_TOKEN = getenv("BOT_TOKEN")
JOIN_CHANNEL_ID = getenv("JOIN_CHANNEL_ID")
