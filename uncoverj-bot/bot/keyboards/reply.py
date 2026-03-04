from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню бота"""
    kb = [
        [KeyboardButton(text="🔍 Поиск"), KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="💞 Мэтчи"), KeyboardButton(text="⚙️ Настройки")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_gender_kb() -> ReplyKeyboardMarkup:
    """Выбор пола"""
    kb = [
        [KeyboardButton(text="Парень"), KeyboardButton(text="Девушка")],
        [KeyboardButton(text="Скрыть")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def get_game_kb() -> ReplyKeyboardMarkup:
    """Выбор игры"""
    kb = [
        [KeyboardButton(text="Valorant"), KeyboardButton(text="CS2")],
        [KeyboardButton(text="Dota 2"), KeyboardButton(text="LoL")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def get_skip_bio_kb() -> ReplyKeyboardMarkup:
    """Кнопка пропуска биографии"""
    kb = [[KeyboardButton(text="Пропустить")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
