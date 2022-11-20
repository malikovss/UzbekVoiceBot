import logging
import os

from aiogram.utils import executor

import handlers  # noqa
from main import dp, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from utils.helpers import on_startup, on_shutdown

if __name__ == '__main__':
    logging.basicConfig(
        format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
        level=logging.DEBUG
    )
    logger = logging.getLogger(__name__)

    if os.getenv('WEBHOOK_HOST') is not None:
        logger.info('RUNNING WEBHOOK')
        executor.start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )
    else:
        logger.info('RUNNING POLLING')
        executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
