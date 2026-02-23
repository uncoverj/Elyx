from aiogram.fsm.state import State, StatesGroup


class RegistrationState(StatesGroup):
    nickname = State()
    gender = State()
    age = State()
    game = State()
    roles = State()
    tags = State()
    bio = State()
    media = State()
    confirm = State()


class BrowsingState(StatesGroup):
    active = State()
    letter_text = State()


class MatchesState(StatesGroup):
    viewing = State()


class SettingsState(StatesGroup):
    menu = State()
    riot = State()
    steam = State()


class ProfileEditState(StatesGroup):
    bio = State()
    media = State()
