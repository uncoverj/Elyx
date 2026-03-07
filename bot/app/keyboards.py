"""Telegram keyboards for the simplified Elyx bot UX."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

from app.config import get_settings


def main_menu_kb(is_admin: bool = False) -> ReplyKeyboardMarkup:
    cfg = get_settings()
    keyboard = [
        [KeyboardButton(text="🔍 Поиск"), KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="📊 Стата"), KeyboardButton(text="💞 Мэтчи")],
        [KeyboardButton(text="🏆 Лидерборд"), KeyboardButton(text="⚙️ Настройки")],
        [KeyboardButton(text="ℹ️ Помощь")],
        [KeyboardButton(text="📱 Elyx App", web_app=WebAppInfo(url=cfg.webapp_url))],
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text="🛡 Админ-панель")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


MAIN_MENU = main_menu_kb()


def webapp_inline_kb() -> InlineKeyboardMarkup:
    cfg = get_settings()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📱 Открыть Elyx App", web_app=WebAppInfo(url=cfg.webapp_url))]
        ]
    )


GENDER_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Парень 🙋‍♂️"), KeyboardButton(text="Девушка 🙋‍♀️")],
        [KeyboardButton(text="Скрыть 🙈")],
    ],
    resize_keyboard=True,
)


GAME_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Valorant"), KeyboardButton(text="CS2 / Faceit")],
    ],
    resize_keyboard=True,
)


CONFIRM_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="✅ Сохранить"), KeyboardButton(text="✏️ Изменить")]],
    resize_keyboard=True,
)


SEARCH_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❤️ Лайк"), KeyboardButton(text="👎 Скип")],
        [KeyboardButton(text="✉️ Письмо"), KeyboardButton(text="⛔ Стоп")],
        [KeyboardButton(text="🚫 Блок"), KeyboardButton(text="⚠️ Репорт")],
    ],
    resize_keyboard=True,
)


PROFILE_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Смотреть анкеты"), KeyboardButton(text="📊 Обновить стату")],
        [KeyboardButton(text="📷 Изменить фото/видео"), KeyboardButton(text="✏️ Изменить текст")],
        [KeyboardButton(text="🔄 Заполнить заново"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)


SETTINGS_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎮 Аккаунты"), KeyboardButton(text="🔄 Обновить статистику")],
        [KeyboardButton(text="🏆 Лидерборд"), KeyboardButton(text="🆘 Поддержка")],
        [KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)


ACCOUNT_DATA_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Riot ID"), KeyboardButton(text="Faceit")],
        [KeyboardButton(text="🔄 Обновить статистику"), KeyboardButton(text="🏆 Лидерборд")],
        [KeyboardButton(text="⬅️ Назад")],
    ],
    resize_keyboard=True,
)


ACCOUNT_PROVIDER_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Riot ID"), KeyboardButton(text="Faceit")],
        [KeyboardButton(text="Пропустить")],
    ],
    resize_keyboard=True,
)


MOOD_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="😌 Chill"), KeyboardButton(text="🔥 Serious")],
        [KeyboardButton(text="😏 Flirty"), KeyboardButton(text="🏆 Duo Ranked")],
        [KeyboardButton(text="💬 Just Chat"), KeyboardButton(text="⏩ Пропустить")],
    ],
    resize_keyboard=True,
)


GREEN_FLAG_OPTIONS = [
    "🧘 Спокойный",
    "🎤 Есть микрофон",
    "⏰ Стабильный онлайн",
    "🙂 Без токсика",
    "🎯 Играет на результат",
    "🤝 Командный",
    "🌙 Вечерний онлайн",
    "😂 С юмором",
    "🛡 Уважительный",
]


DEALBREAKER_OPTIONS = [
    "🗑 Токсичность",
    "👻 Гостинг",
    "😤 Агрессия",
    "🔇 Никогда не в голосе",
    "📵 Частые афк",
    "🤬 Оскорбления",
]


def green_flags_kb(selected: list[str]) -> InlineKeyboardMarkup:
    rows = []
    for i in range(0, len(GREEN_FLAG_OPTIONS), 3):
        row = []
        for opt in GREEN_FLAG_OPTIONS[i : i + 3]:
            marker = "✅ " if opt in selected else ""
            row.append(InlineKeyboardButton(text=f"{marker}{opt}", callback_data=f"gf:{opt}"))
        rows.append(row)
    rows.append([InlineKeyboardButton(text="✅ Готово", callback_data="gf:done")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def dealbreaker_kb() -> InlineKeyboardMarkup:
    rows = []
    for i in range(0, len(DEALBREAKER_OPTIONS), 3):
        rows.append(
            [InlineKeyboardButton(text=opt, callback_data=f"db:{opt}") for opt in DEALBREAKER_OPTIONS[i : i + 3]]
        )
    rows.append([InlineKeyboardButton(text="⏩ Пропустить", callback_data="db:skip")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def view_like_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="👀 Посмотреть")]], resize_keyboard=True, one_time_keyboard=True)


def react_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❤️ Лайк"), KeyboardButton(text="👎 Скип")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def match_username_kb(username: str | None) -> ReplyKeyboardMarkup:
    rows = []
    if username:
        rows.append([KeyboardButton(text=f"@{username}")])
    rows.append([KeyboardButton(text="🏠 Главное меню")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def matches_nav(index: int, total: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="◀️", callback_data="match_prev"),
                InlineKeyboardButton(text=f"{index}/{total}", callback_data="match_idx"),
                InlineKeyboardButton(text="▶️", callback_data="match_next"),
            ]
        ]
    )


def leaderboard_nav(page: int, total_pages: int) -> InlineKeyboardMarkup:
    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"lb_page_{page - 1}"))
    buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="lb_idx"))
    if page < total_pages:
        buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"lb_page_{page + 1}"))
    return InlineKeyboardMarkup(
        inline_keyboard=[
            buttons,
            [InlineKeyboardButton(text="📊 Моя позиция", callback_data="lb_my_pos")],
        ]
    )


def first_move_kb(match_user_id: int, options: list[str]) -> InlineKeyboardMarkup:
    rows = []
    for i, text in enumerate(options):
        short = f"{text[:40]}…" if len(text) > 40 else text
        rows.append([InlineKeyboardButton(text=f"💬 {short}", callback_data=f"fm:{match_user_id}:{i}")])
    rows.append([InlineKeyboardButton(text="✍️ Написать своё", callback_data=f"fm:{match_user_id}:custom")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
