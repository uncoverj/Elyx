from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Поиск"), KeyboardButton(text="Мой профиль")],
        [KeyboardButton(text="Мэтчи"), KeyboardButton(text="Настройки")],
    ],
    resize_keyboard=True,
)

GENDER_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Male"), KeyboardButton(text="Female"), KeyboardButton(text="Other")]],
    resize_keyboard=True,
)

GAME_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Valorant"), KeyboardButton(text="CS2")],
        [KeyboardButton(text="Dota 2"), KeyboardButton(text="League of Legends")],
        [KeyboardButton(text="Apex Legends"), KeyboardButton(text="Other")],
    ],
    resize_keyboard=True,
)

SEARCH_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Лайк"), KeyboardButton(text="Скип")],
        [KeyboardButton(text="Отправить письмо"), KeyboardButton(text="Остановить поиск")],
    ],
    resize_keyboard=True,
)

PROFILE_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Поиск")],
        [KeyboardButton(text="Перезаполнить анкету"), KeyboardButton(text="Изменить фото/видео")],
        [KeyboardButton(text="Изменить био"), KeyboardButton(text="Главное меню")],
    ],
    resize_keyboard=True,
)

SETTINGS_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Премиум"), KeyboardButton(text="Поддержка")],
        [KeyboardButton(text="Данные аккаунта"), KeyboardButton(text="Главное меню")],
    ],
    resize_keyboard=True,
)

ACCOUNT_DATA_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Riot ID"), KeyboardButton(text="Steam")],
        [KeyboardButton(text="Обновить статистику"), KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True,
)

CONFIRM_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="✅ Сохранить"), KeyboardButton(text="✏️ Изменить")]],
    resize_keyboard=True,
)

OPEN_WEBAPP_INLINE = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Открыть Web App", web_app={"url": "https://example.com"})]]
)


def matches_nav(index: int, total: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️", callback_data="match_prev"),
                InlineKeyboardButton(text=f"{index}/{total}", callback_data="match_idx"),
                InlineKeyboardButton(text="➡️", callback_data="match_next"),
            ]
        ]
    )
