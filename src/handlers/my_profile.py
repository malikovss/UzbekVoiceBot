from aiogram import types
from aiogram.dispatcher import FSMContext

from data import messages
from db import shortcuts
from filters.custom_filters import (
    IsRegistered,
    IsSubscribedChannel,
)
from filters.states import (
    EditProfile,
)
from keyboards.buttons import go_back_markup, start_markup
from keyboards.inline import (
    edit_accent_markup,
    edit_lang_markup,
    edit_profile_markup,
    edit_age_markup
)
from main import dp
from utils.helpers import (
    authorization_token,
    send_my_profile,
    delete_message_markup,
    send_message
)
from utils.uzbekvoice import common_voice


# Handler that answers to cancel callbacks
@dp.callback_query_handler(state=EditProfile.all_states, text=messages.GO_HOME_TEXT)
async def cancel_message_handler(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'reply_message_id' in data:
        reply_message_id = data['reply_message_id']
        await delete_message_markup(call.from_user.id, reply_message_id)
    await send_message(call.from_user.id, 'action-rejected', markup=start_markup)
    await state.finish()


@dp.message_handler(IsRegistered(), IsSubscribedChannel(), text=messages.MY_PROFILE)
async def my_profile(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if 'reply_message_id' in data:
        reply_message_id = data['reply_message_id']
        await delete_message_markup(message.from_user.id, reply_message_id)
    await send_my_profile(message.from_user.id)


@dp.callback_query_handler(text="⚙️ Sozlamalar")
async def edit_profile(call: types.CallbackQuery):
    if shortcuts.user_exists(call.from_user.id):
        await EditProfile.choose_field_to_edit.set()
        await call.message.delete()
        await send_message(call.from_user.id, 'choose-field-to-edit', markup=edit_profile_markup())


@dp.callback_query_handler(text="⚙️ Sozlamalar", state='*')
async def edit_profile(call: types.CallbackQuery):
    if shortcuts.user_exists(call.from_user.id):
        await EditProfile.choose_field_to_edit.set()
        await call.message.delete()
        await send_message(call.from_user.id, 'choose-field-to-edit', markup=edit_profile_markup())


@dp.callback_query_handler(state=EditProfile.choose_field_to_edit, text=['edit-age', 'edit-lang', 'edit-accent'])
async def choose_field_handler(call: types.CallbackQuery, state: FSMContext):
    call_data = str(call.data)
    await call.message.delete()
    if call_data == 'edit-age':
        await state.update_data(message_to_delete=call.message)
        await EditProfile.edit_age.set()
        await send_message(call.from_user.id, 'ask-birth-year', markup=edit_age_markup())
    elif call_data == 'edit-lang':
        await EditProfile.edit_language.set()
        await send_message(call.from_user.id, 'ask-native-language', markup=edit_lang_markup())
    elif call_data == 'edit-accent':
        await EditProfile.edit_accent.set()
        await send_message(call.from_user.id, 'ask-accent', markup=edit_accent_markup())


@dp.callback_query_handler(state=EditProfile.edit_age, text=messages.AGE_RANGES)
async def edit_age(call: types.CallbackQuery):
    await shortcuts.edit_profile(call.from_user.id, age=call.data)
    await call.message.delete()
    await send_my_profile(call.from_user.id)


@dp.callback_query_handler(state=EditProfile.edit_language, text=messages.LANGUAGES)
async def edit_lang(call: types.CallbackQuery):
    await shortcuts.edit_profile(call.from_user.id, lang=call.data)
    await call.message.delete()
    await send_my_profile(call.from_user.id)


@dp.callback_query_handler(state=EditProfile.edit_accent,
                           text=messages.REGIONS)
async def edit_accent(call: types.CallbackQuery):
    await shortcuts.edit_profile(call.from_user.id, accent=call.data)
    await call.message.delete()
    await send_my_profile(call.from_user.id)


@dp.message_handler(IsRegistered(), IsSubscribedChannel(), text=messages.MY_RATING)
async def vote_leaderboard(message: types.Message):
    token = await authorization_token(message.chat.id)
    given_votes, votes_position = await common_voice.get_votes_leaderboard(token)
    recorded_clips, clips_position = await common_voice.get_clips_leaderboard(token)

    my_stats = [
        f"ID: <code>{message.chat.id}</code>\n",
        f"<b>🏆 Sizning yutuqlaringiz:</b>\n",
        f"🗣 Yozilgan ovozlar: {recorded_clips}",
        f"📊 Ovoz yozishdagi o'rningiz: {clips_position}\n",
        f"🎧 Tekshirilgan ovozlar: {given_votes}",
        f"📊 Ovoz tekshirishdagi o'rningiz: {votes_position}"
    ]

    await message.answer("\n".join(my_stats), parse_mode="HTML", reply_markup=go_back_markup)
