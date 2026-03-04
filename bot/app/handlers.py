"""
Bot handlers — full dating UX with green flags, dealbreaker, mood, first move.

All imports and flows: registration (11 steps), search with mood, swipe/like/letter,
matches with pagination, profile editing, settings with smart account linking.
"""

from datetime import datetime, timezone

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from app.api import backend
from app.first_move import generate_first_moves
from app.keyboards import (
    ACCOUNT_DATA_KB,
    ACCOUNT_PROVIDER_KB,
    CONFIRM_KB,
    GAME_KB,
    GENDER_KB,
    MAIN_MENU,
    MOOD_KB,
    PROFILE_KB,
    SEARCH_KB,
    SETTINGS_KB,
    dealbreaker_kb,
    first_move_kb,
    green_flags_kb,
    leaderboard_nav,
    match_username_kb,
    matches_nav,
    react_kb,
    view_like_kb,
    webapp_inline_kb,
)
from app.states import BrowsingState, MatchesState, ProfileEditState, RegistrationState, SettingsState
from app.storage import current_candidates, letters_target, matches_cache, matches_index, pending_reactions, registration_drafts
from app.texts import (
    BIO_HINT,
    DEALBREAKER_HINT,
    GREEN_FLAGS_HINT,
    MATCH_CONGRATS,
    MOOD_HINT,
    NEED_PROFILE,
    NO_CANDIDATES,
    PHOTO_HINT,
    PREMIUM_TEXT,
    ROLE_HINT,
    SETTINGS_TEXT,
    SUPPORT_TEXT,
    TAG_HINT,
    WELCOME,
)

router = Router()

# ── Map game name → provider for auto-linking ────────────
GAME_PROVIDER = {
    "valorant": "riot",
    "cs2": "faceit",
    "dota 2": "steam",
    "league of legends": "riot",
    "apex legends": "steam",
    "overwatch 2": "blizzard",
    "fortnite": "epic",
    "other": None,
}

PROVIDER_PROMPTS = {
    "riot": "Введи свой Riot ID (формат: Nickname#TAG):",
    "faceit": "Введи свой Faceit никнейм (как на faceit.com):",
    "steam": "Введи свой Steam ID (17-значный steam64 или vanity URL):",
    "blizzard": "Введи свой BattleTag (формат: Name#1234):",
    "epic": "Введи свой Epic Games ник:",
}

# Store first-move options in memory for callback handling
_first_move_cache: dict[int, dict] = {}


# ── Profile card builder ─────────────────────────────────

