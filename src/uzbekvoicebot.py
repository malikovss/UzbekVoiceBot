import logging
import os

from aiogram.utils import executor
from aiogram.utils.exceptions import TelegramAPIError

import handlers  # noqa
from core import config
from filters.custom_filters import register_filters
from keyboards.buttons import start_markup
from main import dp

logging.basicConfig(
    format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)


async def on_startup(args):
    register_filters(dp)

    for user_id in config.ADMINS_ID:
        try:
            await dp.bot.send_message(user_id, "Bot ishga tushurildi", markup=start_markup)
        except TelegramAPIError as e:
            logger.error(e)

    if config.WEBHOOK_HOST is not None:
        await dp.bot.set_webhook(config.WEBHOOK_URL)


async def on_shutdown(args):
    pass


if __name__ == '__main__':

    if os.getenv('WEBHOOK_HOST') is not None:
        logger.info('RUNNING WEBHOOK')
        executor.start_webhook(
            dispatcher=dp,
            webhook_path=config.WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=config.WEBAPP_HOST,
            port=config.WEBAPP_PORT,
        )
    else:
        logger.info('RUNNING POLLING')
        executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
