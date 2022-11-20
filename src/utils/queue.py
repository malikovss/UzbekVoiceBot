import logging

from rq import Retry

from main import queue
from .helpers import authorization_token
from .uzbekvoice.common_voice import common_voice

logger = logging.getLogger(__name__)


async def enqueue_operation(operation, chat_id):
    # if queue is not open
    token = await authorization_token(chat_id)
    if queue is None:
        logger.info('Queue is not open')
        return await common_voice.handle_operation(
            token,
            operation,
        )
    else:
        queue.enqueue(
            common_voice.handle_operation,
            operation,
            retry=Retry(max=100, interval=30)
        )
