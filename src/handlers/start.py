from datetime import datetime

import aiohttp
import pandas
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ParseMode

from data.messages import INSTRUCTIONS, LEADERBOARD, CANCEL_MESSAGE, ABOUT_PROJECT, msg_dict, VOICE_LEADERBOARD, \
    VOTE_LEADERBOARD, OVERALL_STATS
from keyboards.buttons import (
    native_languages_markup,
    share_phone_markup,
    register_markup,
    accents_markup,
    genders_markup,
    leader_markup,
    start_markup,
    age_markup
)
from main import UserRegistration, dp
from main import bot
from utils.helpers import send_message, IsSubscribedChannel, IsRegistered
from utils.uzbekvoice import db
from utils.uzbekvoice.common_voice import CLIPS_LEADERBOARD_URL, VOTES_LEADERBOARD_URL, RECORDS_STAT_URL, \
    ACTIVITY_STAT_URL
from utils.uzbekvoice.helpers import register_user, authorization_token


@dp.message_handler(commands=['start'], state='*')
async def start_command(message: Message, state: FSMContext):
    await state.finish()
    if db.user_exists(message.chat.id):
        await send_message(message.chat.id, 'welcome-text', markup=start_markup)
    else:
        await send_message(message.chat.id, 'start', markup=register_markup)


# Answer to all bot commands
@dp.message_handler(text="👤 Ro'yxatdan o'tish")
async def register_command(message: Message):
    if not db.user_exists(message.chat.id):
        await UserRegistration.full_name.set()
        await send_message(message.chat.id, 'ask-full-name')
    else:
        await send_message(message.chat.id, 'Siz ro\'yxatdan o\'tib bo\'lgansiz!', markup=start_markup)


@dp.message_handler(state=UserRegistration.full_name)
async def get_name(message: Message, state: FSMContext):
    if message.text == "👤 Ro'yxatdan o'tish":
        await UserRegistration.full_name.set()
        await send_message(message.chat.id, 'ask-full-name')
    else:
        async with state.proxy() as data:
            data["full_name"] = message.text
            await UserRegistration.next()
            await send_message(message.chat.id, 'ask-phone', markup=share_phone_markup)


