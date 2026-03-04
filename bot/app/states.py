"""FSM states for the dating bot."""

from aiogram.fsm.state import State, StatesGroup


class RegistrationState(StatesGroup):
    nickname = State()
    gender = State()
    age = State()
    game = State()
    roles = State()
    tags = State()
    green_flags = State()      # multi-select inline
    dealbreaker = State()      # single-select inline
    bio = State()
    media = State()
    account_ref = State()      # game ID input (auto-detected provider)
    confirm = State()


class BrowsingState(StatesGroup):
    mood = State()             # mood selection before search
    active = State()
    letter_text = State()
    reacting = State()         # reacting to incoming like/letter


class MatchesState(StatesGroup):
    viewing = State()


class SettingsState(StatesGroup):
    menu = State()
    riot = State()
    faceit = State()
    steam = State()
    blizzard = State()
    epic = State()
    change_game = State()
    new_game_id = State()


class ProfileEditState(StatesGroup):
    bio = State()
    media = State()
