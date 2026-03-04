from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_search_kb() -> ReplyKeyboardMarkup:
    """Клавиатура для поиска (свайпы)"""
    kb = [
        [KeyboardButton(text="❤️ Лайк"), KeyboardButton(text="👎 Скип")],
        [KeyboardButton(text="✉️ Письмо"), KeyboardButton(text="⛔ Стоп")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_letter_kb() -> ReplyKeyboardMarkup:
    """Клавиатура при написании письма"""
    kb = [[KeyboardButton(text="Отмена")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def get_incoming_like_kb(from_user_id: int) -> InlineKeyboardMarkup:
    """Кнопка 'Посмотреть' при получении лайка/письма"""
    kb = [[InlineKeyboardButton(text="👀 Посмотреть", callback_data=f"view_{from_user_id}")]]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_reaction_kb(from_user_id: int) -> InlineKeyboardMarkup:
    """Кнопки ответа на лайк/письмо"""
    kb = [
        [
            InlineKeyboardButton(text="❤️ Лайк", callback_data=f"match_{from_user_id}"),
            InlineKeyboardButton(text="👎 Скип", callback_data=f"rej_{from_user_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_match_pagination_kb(match_id: int, current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Пагинация для мэтчей (◀ 2/12 ▶)"""
    # Если страниц <= 1, кнопки не нужны или нужны неактивные
    if total_pages <= 1:
        return InlineKeyboardMarkup(inline_keyboard=[])
        
    prev_page = current_page - 1 if current_page > 1 else total_pages
    next_page = current_page + 1 if current_page < total_pages else 1
    
    kb = [
        [
            InlineKeyboardButton(text="◀", callback_data=f"mpage_{prev_page}"),
            InlineKeyboardButton(text=f"{current_page} / {total_pages}", callback_data="ignore"),
            InlineKeyboardButton(text="▶", callback_data=f"mpage_{next_page}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
