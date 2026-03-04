"""All keyboards for the dating bot — emoji-rich, dating vibe."""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

from app.config import get_settings

# ── Main Menu ──────────────────────────────────────────────
def main_menu_kb() -> ReplyKeyboardMarkup:
    """Main menu with Web App button."""
    cfg = get_settings()
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Поиск"), KeyboardButton(text="👤 Мой профиль")],
            [KeyboardButton(text="💞 Мэтчи"), KeyboardButton(text="⚙️ Настройки")],
            [KeyboardButton(text="📊 Elyx App", web_app=WebAppInfo(url=cfg.webapp_url))],
        ],
        resize_keyboard=True,
    )

# Backward compat alias
MAIN_MENU = main_menu_kb()


def webapp_inline_kb() -> InlineKeyboardMarkup:
    """Inline keyboard with a button that opens the Elyx webapp."""
    cfg = get_settings()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="📊 Открыть Elyx Stats",
                web_app=WebAppInfo(url=cfg.webapp_url),
            )]
        ]
    )

# ── Registration ──────────────────────────────────────────
GENDER_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Парень 🙋‍♂️"), KeyboardButton(text="Девушка 🙋‍♀️")],
        [KeyboardButton(text="Скрыть 🙈")],
    ],
    resize_keyboard=True,
)

GAME_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Valorant"), KeyboardButton(text="CS2")],
        [KeyboardButton(text="Dota 2"), KeyboardButton(text="League of Legends")],
        [KeyboardButton(text="Apex Legends"), KeyboardButton(text="Overwatch 2")],
        [KeyboardButton(text="Fortnite"), KeyboardButton(text="Other")],
    ],
    resize_keyboard=True,
)

CONFIRM_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="✅ Сохранить"), KeyboardButton(text="✏️ Изменить")]],
    resize_keyboard=True,
)

# ── Search ────────────────────────────────────────────────
SEARCH_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❤️ Лайк"), KeyboardButton(text="👎 Скип")],
        [KeyboardButton(text="✉️ Письмо"), KeyboardButton(text="⛔ Стоп")],
    ],
    resize_keyboard=True,
)

# ── Profile ───────────────────────────────────────────────
PROFILE_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Смотреть анкеты"), KeyboardButton(text="🔄 Заполнить заново")],
        [KeyboardButton(text="📷 Изменить фото/видео"), KeyboardButton(text="✏️ Изменить текст")],
        [KeyboardButton(text="🎮 Проверить ранг"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)

# ── Settings ──────────────────────────────────────────────
SETTINGS_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⭐ Premium"), KeyboardButton(text="🆘 Поддержка")],
        [KeyboardButton(text="🎮 Данные аккаунта"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)

ACCOUNT_DATA_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Riot ID"), KeyboardButton(text="Faceit"), KeyboardButton(text="Steam")],
        [KeyboardButton(text="BattleTag"), KeyboardButton(text="Epic Games")],
        [KeyboardButton(text="🔄 Обновить статистику"), KeyboardButton(text="⬅️ Назад")],
    ],
    resize_keyboard=True,
)

ACCOUNT_PROVIDER_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Riot ID"), KeyboardButton(text="Faceit"), KeyboardButton(text="Steam")],
        [KeyboardButton(text="BattleTag"), KeyboardButton(text="Epic Games")],
        [KeyboardButton(text="Пропустить")],
    ],
    resize_keyboard=True,
)

# ── Mood ──────────────────────────────────────────────────
MOOD_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="😌 Chill"), KeyboardButton(text="🔥 Serious")],
        [KeyboardButton(text="😏 Flirty"), KeyboardButton(text="🏆 Duo Ranked")],
        [KeyboardButton(text="💬 Just Chat"), KeyboardButton(text="⏩ Пропустить")],
    ],
    resize_keyboard=True,
)

# ── Green Flags (inline multi-select) ────────────────────
GREEN_FLAG_OPTIONS = [
    "🧘 Спокойный", "🎤 Голосовой", "⏰ Стабильный",
    "😊 Уважительный", "🎯 Целеустремлённый", "🤝 Командный",
    "🌙 Совы", "😂 Весёлый", "🛡 Без токса",
]

DEALBREAKER_OPTIONS = [
    "🗑 Токсичность", "👻 Гостинг", "😤 Грубость",
    "🔇 Молчун", "📵 Не в голос", "🤬 Оскорбления",
]


def green_flags_kb(selected: list[str]) -> InlineKeyboardMarkup:
    """Multi-select inline keyboard for green flags (max 3)."""
    rows = []
    for i in range(0, len(GREEN_FLAG_OPTIONS), 3):
        row = []
        for opt in GREEN_FLAG_OPTIONS[i:i + 3]:
            marker = "✅ " if opt in selected else ""
            row.append(InlineKeyboardButton(
                text=f"{marker}{opt}",
                callback_data=f"gf:{opt}",
            ))
        rows.append(row)
    rows.append([InlineKeyboardButton(text="✅ Готово", callback_data="gf:done")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def dealbreaker_kb() -> InlineKeyboardMarkup:
    """Single-select inline keyboard for dealbreaker."""
    rows = []
    for i in range(0, len(DEALBREAKER_OPTIONS), 3):
        row = []
        for opt in DEALBREAKER_OPTIONS[i:i + 3]:
            row.append(InlineKeyboardButton(text=opt, callback_data=f"db:{opt}"))
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⏩ Пропустить", callback_data="db:skip")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── Notification reactions ────────────────────────────────
def view_like_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="👀 Посмотреть")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def react_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❤️ Лайк"), KeyboardButton(text="👎 Скип")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


# ── Match navigation ─────────────────────────────────────
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


# ── Leaderboard ──────────────────────────────────────────
def leaderboard_nav(page: int, total_pages: int) -> InlineKeyboardMarkup:
    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"lb_page_{page - 1}"))
    buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="lb_idx"))
    if page < total_pages:
        buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"lb_page_{page + 1}"))
    rows = [buttons]
    rows.append([InlineKeyboardButton(text="📊 Моя позиция", callback_data="lb_my_pos")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── First Move Generator (after match) ───────────────────
def first_move_kb(match_user_id: int, options: list[str]) -> InlineKeyboardMarkup:
    """Inline keyboard with 3 suggested first messages after a match."""
    rows = []
    for i, text in enumerate(options):
        rows.append([InlineKeyboardButton(
            text=f"💬 {text[:40]}{'…' if len(text) > 40 else ''}",
            callback_data=f"fm:{match_user_id}:{i}",
        )])
    rows.append([InlineKeyboardButton(text="✍️ Написать своё", callback_data=f"fm:{match_user_id}:custom")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
