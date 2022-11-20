import base64
import random
import string
import uuid

from data.messages import msg_dict
from keyboards.inline import my_profile_markup
from main import bot
from .uzbekvoice import db


async def authorization_token(tg_id):
    user = db.get_user(tg_id)
    auth = f"{user.uuid}:{user.access_token}".encode('ascii')
    base64_bytes = base64.b64encode(auth)
    base64_string = base64_bytes.decode('ascii')
    return f'Basic {base64_string}'


async def register_user(state, tg_id):
    user_uid = uuid.uuid4()
    access_token = ''.join(
        random.choice(string.ascii_letters + string.digits) for _ in range(40)
    )

    await db.write_user(
        tg_id=tg_id,
        uuid=user_uid,
        access_token=access_token,
        full_name=state['full_name'],
        phone_number=state['phone_number'],
        gender=state['gender'],
        accent_region=state['accent_region'],
        year_of_birth=state['year_of_birth'],
        native_language=state['native_language']
    )


async def send_my_profile(tg_id):
    user = db.get_user(tg_id)
    my_profile = [
        f"👤 Mening profilim:\n\n"
        f"ID: <code>{tg_id}</code>",
        f"Ism: <b>{user['full_name']}</b>",
        f"Telefon raqam: <b>{user['phone_number']}</b>",
        f"Yosh oralig'i: <b>{str(user['year_of_birth'])}</b>",
        f"Jinsi: <b>{user['gender']}</b>",
        f"Ona-tili: <b>{user['native_language']}</b>",
        f"Shevasi: <b>{user['accent_region']}</b>",
    ]
    await bot.send_message(tg_id, '\n'.join(my_profile), parse_mode="HTML", reply_markup=my_profile_markup())


# Function to send waiting message
async def send_message(chat_id, msg, args=None, markup=None, parse=None, reply=None):
    try:
        msg_to_send = await user_msg(msg, args)
        sent_message = await bot.send_message(chat_id, msg_to_send, reply_markup=markup, parse_mode=parse,
                                              disable_web_page_preview=True, disable_notification=True,
                                              reply_to_message_id=reply)
        return sent_message.message_id
    except Exception as err:
        print('Error in send_message', err)


async def delete_message_markup(chat_id, message_id):
    try:
        await bot.edit_message_reply_markup(chat_id, message_id)

    except Exception as err:
        print('Error in delete_message_markup', err)


async def delete_message(chat_id, message_id):
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception as err:
        print('Error in delete_message', err)


async def send_voice(chat_id, file_to_send, caption, args=None, markup=None, parse=None):
    msg_to_send = await user_msg(caption, args)
    sent_voice = await bot.send_voice(chat_id, file_to_send, caption=msg_to_send, reply_markup=markup, parse_mode=parse)
    return sent_voice.message_id


async def edit_reply_markup(chat_id, message_id, markup):
    await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=markup)


# Get user message
async def user_msg(message_str, args):
    if args is None:
        if not (message_str in msg_dict):
            return message_str
        else:
            user_message = msg_dict[message_str]
    else:
        if type(args) != tuple:
            user_message = msg_dict[message_str].format(args)
        else:
            user_message = msg_dict[message_str].format(*args)

    return user_message
