from db.base import session
from db.models import User
from main import bot


# Function to get bot statistics
async def get_bot_stat_func(chat_id):
    users_count = session.query(User).count()
    admin_text = 'Total users count: {}'.format(users_count)
    await bot.send_message(chat_id, admin_text, parse_mode='markdown')
