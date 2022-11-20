from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from main import dp
from utils.helpers import delete_message_markup
from . import admin
from . import my_profile
from . import start
from .uzbekvoice import check_voice
from .uzbekvoice import record_voice


# default handler
@dp.message_handler(state='*')
async def not_found_command(message: Message, state: FSMContext):
    await start.start_command(message, state)


@dp.callback_query_handler(state="*")
async def not_found_button(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
    except:
        pass
    await delete_message_markup(call.message.chat.id, call.message.message_id)
    await start.start_command(call.message, state)
