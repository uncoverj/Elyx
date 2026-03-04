from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_profile_kb() -> ReplyKeyboardMarkup:
    """Клавиатура 'Мой профиль'"""
    kb = [
        [KeyboardButton(text="🔍 Смотреть анкеты"), KeyboardButton(text="🔄 Заполнить заново")],
        [KeyboardButton(text="📷 Изменить фото/видео"), KeyboardButton(text="✏️ Изменить текст")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_settings_kb() -> ReplyKeyboardMarkup:
    """Клавиатура 'Настройки'"""
    kb = [
        [KeyboardButton(text="⭐ Premium"), KeyboardButton(text="🆘 Поддержка")],
        [KeyboardButton(text="🎮 Данные аккаунта"), KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_cancel_kb() -> ReplyKeyboardMarkup:
    """Кнопка Отмена для состояний редактирования"""
    kb = [[KeyboardButton(text="Отмена")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