@dp.message_handler(state=UserRegistration.phone_number, content_types=['contact', 'text'])
async def get_phone(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["phone_number"] = str(message.contact.phone_number if message.contact else message.text)
        await UserRegistration.gender.set()
        await send_message(message.chat.id, 'ask-gender', markup=genders_markup)


@dp.inline_handler()
@dp.message_handler(state=UserRegistration.gender)
async def get_gender(message: Message, state: FSMContext):
    if message.text in ['👨 Erkak', '👩 Ayol']:
        async with state.proxy() as data:
            without_emoji = message.text.split(' ')[1]
            data["gender"] = without_emoji
        await UserRegistration.native_language.set()
        await send_message(message.chat.id, 'ask-native-language', markup=native_languages_markup)
    else:
        await send_message(message.chat.id, 'ask-gender', markup=genders_markup)
        return await UserRegistration.gender.set()


@dp.message_handler(state=UserRegistration.native_language)
async def native_language(message: Message, state: FSMContext):
    if message.text in [
        "O'zbek tili",
        "Qoraqalpoq tili",
        "Rus tili",
        "Tojik tili",
        "Qozoq tili"
    ]:
        async with state.proxy() as data:
            data["native_language"] = message.text

        await send_message(message.chat.id, 'ask-accent', markup=accents_markup)
        await UserRegistration.accent_region.set()
    else:
        await send_message(message.chat.id, 'ask-native-language', markup=native_languages_markup)


@dp.message_handler(state=UserRegistration.accent_region)
async def get_accent_region(message: Message, state: FSMContext):
    if (message.text in ["Andijon",
                         "Buxoro",
                         "Farg'ona",
                         "Jizzax",
                         "Sirdaryo",
                         "Xorazm",
                         "Namangan",
                         "Navoiy",
                         "Qashqadaryo",
                         "Qoraqalpog'iston",
                         "Samarqand",
                         "Surxondaryo",
                         "Toshkent viloyati",
                         "Toshkent shahri"]):
        async with state.proxy() as data:
            data["accent_region"] = message.text
        await send_message(message.chat.id, 'ask-birth-year', markup=age_markup)
        await UserRegistration.year_of_birth.set()
    else:
        await send_message(message.chat.id, 'ask-accent', markup=accents_markup)


@dp.message_handler(state=UserRegistration.year_of_birth)
async def finish(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text in ["< 19", "19-29", "30-39", "40-49", "50-59",
                            "60-69", "70-79", "80-89", "> 89"]:
            data["year_of_birth"] = message.text
            await register_user(data, message.chat.id)
            await send_message(message.chat.id, 'register-success', markup=start_markup)
            await state.finish()
        else:
            await send_message(message.chat.id, 'ask-birth-year-again')
            return await UserRegistration.year_of_birth.set()


@dp.message_handler(IsSubscribedChannel(), text=LEADERBOARD)
async def leaderboard(message: Message):
    await send_message(message.chat.id, 'leaderboard', markup=leader_markup)


@dp.message_handler(IsSubscribedChannel(), text=INSTRUCTIONS)
async def instructions(message: Message):
    await send_message(message.chat.id, 'instructions', markup=start_markup)


@dp.message_handler(IsSubscribedChannel(), text=ABOUT_PROJECT)
async def instructions(message: Message):
    await bot.send_message(message.chat.id, msg_dict['about-project'], reply_markup=start_markup,
                           parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(text=CANCEL_MESSAGE)
async def go_back(message: Message):
    await bot.send_message(message.chat.id, 'Bosh menyu: ', reply_markup=start_markup)


@dp.message_handler(IsRegistered(), IsSubscribedChannel(), text=VOICE_LEADERBOARD)
async def voice_leaderboard(message: Message):
    headers = {
        'Authorization': await authorization_token(message.chat.id)
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(CLIPS_LEADERBOARD_URL, headers=headers) as get_request:
            leaderboard_dict = await get_request.json()
            print(leaderboard_dict)
    data = {
        '№': [],
        '|FIO|': [],
        '|Yozilgan|': []
    }

    for leader in leaderboard_dict:
        data['№'].append(leader['position'] + 1)
        data['|FIO|'].append(f"{leader['username'][:10]}...")
        data['|Yozilgan|'].append(leader['total'])

    copy_data = data.copy()
    del data['№']
    leaderboard_text = pandas.DataFrame(data=data, index=copy_data['№'])
    leaderboard_text.index.name = '№'
    leaderboard_text = '```' + leaderboard_text.to_string() + '```'

    await bot.send_message(
        message.chat.id,
        leaderboard_text,
        reply_markup=start_markup,
        parse_mode=ParseMode.MARKDOWN
    )


@dp.message_handler(IsRegistered(), IsSubscribedChannel(), text=VOTE_LEADERBOARD)
async def vote_leaderboard(message: Message):
    headers = {
        'Authorization': await authorization_token(message.chat.id)
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(VOTES_LEADERBOARD_URL, headers=headers) as get_request:
            leaderboard_dict = await get_request.json()
    data = {
        '№': [],
        '|FIO|': [],
        '|Tekshirilgan|': []
    }

    for leader in leaderboard_dict:
        data['№'].append(leader['position'] + 1)
        data['|FIO|'].append(f"{leader['username'][:10]}...")
        data['|Tekshirilgan|'].append(leader['total'])

    copy_data = data.copy()
    del data['№']
    leaderboard_text = pandas.DataFrame(data=data, index=copy_data['№'])
    leaderboard_text.index.name = '№'
    leaderboard_text = '```' + leaderboard_text.to_string() + '```'

    await bot.send_message(
        message.chat.id,
        leaderboard_text,
        reply_markup=start_markup,
        parse_mode=ParseMode.MARKDOWN
    )


@dp.message_handler(IsRegistered(), IsSubscribedChannel(), text=OVERALL_STATS)
async def stats(message: Message):
    headers = {
        'Authorization': await authorization_token(message.chat.id)
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(RECORDS_STAT_URL, headers=headers) as get_request:
            stats_dict = await get_request.json()
        async with session.get(ACTIVITY_STAT_URL, headers=headers) as get_request:
            activity_dict = await get_request.json()

    latest_records = stats_dict[-1]
    latest_activity = activity_dict[-1]

    overall_records = int(int(latest_records['total']) / 3600)  # 1 hour = 3600 seconds
    checked_records = int(int(latest_records['valid']) / 3600)
    stats_hour = latest_activity['date']
    stats_hour = datetime.strptime(stats_hour, '%Y-%m-%dT%H:%M:%S.%fZ').hour + 5
    users_count = latest_activity['value']

    stat_message = f"""
🗣️ Umumiy yozilgan: {overall_records} soat

✅ Tekshirilgan yozuvlar: {checked_records} soat

☑️ 2-bosqich maqsadi: 2000 soat tekshirilgan yozvular

⌛ Bugun {stats_hour}:00da aktivlar soni: {users_count}
    """

    await bot.send_message(
        message.chat.id,
        text=stat_message,
        reply_markup=start_markup,
        parse_mode=ParseMode.MARKDOWN
    )
