from aiogram.dispatcher.filters.state import StatesGroup, State


class UserRegistration(StatesGroup):
    full_name = State()
    phone_number = State()
    gender = State()
    native_language = State()
    accent_region = State()
    year_of_birth = State()
    finish = State()


class AdminSendEveryOne(StatesGroup):
    ask_post = State()
    ask_send = State()


class AdminSendCertain(StatesGroup):
    ask_post = State()
    ask_correct = State()
    ask_users = State()
    ask_send = State()


class AdminBanCertain(StatesGroup):
    ask_correct = State()
    ask_users = State()


class AdminUnbanCertain(StatesGroup):
    ask_correct = State()
    ask_users = State()


class AskUserVoice(StatesGroup):
    ask_voice = State()
    ask_confirm = State()
    confirm_action = State()
    report_type = State()


class AskUserAction(StatesGroup):
    ask_action = State()
    confirm_action = State()
    report_type = State()


class EditProfile(StatesGroup):
    choose_field_to_edit = State()
    edit_age = State()
    edit_language = State()
    edit_accent = State()
