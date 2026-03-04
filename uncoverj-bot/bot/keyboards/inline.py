from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Наборы тегов (playstyle + behavior)
AVAILABLE_TAGS = [
    "duelist", "support", "igl", "sniper", "lurker",
    "chill", "tryhard", "no_toxic", "18plus", "mic_required"
]

def get_tags_kb(selected_tags: set) -> InlineKeyboardMarkup:
    """Multi-select клавиатура для тегов"""
    builder = InlineKeyboardBuilder()
    
    for tag in AVAILABLE_TAGS:
        status = "✅" if tag in selected_tags else "❌"
        builder.button(text=f"{status} {tag}", callback_data=f"tag_{tag}")
    
    builder.adjust(2) # по 2 кнопки в ряд
    
    # Кнопка Готово всегда внизу
    builder.row(InlineKeyboardButton(text="Готово ✅", callback_data="tags_done"))
    
    return builder.as_markup()
