import logging

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.filters import Filter
from aiogram.types import Message, ReplyKeyboardRemove

from core import config
from db import shortcuts
from keyboards.buttons import register_markup
from utils import helpers

logger = logging.getLogger(__name__)


# Filter for checking registration of user
class IsRegistered(Filter):
    key = "is_registered"

    async def check(self, message: Message):

        chat_id = message.chat.id
        if shortcuts.user_exists(chat_id):
            return True
        else:
            await helpers.send_message(chat_id, 'register', markup=register_markup)


# Filter for checking whether user is a member of the channel
class IsSubscribedChannel(Filter):
    key = "is_subscribed_channel"

    async def check(self, message: Message):
        bot = Bot.get_current()
        try:
            if config.JOIN_CHANNEL_ID is None:
                return True
            chat_id = message.chat.id
            check_member = await bot.get_chat_member(config.JOIN_CHANNEL_ID, chat_id)
            if check_member.status not in ["member", "creator", "administrator"]:
                await helpers.send_message(chat_id, 'channel')
                return False
            else:
                return True
        except Exception as err:
            logger.error('Error in IsSubscribedChannel', err)
            return True


# Filter for checking whether user is banned
class IsBlockedUser(Filter):
    key = "is_blocked_user"

    async def check(self, message: Message):
        chat_id = message.chat.id
        if shortcuts.user_banned(chat_id):
            await helpers.send_message(chat_id, 'banned', markup=ReplyKeyboardRemove())
            return False
        else:
            return True


def register_filters(dp: Dispatcher):
    _filters = [
        IsBlockedUser,
        IsSubscribedChannel,
        IsRegistered
    ]
    for _filter in _filters:
        dp.bind_filter(_filter())