def _profile_card(profile: dict) -> str:
    """Build the profile card text — dating-oriented, emoji-rich."""
    trust_up = profile.get("trust_up", 0)
    trust_down = profile.get("trust_down", 0)
    nickname = profile["nickname"]
    age = profile["age"]
    gender = profile["gender"]
    game = profile["game_name"]
    roles = ", ".join(profile.get("roles", [])) or "—"

    stats = profile.get("stats") or {}
    kd = stats.get("kd")
    wr = stats.get("winrate")
    rank = stats.get("rank_name")
    unified = stats.get("unified_score", 0)
    verified = stats.get("verified", False)
    source_status = stats.get("source_status", "ok")

    is_premium = profile.get("is_premium", False)
    badge = " ⭐" if is_premium else ""

    # Verification icon
    if verified:
        verify = " ✅"
    elif source_status == "error":
        verify = " ⚠️"
    elif source_status in ("notfound", "private"):
        verify = " ❌"
    else:
        verify = ""

    # Stats line — never fake, show "—" or "проверяем…"
    if rank:
        kd_str = f"{kd:.2f}" if kd is not None else "—"
        wr_str = f"{wr:.1f}%" if wr is not None else "—"
        stats_line = f"📊 K/D: {kd_str} | Rank: {rank} | Win%: {wr_str}"
    elif source_status == "ok" and not rank:
        stats_line = "📊 Статистика: проверяем… ⏳"
    else:
        stats_line = "📊 Статистика: —"

    # Score bar
    score_line = ""
    if unified > 0:
        filled = min(10, unified // 1000)
        bar = "▰" * filled + "▱" * (10 - filled)
        score_line = f"🏆 {bar} {unified}/10000{verify}"

    # Green flags / dealbreaker
    green_flags = profile.get("green_flags") or []
    dealbreaker = profile.get("dealbreaker")
    flags_line = ""
    if green_flags:
        flags_line = f"✅ {', '.join(green_flags)}"
    deal_line = ""
    if dealbreaker:
        deal_line = f"🚫 {dealbreaker}"

    # Mood
    mood = profile.get("mood_status")
    mood_map = {
        "chill": "😌 Chill",
        "serious": "🔥 Serious",
        "flirty": "😏 Flirty",
        "duo_ranked": "🏆 Duo Ranked",
        "just_chat": "💬 Just Chat",
    }
    mood_line = f"🎭 {mood_map.get(mood, mood)}" if mood else ""

    bio = profile.get("bio", "")
    tags = profile.get("tags", [])

    lines = [
        f"👤 {nickname}{badge}, {age}, {gender}",
        f"🎮 {game} • {roles}",
        stats_line,
    ]
    if score_line:
        lines.append(score_line)
    lines.append(f"🤝 Trust: 👍 {trust_up} | 🗑 {trust_down}")
    if flags_line:
        lines.append(flags_line)
    if deal_line:
        lines.append(deal_line)
    if tags:
        lines.append(f"🏷 {', '.join(tags[:6])}")
    if mood_line:
        lines.append(mood_line)
    lines.append("")
    lines.append(f"💬 {bio}")

    return "\n".join(lines)


async def _send_profile_card(message: Message, profile: dict, reply_markup=None) -> None:
    """Send profile card with media (photo/video) as caption."""
    card_text = _profile_card(profile)
    media_type = profile.get("media_type")
    media_file_id = profile.get("media_file_id", "")

    try:
        if media_type == "photo" and media_file_id:
            await message.answer_photo(photo=media_file_id, caption=card_text, reply_markup=reply_markup)
        elif media_type == "video" and media_file_id:
            await message.answer_video(video=media_file_id, caption=card_text, reply_markup=reply_markup)
        else:
            await message.answer(card_text, reply_markup=reply_markup)
    except Exception:
        await message.answer(card_text, reply_markup=reply_markup)


async def _notify(bot: Bot, chat_id: int, text: str, reply_markup=None) -> None:
    try:
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    except Exception:
        return


async def _show_next_candidate(message: Message, tg_id: int) -> None:
    data = await backend.get("/search/next", tg_id)
    candidate = data.get("candidate")
    if not candidate:
        await message.answer(NO_CANDIDATES, reply_markup=MAIN_MENU)
        return
    current_candidates[tg_id] = candidate["user_id"]
    await _send_profile_card(message, candidate, reply_markup=SEARCH_KB)


async def _update_profile_partial(tg_id: int, **changes) -> None:
    profile = await backend.get("/profiles/me", tg_id)
    payload = {
        "nickname": profile["nickname"],
        "gender": profile["gender"],
        "age": profile["age"],
        "game_id": profile["game_id"],
        "bio": profile["bio"],
        "media_type": profile["media_type"],
        "media_file_id": profile["media_file_id"],
        "roles": profile.get("roles", []),
        "tags": profile.get("tags", []),
        "green_flags": profile.get("green_flags", []),
        "dealbreaker": profile.get("dealbreaker"),
        "mood_status": profile.get("mood_status"),
    }
    payload.update(changes)
    await backend.put("/profiles/me", tg_id, payload)


def _summary(draft: dict) -> str:
    """Registration summary before saving."""
    account_line = "Не указано"
    prov = draft.get("account_provider")
    ref = draft.get("account_ref")
    if prov and ref:
        account_line = f"{prov}: {ref}"

    gf = ", ".join(draft.get("green_flags", [])) or "—"
    db = draft.get("dealbreaker") or "—"

    return (
        "📋 Проверь анкету:\n\n"
        f"👤 Ник: {draft.get('nickname')}\n"
        f"🧑 Пол: {draft.get('gender')}\n"
        f"🎂 Возраст: {draft.get('age')}\n"
        f"🎮 Роли: {', '.join(draft.get('roles', [])) or '—'}\n"
        f"🏷 Теги: {', '.join(draft.get('tags', [])) or '—'}\n"
        f"✅ Green: {gf}\n"
        f"🚫 Дилбрейкер: {db}\n"
        f"✏️ Описание: {draft.get('bio')}\n"
        f"🎮 Аккаунт: {account_line}\n\n"
        "Всё верно? Жми «Сохранить» или «Изменить»."
    )


# ╔══════════════════════════════════════════════════════════╗
# ║  /start                                                  ║
# ╚══════════════════════════════════════════════════════════╝

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    tg_id = message.from_user.id
    uname = message.from_user.username
    try:
        await backend.get("/profiles/me", tg_id, username=uname)
        await message.answer("С возвращением! 💘", reply_markup=MAIN_MENU)
    except Exception:
        await message.answer(WELCOME)
        await state.set_state(RegistrationState.nickname)
        await message.answer("Шаг 1/11 — Как тебя зовут? Введи никнейм:")


@router.message(Command("app"))
async def cmd_app(message: Message) -> None:
    """Open the Elyx Stats webapp inside Telegram."""
    await message.answer(
        "📊 Открой статистику, лидеров и настройки в одном месте:",
        reply_markup=webapp_inline_kb(),
    )


# ╔══════════════════════════════════════════════════════════╗
# ║  Registration FSM                                        ║
# ╚══════════════════════════════════════════════════════════╝

@router.message(RegistrationState.nickname)
async def reg_nickname(message: Message, state: FSMContext) -> None:
    nick = (message.text or "").strip()
    if len(nick) < 2 or len(nick) > 64:
        await message.answer("❌ Никнейм от 2 до 64 символов. Попробуй ещё:")
        return
    registration_drafts[message.from_user.id]["nickname"] = nick
    await state.set_state(RegistrationState.gender)
    await message.answer("Шаг 2/11 — Укажи пол:", reply_markup=GENDER_KB)


@router.message(RegistrationState.gender)
async def reg_gender(message: Message, state: FSMContext) -> None:
    gender_map = {
        "парень 🙋‍♂️": "Парень",
        "девушка 🙋‍♀️": "Девушка",
        "скрыть 🙈": "Скрыто",
    }
    picked = gender_map.get((message.text or "").strip().lower())
    if not picked:
        await message.answer("Выбери пол кнопкой ⬇️")
        return
    registration_drafts[message.from_user.id]["gender"] = picked
    await state.set_state(RegistrationState.age)
    await message.answer("Шаг 3/11 — Сколько тебе лет? (14–60)", reply_markup=ReplyKeyboardRemove())


@router.message(RegistrationState.age)
async def reg_age(message: Message, state: FSMContext) -> None:
    txt = (message.text or "").strip()
    if not txt.isdigit() or not (14 <= int(txt) <= 60):
        await message.answer("❌ Возраст должен быть числом от 14 до 60")
        return
    registration_drafts[message.from_user.id]["age"] = int(txt)
    await state.set_state(RegistrationState.game)
    await message.answer("Шаг 4/11 — Выбери основную игру:", reply_markup=GAME_KB)


@router.message(RegistrationState.game)
async def reg_game(message: Message, state: FSMContext) -> None:
    games = await backend.get("/games", message.from_user.id)
    by_name = {g["name"].lower(): g for g in games}
    picked = by_name.get((message.text or "").strip().lower())
    if not picked:
        await message.answer("Выбери игру кнопкой ⬇️")
        return

    tg_id = message.from_user.id
    registration_drafts[tg_id]["game_id"] = picked["id"]
    registration_drafts[tg_id]["game_name"] = picked["name"]

    # Auto-detect provider for account linking later
    provider = GAME_PROVIDER.get(picked["name"].lower())
    registration_drafts[tg_id]["account_provider"] = provider

    await state.set_state(RegistrationState.roles)
    await message.answer(f"Шаг 5/11 — {ROLE_HINT}", reply_markup=ReplyKeyboardRemove())


@router.message(RegistrationState.roles)
async def reg_roles(message: Message, state: FSMContext) -> None:
    roles = [x.strip() for x in (message.text or "").split(",") if x.strip()]
    registration_drafts[message.from_user.id]["roles"] = roles[:8]
    await state.set_state(RegistrationState.tags)
    await message.answer(f"Шаг 6/11 — {TAG_HINT}")


@router.message(RegistrationState.tags)
async def reg_tags(message: Message, state: FSMContext) -> None:
    tags = [x.strip().lower() for x in (message.text or "").split(",") if x.strip()]
    registration_drafts[message.from_user.id]["tags"] = tags[:12]
    # Initialize green_flags selection
    registration_drafts[message.from_user.id]["green_flags"] = []
    await state.set_state(RegistrationState.green_flags)
    await message.answer(
        f"Шаг 7/11 — {GREEN_FLAGS_HINT}",
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer("Выбери флаги:", reply_markup=green_flags_kb([]))


@router.callback_query(F.data.startswith("gf:"))
async def reg_green_flags_cb(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle green flags multi-select inline buttons."""
    current = await state.get_state()
    if current != RegistrationState.green_flags.state:
        await callback.answer()
        return

    tg_id = callback.from_user.id
    data = callback.data[3:]  # remove "gf:" prefix

    if data == "done":
        # Move to dealbreaker
        await state.set_state(RegistrationState.dealbreaker)
        await callback.message.answer(
            f"Шаг 8/11 — {DEALBREAKER_HINT}",
            reply_markup=dealbreaker_kb(),
        )
        await callback.answer()
        return

    draft = registration_drafts[tg_id]
    selected = draft.get("green_flags", [])

    if data in selected:
        selected.remove(data)
    elif len(selected) < 3:
        selected.append(data)
    else:
        await callback.answer("Максимум 3 флага! Убери один чтобы добавить другой.", show_alert=True)
        return

    draft["green_flags"] = selected
    await callback.message.edit_reply_markup(reply_markup=green_flags_kb(selected))
    await callback.answer(f"Выбрано: {len(selected)}/3")


@router.callback_query(F.data.startswith("db:"))
async def reg_dealbreaker_cb(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle dealbreaker single-select inline buttons."""
    current = await state.get_state()
    if current != RegistrationState.dealbreaker.state:
        await callback.answer()
        return

    tg_id = callback.from_user.id
    data = callback.data[3:]  # remove "db:" prefix

    if data == "skip":
        registration_drafts[tg_id]["dealbreaker"] = None
    else:
        registration_drafts[tg_id]["dealbreaker"] = data

    await state.set_state(RegistrationState.bio)
    await callback.message.answer(f"Шаг 9/11 — {BIO_HINT}")
    await callback.answer()


@router.message(RegistrationState.bio)
async def reg_bio(message: Message, state: FSMContext) -> None:
    txt = (message.text or "").strip()
    if len(txt) < 10 or len(txt) > 400:
        await message.answer("❌ Описание должно быть от 10 до 400 символов")
        return
    registration_drafts[message.from_user.id]["bio"] = txt
    await state.set_state(RegistrationState.media)
    await message.answer(f"Шаг 10/11 — {PHOTO_HINT}")


@router.message(RegistrationState.media)
async def reg_media(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    draft = registration_drafts[tg_id]

    if message.photo:
        draft["media_type"] = "photo"
        draft["media_file_id"] = message.photo[-1].file_id
    elif message.video:
        draft["media_type"] = "video"
        draft["media_file_id"] = message.video.file_id
    else:
        await message.answer("Нужно фото или видео 📸")
        return

    # Smart account linking — auto-detect from game
    provider = draft.get("account_provider")
    if provider:
        prompt = PROVIDER_PROMPTS.get(provider, "Введи ID аккаунта:")
        await state.set_state(RegistrationState.account_ref)
        await message.answer(
            f"Шаг 11/11 — Привяжем аккаунт для верификации ранга.\n\n{prompt}",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        # Game "Other" — no account linking needed
        await state.set_state(RegistrationState.confirm)
        await message.answer(_summary(draft), reply_markup=CONFIRM_KB)


@router.message(RegistrationState.account_ref)
async def reg_account_ref(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    val = (message.text or "").strip()
    draft = registration_drafts[tg_id]
    provider = draft.get("account_provider")

    # Format validation
    if provider == "riot" and "#" not in val:
        await message.answer("❌ Riot ID должен содержать #\nПример: Nickname#TAG")
        return
    if provider == "steam":
        # Accept 17-digit steam64 or vanity string
        if val.isdigit() and len(val) != 17:
            await message.answer("❌ Steam64 ID должен быть 17 цифр.\nИли введи vanity URL (буквы).")
            return

    if len(val) < 2 or len(val) > 128:
        await message.answer("❌ ID должен быть от 2 до 128 символов")
        return

    draft["account_ref"] = val
    await state.set_state(RegistrationState.confirm)
    await message.answer(_summary(draft), reply_markup=CONFIRM_KB)


@router.message(RegistrationState.confirm, F.text == "✅ Сохранить")
async def reg_save(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    uname = message.from_user.username
    draft = registration_drafts.get(tg_id, {})

    payload = {
        "nickname": draft.get("nickname", ""),
        "gender": draft.get("gender", "Скрыто"),
        "age": draft.get("age", 18),
        "game_id": draft.get("game_id"),
        "bio": draft.get("bio", ""),
        "media_type": draft.get("media_type", "photo"),
        "media_file_id": draft.get("media_file_id", ""),
        "roles": draft.get("roles", []),
        "tags": draft.get("tags", []),
        "green_flags": draft.get("green_flags", []),
        "dealbreaker": draft.get("dealbreaker"),
        "mood_status": None,
    }
    await backend.put("/profiles/me", tg_id, payload, username=uname)

    # Link account if provided
    prov = draft.get("account_provider")
    ref = draft.get("account_ref")
    if prov and ref:
        await backend.post(f"/account/link/{prov}", tg_id, {"account_ref": ref})
        try:
            result = await backend.post("/account/refresh-stats", tg_id)
            if result.get("ok"):
                rank = result.get("rank") or "—"
                kd = result.get("kd")
                wr = result.get("winrate")
                score = result.get("unified_score", 0)
                kd_str = f"{kd:.2f}" if kd else "—"
                wr_str = f"{wr:.1f}%" if wr else "—"
                await message.answer(
                    f"✅ Аккаунт подтверждён!\n"
                    f"🎮 {draft.get('game_name', '')}\n"
                    f"📊 K/D: {kd_str} | Rank: {rank} | Win%: {wr_str}\n"
                    f"🏆 Score: {score}"
                )
            else:
                error = result.get("error", "")
                if error == "api_fetch_failed":
                    await message.answer("⏳ Проверяем аккаунт… Обычно 10–60 сек. Я напишу, когда будет готово.")
                else:
                    await message.answer("📊 Статистика подтянется автоматически.")
        except Exception:
            await message.answer("📊 Статистика подтянется автоматически.")

    registration_drafts.pop(tg_id, None)
    await state.clear()
    await message.answer("Анкета сохранена! 🎉\nТеперь можешь искать людей 💘", reply_markup=MAIN_MENU)


@router.message(RegistrationState.confirm, F.text == "✏️ Изменить")
async def reg_edit(message: Message, state: FSMContext) -> None:
    await state.set_state(RegistrationState.nickname)
    await message.answer("Ок, начнём заново! Введи никнейм:", reply_markup=ReplyKeyboardRemove())


# ╔══════════════════════════════════════════════════════════╗
# ║  Main Menu                                               ║
# ╚══════════════════════════════════════════════════════════╝

@router.message(F.text == "🏠 Главное меню")
async def main_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Главное меню 💘", reply_markup=MAIN_MENU)


# ╔══════════════════════════════════════════════════════════╗
# ║  Search — with mood selection                            ║
# ╚══════════════════════════════════════════════════════════╝

@router.message(F.text.in_(["🔍 Поиск", "🔍 Смотреть анкеты"]))
async def search_mode(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    try:
        await backend.get("/profiles/me", tg_id)
    except Exception:
        await message.answer(NEED_PROFILE)
        return
    # Ask mood before starting search
    await state.set_state(BrowsingState.mood)
    await message.answer(MOOD_HINT, reply_markup=MOOD_KB)


MOOD_MAP = {
    "😌 chill": "chill",
    "🔥 serious": "serious",
    "😏 flirty": "flirty",
    "🏆 duo ranked": "duo_ranked",
    "💬 just chat": "just_chat",
}


@router.message(BrowsingState.mood)
async def set_mood_and_search(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    text = (message.text or "").strip().lower()

    if text != "⏩ пропустить":
        mood = MOOD_MAP.get(text)
        if mood:
            # Update mood via partial profile update
            try:
                await _update_profile_partial(tg_id, mood_status=mood)
            except Exception:
                pass

    await state.set_state(BrowsingState.active)
    await message.answer("🔍 Ищу анкеты для тебя…", reply_markup=SEARCH_KB)
    await _show_next_candidate(message, tg_id)


# ── Swipes ────────────────────────────────────────────────

@router.message(BrowsingState.active, F.text == "❤️ Лайк")
async def like_candidate(message: Message, bot: Bot) -> None:
    tg_id = message.from_user.id
    target = current_candidates.get(tg_id)
    if not target:
        await _show_next_candidate(message, tg_id)
        return

    result = await backend.post("/actions/like", tg_id, {"target_user_id": target})
    me = await backend.get("/profiles/me", tg_id)
    them = await backend.get(f"/profiles/{target}", tg_id)

    if result.get("match_created"):
        # MATCH! Send congrats + first move suggestions to both
        await message.answer(MATCH_CONGRATS, reply_markup=MAIN_MENU)

        # Generate first move options
        options = generate_first_moves(me, them)
        _first_move_cache[tg_id] = {"options": options, "target_tg_id": them["tg_id"], "target_name": them["nickname"]}
        await message.answer(
            "💡 Хочешь начать разговор? Выбери сообщение:",
            reply_markup=first_move_kb(them["user_id"], options),
        )

        # Notify the other person
        their_options = generate_first_moves(them, me)
        _first_move_cache[them["tg_id"]] = {"options": their_options, "target_tg_id": tg_id, "target_name": me["nickname"]}
        await _notify(bot, them["tg_id"], MATCH_CONGRATS)
        await _notify(
            bot, them["tg_id"],
            "💡 Хочешь начать разговор? Выбери сообщение:",
            reply_markup=first_move_kb(me["user_id"], their_options),
        )
    else:
        # Notify target about the like
        pending_reactions[them["tg_id"]] = me["user_id"]
        await _notify(
            bot, them["tg_id"],
            f"💘 У тебя новый лайк! Кто-то заинтересовался твоей анкетой",
            reply_markup=view_like_kb(),
        )

    await _show_next_candidate(message, tg_id)


@router.message(BrowsingState.active, F.text == "👎 Скип")
async def skip_candidate(message: Message) -> None:
    tg_id = message.from_user.id
    target = current_candidates.get(tg_id)
    if target:
        await backend.post("/actions/skip", tg_id, {"target_user_id": target})
    await _show_next_candidate(message, tg_id)


@router.message(BrowsingState.active, F.text == "✉️ Письмо")
async def letter_start(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    target = current_candidates.get(tg_id)
    if not target:
        await _show_next_candidate(message, tg_id)
        return
    letters_target[tg_id] = target
    await state.set_state(BrowsingState.letter_text)
    await message.answer("✉️ Напиши сообщение этому человеку (1–500 символов):", reply_markup=ReplyKeyboardRemove())


@router.message(BrowsingState.letter_text)
async def letter_send(message: Message, state: FSMContext, bot: Bot) -> None:
    txt = (message.text or "").strip()
    if len(txt) > 500:
        await message.answer("❌ Слишком длинно, максимум 500 символов")
        return

    tg_id = message.from_user.id
    target = letters_target.get(tg_id)
    if not target:
        await state.set_state(BrowsingState.active)
        await _show_next_candidate(message, tg_id)
        return

    await backend.post("/actions/letter", tg_id, {"target_user_id": target, "text": txt})

    me = await backend.get("/profiles/me", tg_id)
    them = await backend.get(f"/profiles/{target}", tg_id)

    pending_reactions[them["tg_id"]] = me["user_id"]
    await _notify(bot, them["tg_id"], "💌 Тебе оставили письмо:")
    await _notify(bot, them["tg_id"], f"«{txt}»", reply_markup=react_kb())

    await message.answer("Письмо отправлено! 💌", reply_markup=SEARCH_KB)
    await state.set_state(BrowsingState.active)
    await _show_next_candidate(message, tg_id)


@router.message(BrowsingState.active, F.text == "⛔ Стоп")
async def stop_search(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Поиск остановлен ✋", reply_markup=MAIN_MENU)


# ── First Move callback ──────────────────────────────────

@router.callback_query(F.data.startswith("fm:"))
async def first_move_cb(callback: CallbackQuery, bot: Bot) -> None:
    """Handle first move message selection after a match."""
    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.answer()
        return

    tg_id = callback.from_user.id
    cache = _first_move_cache.get(tg_id)
    if not cache:
        await callback.answer("Время истекло, напиши сам 😉")
        return

    choice = parts[2]
    target_tg_id = cache["target_tg_id"]
    target_name = cache["target_name"]

    if choice == "custom":
        await callback.message.answer(f"✍️ Напиши своё сообщение для {target_name}:")
        await callback.answer()
        return

    try:
        idx = int(choice)
        text = cache["options"][idx]
    except (ValueError, IndexError):
        await callback.answer("Ошибка")
        return

    # Send the chosen message to the match partner
    await _notify(bot, target_tg_id, f"💬 Сообщение от мэтча:\n\n«{text}»")
    await callback.message.answer(f"✅ Отправлено {target_name}!")
    _first_move_cache.pop(tg_id, None)
    await callback.answer()


# ╔══════════════════════════════════════════════════════════╗
# ║  Notification reactions (view like, react)               ║
# ╚══════════════════════════════════════════════════════════╝

@router.message(F.text == "👀 Посмотреть")
async def view_like_sender(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    sender_user_id = pending_reactions.pop(tg_id, None)
    if not sender_user_id:
        await message.answer("Нет новых лайков 😔", reply_markup=MAIN_MENU)
        return
    try:
        profile = await backend.get(f"/profiles/{sender_user_id}", tg_id)
    except Exception:
        await message.answer("Анкета недоступна", reply_markup=MAIN_MENU)
        return

    pending_reactions[tg_id] = sender_user_id
    await state.set_state(BrowsingState.reacting)
    await _send_profile_card(message, profile, reply_markup=react_kb())


@router.message(BrowsingState.reacting, F.text == "❤️ Лайк")
async def react_like(message: Message, state: FSMContext, bot: Bot) -> None:
    tg_id = message.from_user.id
    target = pending_reactions.pop(tg_id, None)
    if not target:
        await state.clear()
        await message.answer("Главное меню 💘", reply_markup=MAIN_MENU)
        return

    result = await backend.post("/actions/like", tg_id, {"target_user_id": target})
    if result.get("match_created"):
        me = await backend.get("/profiles/me", tg_id)
        them = await backend.get(f"/profiles/{target}", tg_id)

        await message.answer(MATCH_CONGRATS, reply_markup=MAIN_MENU)

        # First move for me
        options = generate_first_moves(me, them)
        _first_move_cache[tg_id] = {"options": options, "target_tg_id": them["tg_id"], "target_name": them["nickname"]}
        await message.answer(
            "💡 Хочешь начать разговор? Выбери сообщение:",
            reply_markup=first_move_kb(them["user_id"], options),
        )

        # First move for them
        their_options = generate_first_moves(them, me)
        _first_move_cache[them["tg_id"]] = {"options": their_options, "target_tg_id": tg_id, "target_name": me["nickname"]}
        await _notify(bot, them["tg_id"], MATCH_CONGRATS)
        await _notify(
            bot, them["tg_id"],
            "💡 Хочешь начать разговор?",
            reply_markup=first_move_kb(me["user_id"], their_options),
        )
    else:
        await message.answer("Лайк отправлен! 💘", reply_markup=MAIN_MENU)
    await state.clear()


@router.message(BrowsingState.reacting, F.text == "👎 Скип")
async def react_skip(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    target = pending_reactions.pop(tg_id, None)
    if target:
        await backend.post("/actions/skip", tg_id, {"target_user_id": target})
    await state.clear()
    await message.answer("Окей, идём дальше 😌", reply_markup=MAIN_MENU)


# ╔══════════════════════════════════════════════════════════╗
# ║  My Profile                                              ║
# ╚══════════════════════════════════════════════════════════╝

@router.message(F.text == "👤 Мой профиль")
async def my_profile(message: Message) -> None:
    tg_id = message.from_user.id
    try:
        profile = await backend.get("/profiles/me", tg_id)
    except Exception:
        await message.answer(NEED_PROFILE)
        return
    await _send_profile_card(message, profile, reply_markup=PROFILE_KB)


@router.message(F.text == "🔄 Заполнить заново")
async def refill_profile(message: Message, state: FSMContext) -> None:
    await state.set_state(RegistrationState.nickname)
    await message.answer("Ок, начнём заново! Введи никнейм:", reply_markup=ReplyKeyboardRemove())


@router.message(F.text == "📷 Изменить фото/видео")
async def change_media_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(ProfileEditState.media)
    await message.answer("📸 Пришли новое фото или видео:", reply_markup=ReplyKeyboardRemove())


@router.message(F.text == "✏️ Изменить текст")
async def change_bio_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(ProfileEditState.bio)
    await message.answer("✏️ Пришли новый текст анкеты (10–400):", reply_markup=ReplyKeyboardRemove())


@router.message(F.text == "🎮 Проверить ранг")
async def recheck_rank(message: Message) -> None:
    import httpx
    tg_id = message.from_user.id
    await message.answer("🔄 Обновляю статистику…")
    try:
        result = await backend.post("/account/refresh-stats", tg_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            detail = exc.response.json().get("detail", "")
            await message.answer(f"⏳ {detail}", reply_markup=PROFILE_KB)
            return
        raise

    if result.get("ok"):
        rank = result.get("rank") or "—"
        rp = result.get("rank_points")
        score = result.get("unified_score", 0)
        kd = result.get("kd")
        wr = result.get("winrate")
        kd_str = f"{kd:.2f}" if kd else "—"
        wr_str = f"{wr:.1f}%" if wr else "—"
        rp_str = f" ({rp} RR)" if rp else ""
        await message.answer(
            f"✅ Статистика обновлена!\n"
            f"📊 Rank: {rank}{rp_str}\n"
            f"K/D: {kd_str} | Win%: {wr_str}\n"
            f"🏆 Score: {score}",
            reply_markup=PROFILE_KB,
        )
    else:
        error = result.get("error", "")
        label = result.get("label", "")
        msg_map = {
            "no_profile": "Сначала создай анкету",
            "no_linked_account": f"Привяжи аккаунт: {label}",
            "api_fetch_failed": "❌ Не удалось получить данные. Проверь ID и попробуй снова.",
            "unsupported_game": "Игра пока не поддерживается для аналитики",
        }
        await message.answer(f"⚠️ {msg_map.get(error, error)}", reply_markup=PROFILE_KB)


@router.message(ProfileEditState.bio)
async def save_new_bio(message: Message, state: FSMContext) -> None:
    bio = (message.text or "").strip()
    if len(bio) < 10 or len(bio) > 400:
        await message.answer("❌ Описание должно быть от 10 до 400 символов")
        return
    await _update_profile_partial(message.from_user.id, bio=bio)
    await state.clear()
    await message.answer("✅ Текст обновлён!", reply_markup=MAIN_MENU)


@router.message(ProfileEditState.media)
async def save_new_media(message: Message, state: FSMContext) -> None:
    if message.photo:
        mt, fid = "photo", message.photo[-1].file_id
    elif message.video:
        mt, fid = "video", message.video.file_id
    else:
        await message.answer("Нужно фото или видео 📸")
        return
    await _update_profile_partial(message.from_user.id, media_type=mt, media_file_id=fid)
    await state.clear()
    await message.answer("✅ Медиа обновлено!", reply_markup=MAIN_MENU)


# ╔══════════════════════════════════════════════════════════╗
# ║  Matches with pagination                                 ║
# ╚══════════════════════════════════════════════════════════╝

@router.message(F.text == "💞 Мэтчи")
async def matches_open(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    rows = await backend.get("/matches", tg_id)
    if not rows:
        await message.answer("Пока нет мэтчей 😔\nПродолжай свайпать! 💪", reply_markup=MAIN_MENU)
        return

    matches_cache[tg_id] = rows
    matches_index[tg_id] = 0
    await state.set_state(MatchesState.viewing)
    await _show_match_card(message, tg_id)


async def _show_match_card(message: Message, tg_id: int) -> None:
    rows = matches_cache.get(tg_id, [])
    idx = matches_index.get(tg_id, 0)
    if not rows:
        await message.answer("Нет мэтчей 😔", reply_markup=MAIN_MENU)
        return
    item = rows[idx]
    username = item.get("username")
    user_id = item.get("user_id")

    try:
        full_profile = await backend.get(f"/profiles/{user_id}", tg_id)
        await _send_profile_card(message, full_profile, reply_markup=match_username_kb(username))
    except Exception:
        text = f"👤 {item['nickname']} • {item['game_name']}"
        await message.answer(text, reply_markup=match_username_kb(username))

    await message.answer("📖 Навигация:", reply_markup=matches_nav(idx + 1, len(rows)))


@router.callback_query(F.data.in_(["match_prev", "match_next", "match_idx"]))
async def match_nav_cb(callback: CallbackQuery) -> None:
    tg_id = callback.from_user.id
    rows = matches_cache.get(tg_id, [])
    if not rows:
        await callback.answer("Нет мэтчей")
        return

    idx = matches_index.get(tg_id, 0)
    if callback.data == "match_prev":
        idx = (idx - 1) % len(rows)
    elif callback.data == "match_next":
        idx = (idx + 1) % len(rows)

    matches_index[tg_id] = idx
    item = rows[idx]
    username = item.get("username")
    username_text = f"@{username}" if username else ""
    text = f"👤 {item['nickname']} • {item['game_name']}"
    if username_text:
        text += f"\n{username_text}"

    await callback.message.edit_text(text, reply_markup=matches_nav(idx + 1, len(rows)))
    await callback.answer()


# ╔══════════════════════════════════════════════════════════╗
# ║  Settings                                                ║
# ╚══════════════════════════════════════════════════════════╝

@router.message(F.text == "⚙️ Настройки")
async def settings_menu(message: Message, state: FSMContext) -> None:
    await state.set_state(SettingsState.menu)
    await message.answer(SETTINGS_TEXT, reply_markup=SETTINGS_KB)


@router.message(F.text == "🆘 Поддержка")
async def support(message: Message) -> None:
    await message.answer(SUPPORT_TEXT, reply_markup=SETTINGS_KB)


@router.message(F.text == "🎮 Данные аккаунта")
async def account_data(message: Message, state: FSMContext) -> None:
    await state.set_state(SettingsState.menu)
    await message.answer("🎮 Привязка аккаунтов:", reply_markup=ACCOUNT_DATA_KB)


@router.message(F.text == "Riot ID")
async def riot_start(message: Message, state: FSMContext) -> None:
    await state.set_state(SettingsState.riot)
    await message.answer("Введи Riot ID (Nickname#TAG):", reply_markup=ReplyKeyboardRemove())


@router.message(SettingsState.riot)
async def riot_save(message: Message, state: FSMContext) -> None:
    ref = (message.text or "").strip()
    if "#" not in ref:
        await message.answer("❌ Riot ID должен содержать #\nПример: Nickname#TAG")
        return
    await backend.post("/account/link/riot", message.from_user.id, {"account_ref": ref})
    await state.set_state(SettingsState.menu)
    await message.answer("✅ Riot ID сохранён!", reply_markup=ACCOUNT_DATA_KB)


@router.message(F.text == "Faceit")
async def faceit_start(message: Message, state: FSMContext) -> None:
    await state.set_state(SettingsState.faceit)
    await message.answer("Введи свой Faceit никнейм (как на faceit.com):", reply_markup=ReplyKeyboardRemove())


@router.message(SettingsState.faceit)
async def faceit_save(message: Message, state: FSMContext) -> None:
    ref = (message.text or "").strip()
    if len(ref) < 2:
        await message.answer("Никнейм слишком короткий")
        return
    await backend.post("/account/link/faceit", message.from_user.id, {"account_ref": ref})
    await state.set_state(SettingsState.menu)
    await message.answer("Faceit сохранён ✅", reply_markup=ACCOUNT_DATA_KB)


@router.message(F.text == "Steam")
async def steam_start(message: Message, state: FSMContext) -> None:
    await state.set_state(SettingsState.steam)
    await message.answer("Введи Steam ID (steam64 или vanity URL):", reply_markup=ReplyKeyboardRemove())


@router.message(SettingsState.steam)
async def steam_save(message: Message, state: FSMContext) -> None:
    ref = (message.text or "").strip()
    if len(ref) < 2:
        await message.answer("❌ Steam ID слишком короткий")
        return
    await backend.post("/account/link/steam", message.from_user.id, {"account_ref": ref})
    await state.set_state(SettingsState.menu)
    await message.answer("✅ Steam сохранён!", reply_markup=ACCOUNT_DATA_KB)


@router.message(F.text == "BattleTag")
async def battletag_start(message: Message, state: FSMContext) -> None:
    await state.set_state(SettingsState.blizzard)
    await message.answer("Введи BattleTag (Name#1234):", reply_markup=ReplyKeyboardRemove())


@router.message(SettingsState.blizzard)
async def battletag_save(message: Message, state: FSMContext) -> None:
    ref = (message.text or "").strip()
    if len(ref) < 2:
        await message.answer("❌ BattleTag слишком короткий")
        return
    await backend.post("/account/link/blizzard", message.from_user.id, {"account_ref": ref})
    await state.set_state(SettingsState.menu)
    await message.answer("✅ BattleTag сохранён!", reply_markup=ACCOUNT_DATA_KB)


@router.message(F.text == "Epic Games")
async def epic_start(message: Message, state: FSMContext) -> None:
    await state.set_state(SettingsState.epic)
    await message.answer("Введи Epic Games ник:", reply_markup=ReplyKeyboardRemove())


@router.message(SettingsState.epic)
async def epic_save(message: Message, state: FSMContext) -> None:
    ref = (message.text or "").strip()
    if len(ref) < 2:
        await message.answer("❌ Ник слишком короткий")
        return
    await backend.post("/account/link/epic", message.from_user.id, {"account_ref": ref})
    await state.set_state(SettingsState.menu)
    await message.answer("✅ Epic Games сохранён!", reply_markup=ACCOUNT_DATA_KB)


@router.message(F.text == "🔄 Обновить статистику")
async def refresh_stats(message: Message) -> None:
    import httpx

    await message.answer("🔄 Обновляю статистику…")
    try:
        result = await backend.post("/account/refresh-stats", message.from_user.id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            detail = exc.response.json().get("detail", "")
            await message.answer(f"⏳ {detail}", reply_markup=ACCOUNT_DATA_KB)
            return
        raise

    if result.get("ok"):
        rank = result.get("rank") or "—"
        score = result.get("unified_score", 0)
        kd = result.get("kd")
        wr = result.get("winrate")
        kd_str = f"{kd:.2f}" if kd else "—"
        wr_str = f"{wr:.1f}%" if wr else "—"
        await message.answer(
            f"✅ Обновлено!\nRank: {rank}\nK/D: {kd_str} | Win%: {wr_str}\n🏆 Score: {score}",
            reply_markup=ACCOUNT_DATA_KB,
        )
    else:
        error = result.get("error", "unknown")
        label = result.get("label") or result.get("provider", "")
        msg_map = {
            "no_profile": "Сначала создай анкету",
            "no_linked_account": f"Привяжи аккаунт: {label}",
            "api_fetch_failed": "❌ Не удалось получить данные. Проверь ID и попробуй снова.",
            "unsupported_game": f"Игра «{result.get('game')}» пока не поддерживается",
        }
        await message.answer(f"⚠️ {msg_map.get(error, error)}", reply_markup=ACCOUNT_DATA_KB)


@router.message(F.text == "⬅️ Назад")
async def back_settings(message: Message, state: FSMContext) -> None:
    await state.set_state(SettingsState.menu)
    await message.answer(SETTINGS_TEXT, reply_markup=SETTINGS_KB)


# ── Premium ───────────────────────────────────────────────

@router.message(F.text == "⭐ Premium")
async def premium_info(message: Message) -> None:
    try:
        status = await backend.get("/premium/status", message.from_user.id)
        if status.get("is_premium"):
            days = status.get("days_left", 0)
            await message.answer(
                f"⭐ У тебя Premium!\n"
                f"Осталось дней: {days}\n\n"
                f"💎 Безлимитные лайки и письма\n"
                f"🚀 Приоритет в поиске\n"
                f"⭐ Значок в анкете\n"
                f"👁 Видеть кто лайкнул",
                reply_markup=SETTINGS_KB,
            )
        else:
            await message.answer(PREMIUM_TEXT, reply_markup=SETTINGS_KB)
    except Exception:
        await message.answer(PREMIUM_TEXT, reply_markup=SETTINGS_KB)


# ── Leaderboard ───────────────────────────────────────────

@router.message(F.text == "Лидерборд")
async def leaderboard_cmd(message: Message) -> None:
    tg_id = message.from_user.id
    try:
        profile = await backend.get("/profiles/me", tg_id)
    except Exception:
        await message.answer(NEED_PROFILE)
        return

    game_id = profile.get("game_id")
    game_name = profile.get("game_name", "")
    data = await backend.get(f"/leaderboard/{game_id}?offset=0&limit=10", tg_id)

    entries = data.get("entries", [])
    total = data.get("total", 0)
    if not entries:
        await message.answer("🏆 Лидерборд пуст. Будь первым!", reply_markup=MAIN_MENU)
        return

    lines = [f"🏆 Лидерборд — {game_name}\n"]
    for e in entries:
        pos = e.get("position", "?")
        nick = e.get("nickname", "?")
        score = e.get("unified_score", 0)
        rank = e.get("rank_name") or "—"
        lines.append(f"{pos}. {nick} — {rank} ({score})")

    total_pages = max(1, (total + 9) // 10)
    await message.answer("\n".join(lines), reply_markup=leaderboard_nav(1, total_pages))


@router.callback_query(F.data.startswith("lb_page_"))
async def leaderboard_page_cb(callback: CallbackQuery) -> None:
    tg_id = callback.from_user.id
    page = int(callback.data.replace("lb_page_", ""))
    offset = (page - 1) * 10

    try:
        profile = await backend.get("/profiles/me", tg_id)
    except Exception:
        await callback.answer("Нет профиля")
        return

    game_id = profile.get("game_id")
    game_name = profile.get("game_name", "")
    data = await backend.get(f"/leaderboard/{game_id}?offset={offset}&limit=10", tg_id)

    entries = data.get("entries", [])
    total = data.get("total", 0)
    total_pages = max(1, (total + 9) // 10)

    lines = [f"🏆 Лидерборд — {game_name}\n"]
    for e in entries:
        pos = e.get("position", "?")
        nick = e.get("nickname", "?")
        score = e.get("unified_score", 0)
        rank = e.get("rank_name") or "—"
        lines.append(f"{pos}. {nick} — {rank} ({score})")

    await callback.message.edit_text("\n".join(lines), reply_markup=leaderboard_nav(page, total_pages))
    await callback.answer()


@router.callback_query(F.data == "lb_my_pos")
async def leaderboard_my_pos_cb(callback: CallbackQuery) -> None:
    tg_id = callback.from_user.id
    try:
        profile = await backend.get("/profiles/me", tg_id)
    except Exception:
        await callback.answer("Нет профиля")
        return

    game_id = profile.get("game_id")
    data = await backend.get(f"/leaderboard/{game_id}/me", tg_id)
    pos = data.get("position")
    if pos:
        await callback.answer(f"📊 Твоя позиция: #{pos.get('position', '?')} (Score: {pos.get('unified_score', 0)})", show_alert=True)
    else:
        await callback.answer("Ты ещё не в рейтинге. Привяжи аккаунт и обнови статистику!", show_alert=True)
