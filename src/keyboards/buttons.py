from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from data import messages

admin_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
admin_markup.add(
    KeyboardButton(messages.SEND_EVERYONE),
    KeyboardButton(messages.SEND_CERTAIN),
    KeyboardButton(messages.BLOCK_CERTAIN),
    KeyboardButton(messages.UNBLOCK_CERTAIN),
    KeyboardButton(messages.BOT_STATISTICS),
)

go_back_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
go_back_markup.add(KeyboardButton(messages.CANCEL_MESSAGE))

sure_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
sure_markup.add(
    KeyboardButton('✅ Start'),
    KeyboardButton('🚫 Cancel')
)

yes_no_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
yes_no_markup.add(
    KeyboardButton('✅ Yes'),
    KeyboardButton('🚫 No'),
)

age_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
age_markup.add(*[KeyboardButton(t) for t in messages.AGE_RANGES])

share_phone_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
share_phone_markup.add(KeyboardButton("📱Raqamimni jo'natish", request_contact=True))

register_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
register_markup.add(KeyboardButton("👤 Ro'yxatdan o'tish"))

start_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
start_markup.add(
    KeyboardButton(messages.RECORD_VOICE),
    KeyboardButton(messages.CHECK_VOICE),
    KeyboardButton(messages.LEADERBOARD),
    KeyboardButton(messages.INSTRUCTIONS),
    KeyboardButton(messages.MY_PROFILE),
    KeyboardButton(messages.MY_RATING),
    KeyboardButton(messages.OVERALL_STATS),
    KeyboardButton(messages.ABOUT_PROJECT),
)

genders_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
genders_markup.add(
    KeyboardButton('👩 Ayol'),
    KeyboardButton('👨 Erkak')
)

accents_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
accents_markup.add(*[KeyboardButton(t) for t in messages.REGIONS])

native_languages_markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
native_languages_markup.add(KeyboardButton(t) for t in messages.LANGUAGES)

leader_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
leader_markup.add(
    KeyboardButton(messages.VOICE_LEADERBOARD),
    KeyboardButton(messages.VOTE_LEADERBOARD),
    KeyboardButton(messages.CANCEL_MESSAGE),
)
