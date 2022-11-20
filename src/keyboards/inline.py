from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from data import messages


def yes_no_markup(voice_id, confirm_state=None):
    markup = InlineKeyboardMarkup(row_width=2)
    accept_button = InlineKeyboardButton(
        text='{} {}'.format('✅️' if confirm_state == 'accept' else '', messages.VOICE_CORRECT),
        callback_data='accept/{}'.format(voice_id))
    reject_button = InlineKeyboardButton(
        text='{} {}'.format('✅️' if confirm_state == 'reject' else '', messages.VOICE_INCORRECT),
        callback_data='reject/{}'.format(voice_id))
    skip_button = InlineKeyboardButton(text='{} {}'.format('✅️' if confirm_state == 'skip' else '', messages.SKIP_STEP),
                                       callback_data='skip/{}'.format(voice_id))
    report_button = InlineKeyboardButton(text=messages.VOICE_REPORT, callback_data='report/{}'.format(voice_id))
    markup.add(
        accept_button,
        reject_button,
        skip_button,
        report_button
    )
    if confirm_state is not None:
        markup.add(
            InlineKeyboardButton(messages.SUBMIT_VOICE_TEXT,
                                 callback_data='submit/{}'.format(voice_id))
        )
    else:
        markup.add(InlineKeyboardButton(messages.GO_HOME_TEXT, callback_data='home'))
    return markup


def report_voice_markup(voice_id):
    markup = InlineKeyboardMarkup(row_width=1)
    texts = [
        messages.REPORT_TEXT_1,
        messages.REPORT_TEXT_2,
        messages.REPORT_TEXT_3,
        messages.REPORT_TEXT_4,
    ]
    markup.add(
        *[
            InlineKeyboardButton(text=txt, callback_data=f"report_{idx}/{voice_id}") for idx, txt in enumerate(texts, 1)
        ],
        InlineKeyboardButton(text=messages.REPORT_TEXT_5, callback_data=f'back/{voice_id}')
    )
    return markup


def report_text_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    _report_texts = {
        'report_1': messages.REPORT_TEXT_1,
        'report_2': messages.REPORT_TEXT_2,
        'report_3': messages.REPORT_TEXT_3,
        'report_4': messages.REPORT_TEXT_4,
        'back': messages.REPORT_TEXT_5
    }
    markup.add(*[InlineKeyboardButton(text=v, callback_data=k) for k, v in _report_texts.items()])
    return markup


def text_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(text=messages.SKIP_STEP, callback_data='skip'),
        InlineKeyboardButton(text=messages.VOICE_REPORT, callback_data='report')
    )
    return markup


def confirm_voice_markup():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(messages.CONFIRM_VOICE_TEXT,
                             callback_data='confirm-voice'),
        InlineKeyboardButton(messages.REJECT_VOICE_TEXT,
                             callback_data='reject-voice')
    )
    return markup


def edit_profile_markup():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Yosh", callback_data='edit-age'),
        InlineKeyboardButton("Til", callback_data='edit-lang'),
        InlineKeyboardButton("Sheva", callback_data='edit-accent'),
        InlineKeyboardButton(messages.GO_HOME_TEXT, callback_data=messages.GO_HOME_TEXT)
    )
    return markup


def edit_age_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        *[
            InlineKeyboardButton(text=age, callback_data=age) for age in messages.AGE_RANGES
        ],
        InlineKeyboardButton(messages.GO_HOME_TEXT, callback_data=messages.GO_HOME_TEXT)
    )
    return markup


def edit_lang_markup():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        *[
            InlineKeyboardButton(text=lang, callback_data=lang) for lang in messages.LANGUAGES
        ],
        InlineKeyboardButton(messages.GO_HOME_TEXT, callback_data=messages.GO_HOME_TEXT)
    )

    return markup


def edit_accent_markup():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        *[
            InlineKeyboardButton(text=reg, callback_data=reg) for reg in messages.REGIONS
        ],
        InlineKeyboardButton(messages.GO_HOME_TEXT, callback_data=messages.GO_HOME_TEXT)
    )

    return markup


def my_profile_markup():
    markup = InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(
        InlineKeyboardButton('⚙️ Sozlamalar', callback_data='⚙️ Sozlamalar'),
        InlineKeyboardButton(messages.GO_HOME_TEXT, callback_data=messages.GO_HOME_TEXT)
    )

    return markup
