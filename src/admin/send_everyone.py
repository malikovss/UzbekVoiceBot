import asyncio

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.exceptions import UserDeactivated, BotBlocked

from keyboards.buttons import sure_markup, admin_markup
from main import dp, bot, AdminSendEveryOne
from utils.uzbekvoice.db import session, User


# Ask admin to send post
async def send_everyone_func(chat_id):
    await bot.send_message(chat_id, 'Send the post for push-notification 👇', reply_markup=ReplyKeyboardRemove())
    await AdminSendEveryOne.ask_post.set()


# Show post sample
@dp.message_handler(state=AdminSendEveryOne.all_states, text='Cancel')
async def admin_reject_handler(message: Message, state: FSMContext):
    await bot.send_message(message.chat.id, 'You have canceled push-notification  ✅', reply_markup=admin_markup)
    await state.finish()


# Show post sample
@dp.message_handler(state=AdminSendEveryOne.ask_post, content_types=['photo', 'text', 'voice', 'animation', 'video'])
async def admin_ask_post(message: Message, state: FSMContext):
    chat_id = message.chat.id
    buttons = message.reply_markup

    await state.update_data(buttons=buttons)
    await state.update_data(message_id=message.message_id)
    await state.update_data(copy_from=chat_id)

    await bot.copy_message(chat_id, chat_id, message.message_id)
    await bot.send_message(chat_id,
                           'Your push-notification will look like this, start sending it to users?',
                           reply_markup=sure_markup)

    await AdminSendEveryOne.ask_send.set()


# Ask if the admin sure to start sending notifications
@dp.message_handler(state=AdminSendEveryOne.ask_send)
async def admin_ask_send(message: Message, state: FSMContext):
    chat_id = message.chat.id
    admin_message = message.text

    if admin_message == '✅ Start':
        await send_post(chat_id, state)
        return
    elif admin_message == '🚫 Cancel':
        await state.finish()
        await bot.send_message(chat_id, 'Message canceled ✅', reply_markup=admin_markup)
        return
    await bot.send_message(chat_id, 'Begin push-notification or cancel?', reply_markup=sure_markup)
    await AdminSendEveryOne.ask_send.set()


# Function for sending notifications to all users
async def send_post(chat_id, state):
    data = await state.get_data()
    message_id = data.get('message_id')
    buttons = data.get('buttons')

    await state.finish()

    await bot.send_message(chat_id, 'Push-notification begin!', reply_markup=admin_markup)
    users_id = session.query(User).all()

    send_count = 0
    blocked = 0
    deactivated = 0
    errors = 0
    success = 0
    sent_message = await send_progress_message(chat_id, success)
    tasks = []
    for user_id in users_id:
        tg_id = user_id.tg_id
        tasks.append(asyncio.ensure_future(send_copied_post_to_user(tg_id, chat_id, message_id, buttons)))
        send_count += 1
        if send_count >= 30:
            send_count = 0
            await asyncio.sleep(1)

    gather_results = await asyncio.gather(*tasks)
    for result in gather_results:
        if result == 'success':
            success += 1
        elif result == 'blocked':
            blocked += 1
        elif result == 'deactivated':
            deactivated += 1
        else:
            errors += 1

    admin_stat = "Notification received: {0:,}\n" \
                 "Blocked the bot: {1:,}\n" \
                 "Deleted the telegram: {2:,}\n" \
                 "Other reasons: {3:,}".format(success, blocked, deactivated, errors)

    await bot.send_message(chat_id, admin_stat, reply_markup=admin_markup)
    await sent_message.delete()


# Function to send copy message-notification to one user
async def send_copied_post_to_user(user_id, copy_from_chat_id, message_id, buttons):
    try:
        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=copy_from_chat_id,
            message_id=message_id,
            disable_notification=True,
            reply_markup=buttons
        )
        return 'success'
    except BotBlocked:
        return 'blocked'
    except UserDeactivated:
        return 'deactivated'
    except Exception as err:
        print(err, 'send_copied_post_to_user')
        return False


async def send_progress_message(chat_id, count):
    sent_message = await bot.send_message(chat_id, '{0:,} users received the push-notification.'.format(count))
    return sent_message
