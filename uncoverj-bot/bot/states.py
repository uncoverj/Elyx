from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    waiting_nickname = State()   # шаг 2: никнейм
    waiting_gender = State()     # шаг 3: пол (кнопки)
    waiting_age = State()        # шаг 4: возраст (число)
    waiting_game = State()       # шаг 5: игра (кнопки)
    waiting_tags = State()       # шаг 6: теги стиля (multi-select)
    waiting_bio = State()        # шаг 7: описание (текст)
    waiting_photo = State()      # шаг 8: фото или видео
    waiting_game_id = State()    # шаг 9: Riot ID или Steam ID

class SearchStates(StatesGroup):
    browsing = State()           # просмотр анкет
    waiting_letter = State()     # ожидание текста письма

class ProfileStates(StatesGroup):
    waiting_new_photo = State()
    waiting_new_bio = State()

class SettingsStates(StatesGroup):
    waiting_new_game_id = State()
