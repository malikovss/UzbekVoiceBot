from aiogram.types import Message

from admin.block_certain import block_certain_func
from admin.get_bot_stat import get_bot_stat_func
from admin.send_certain import send_certain_func
from admin.send_everyone import send_everyone_func
from admin.unblock_certain import unblock_certain_func
from core import config
from data.messages import SEND_EVERYONE, BOT_STATISTICS, SEND_CERTAIN, BLOCK_CERTAIN, UNBLOCK_CERTAIN
from keyboards.buttons import admin_markup
from main import dp


# Answer to /admin command to get list of admin commands
@dp.message_handler(chat_id=config.ADMINS_ID, commands=['admin'])
async def ask_admin_commands(message: Message):
    await message.answer('All admin commands:', reply_markup=admin_markup)


# Answer to all admin commands
@dp.message_handler(chat_id=config.ADMINS_ID,
                    text=[SEND_EVERYONE, BOT_STATISTICS, SEND_CERTAIN, BLOCK_CERTAIN, UNBLOCK_CERTAIN])
async def admin_commands(message: Message):
    chat_id = message.chat.id
    _functions = {
        SEND_EVERYONE: send_everyone_func(chat_id),
        SEND_CERTAIN: send_certain_func(chat_id),
        BLOCK_CERTAIN: block_certain_func(chat_id),
        UNBLOCK_CERTAIN: unblock_certain_func(chat_id),
        BOT_STATISTICS: get_bot_stat_func(chat_id),
    }
    await _functions[message.text]
