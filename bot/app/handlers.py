from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from app.api import backend
from app.keyboards import (
    ACCOUNT_DATA_KB,
    CONFIRM_KB,
    GAME_KB,
    GENDER_KB,
    MAIN_MENU,
    PROFILE_KB,
    SEARCH_KB,
    SETTINGS_KB,
    matches_nav,
)
from app.states import BrowsingState, MatchesState, ProfileEditState, RegistrationState, SettingsState
from app.storage import current_candidates, letters_target, matches_cache, matches_index, registration_drafts
from app.texts import NEED_PROFILE, ROLE_HINT, SETTINGS_TEXT, TAG_HINT, WELCOME

router = Router()


def _profile_card(profile: dict) -> str:
    stats = profile.get("stats") or {}
    kd = stats.get("kd")
    wr = stats.get("winrate")
    rank = stats.get("rank_name")
    return (
        f"🎮 {profile['nickname']} ({profile['age']}, {profile['gender']})\n"
        f"Game: {profile['game_name']}\n"
        f"Roles: {', '.join(profile.get('roles', [])) or '-'}\n"
        f"Tags: {', '.join(profile.get('tags', [])) or '-'}\n"
        f"Rank: {rank or '-'} | KD: {kd if kd is not None else '-'} | WR: {wr if wr is not None else '-'}\n"
        f"Trust: 👍 {profile['trust_up']} | 🗑 {profile['trust_down']}\n\n"
        f"{profile['bio']}"
    )


async def _show_next_candidate(message: Message, tg_id: int) -> None:
    data = await backend.get("/search/next", tg_id)
    candidate = data.get("candidate")
    if not candidate:
        await message.answer("Кандидаты закончились. Попробуй позже.", reply_markup=MAIN_MENU)
        return

    current_candidates[tg_id] = candidate["user_id"]
    await message.answer(_profile_card(candidate), reply_markup=SEARCH_KB)


async def _update_profile_partial(tg_id: int, **changes: str) -> None:
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
    }
    payload.update(changes)
    await backend.put("/profiles/me", tg_id, payload)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    tg_id = message.from_user.id

    try:
        await backend.get("/profiles/me", tg_id)
        await message.answer("С возвращением!", reply_markup=MAIN_MENU)
    except Exception:
        await message.answer(WELCOME)
        await state.set_state(RegistrationState.nickname)
        await message.answer("Введите никнейм")


@router.message(RegistrationState.nickname)
async def reg_nickname(message: Message, state: FSMContext) -> None:
    registration_drafts[message.from_user.id]["nickname"] = message.text.strip()
    await state.set_state(RegistrationState.gender)
    await message.answer("Выбери пол", reply_markup=GENDER_KB)


@router.message(RegistrationState.gender)
async def reg_gender(message: Message, state: FSMContext) -> None:
    registration_drafts[message.from_user.id]["gender"] = message.text.strip().lower()
    await state.set_state(RegistrationState.age)
    await message.answer("Возраст (13-99)", reply_markup=ReplyKeyboardRemove())


@router.message(RegistrationState.age)
async def reg_age(message: Message, state: FSMContext) -> None:
    if not message.text.isdigit() or not (13 <= int(message.text) <= 99):
        await message.answer("Возраст должен быть числом от 13 до 99")
        return
    registration_drafts[message.from_user.id]["age"] = int(message.text)
    await state.set_state(RegistrationState.game)
    await message.answer("Выбери игру", reply_markup=GAME_KB)


@router.message(RegistrationState.game)
async def reg_game(message: Message, state: FSMContext) -> None:
    games = await backend.get("/games", message.from_user.id)
    by_name = {item["name"].lower(): item["id"] for item in games}
    selected = by_name.get(message.text.strip().lower())
    if not selected:
        await message.answer("Выбери игру кнопкой")
        return

    registration_drafts[message.from_user.id]["game_id"] = selected
    await state.set_state(RegistrationState.roles)
    await message.answer(ROLE_HINT, reply_markup=ReplyKeyboardRemove())


@router.message(RegistrationState.roles)
async def reg_roles(message: Message, state: FSMContext) -> None:
    roles = [x.strip() for x in message.text.split(",") if x.strip()]
    registration_drafts[message.from_user.id]["roles"] = roles[:8]
    await state.set_state(RegistrationState.tags)
    await message.answer(TAG_HINT)


@router.message(RegistrationState.tags)
async def reg_tags(message: Message, state: FSMContext) -> None:
    tags = [x.strip().lower() for x in message.text.split(",") if x.strip()]
    registration_drafts[message.from_user.id]["tags"] = tags[:12]
    await state.set_state(RegistrationState.bio)
    await message.answer("Напиши описание (10..400)")


@router.message(RegistrationState.bio)
async def reg_bio(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if len(text) < 10 or len(text) > 400:
        await message.answer("Описание должно быть от 10 до 400 символов")
        return
    registration_drafts[message.from_user.id]["bio"] = text
    await state.set_state(RegistrationState.media)
    await message.answer("Отправь фото или видео")


@router.message(RegistrationState.media)
async def reg_media(message: Message, state: FSMContext) -> None:
    draft = registration_drafts[message.from_user.id]

    if message.photo:
        draft["media_type"] = "photo"
        draft["media_file_id"] = message.photo[-1].file_id
    elif message.video:
        draft["media_type"] = "video"
        draft["media_file_id"] = message.video.file_id
    else:
        await message.answer("Нужны фото или видео")
        return

    await state.set_state(RegistrationState.confirm)
    await message.answer(
        "Проверь анкету:\n"
        f"Ник: {draft['nickname']}\n"
        f"Пол: {draft['gender']}\n"
        f"Возраст: {draft['age']}\n"
        f"Роли: {', '.join(draft['roles']) or '-'}\n"
        f"Теги: {', '.join(draft['tags']) or '-'}\n"
        f"Описание: {draft['bio']}",
        reply_markup=CONFIRM_KB,
    )


@router.message(RegistrationState.confirm, F.text == "✅ Сохранить")
async def reg_save(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    draft = registration_drafts[tg_id]
    await backend.put("/profiles/me", tg_id, draft)
    await state.clear()
    await message.answer("Анкета сохранена ✅", reply_markup=MAIN_MENU)


@router.message(RegistrationState.confirm, F.text == "✏️ Изменить")
async def reg_edit(message: Message, state: FSMContext) -> None:
    await state.set_state(RegistrationState.nickname)
    await message.answer("Ок, начнем заново. Введи никнейм", reply_markup=ReplyKeyboardRemove())


@router.message(F.text == "Главное меню")
async def main_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Главное меню", reply_markup=MAIN_MENU)


@router.message(F.text == "Поиск")
async def search_mode(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    try:
        await backend.get("/profiles/me", tg_id)
    except Exception:
        await message.answer(NEED_PROFILE)
        return

    await state.set_state(BrowsingState.active)
    await _show_next_candidate(message, tg_id)


@router.message(BrowsingState.active, F.text == "Лайк")
async def like_candidate(message: Message) -> None:
    tg_id = message.from_user.id
    target = current_candidates.get(tg_id)
    if not target:
        await _show_next_candidate(message, tg_id)
        return

    result = await backend.post("/actions/like", tg_id, {"target_user_id": target})
    if result.get("match_created"):
        await message.answer("Это взаимный лайк! У вас новый мэтч 🎉")
    await _show_next_candidate(message, tg_id)


@router.message(BrowsingState.active, F.text == "Скип")
async def skip_candidate(message: Message) -> None:
    tg_id = message.from_user.id
    target = current_candidates.get(tg_id)
    if target:
        await backend.post("/actions/skip", tg_id, {"target_user_id": target})
    await _show_next_candidate(message, tg_id)


@router.message(BrowsingState.active, F.text == "Отправить письмо")
async def letter_start(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    target = current_candidates.get(tg_id)
    if not target:
        await _show_next_candidate(message, tg_id)
        return
    letters_target[tg_id] = target
    await state.set_state(BrowsingState.letter_text)
    await message.answer("Введи текст письма (1..500)")


@router.message(BrowsingState.letter_text)
async def letter_send(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if len(text) > 500:
        await message.answer("Слишком длинно. Максимум 500")
        return

    tg_id = message.from_user.id
    target = letters_target.get(tg_id)
    if not target:
        await state.set_state(BrowsingState.active)
        await _show_next_candidate(message, tg_id)
        return

    await backend.post("/actions/letter", tg_id, {"target_user_id": target, "text": text})
    await message.answer("Письмо отправлено ✉️")
    await state.set_state(BrowsingState.active)
    await _show_next_candidate(message, tg_id)


@router.message(BrowsingState.active, F.text == "Остановить поиск")
async def stop_search(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Поиск остановлен", reply_markup=MAIN_MENU)


@router.message(F.text == "Мой профиль")
async def my_profile(message: Message) -> None:
    tg_id = message.from_user.id
    try:
        profile = await backend.get("/profiles/me", tg_id)
    except Exception:
        await message.answer(NEED_PROFILE)
        return

    await message.answer(_profile_card(profile), reply_markup=PROFILE_KB)


@router.message(F.text == "Перезаполнить анкету")
async def refill_profile(message: Message, state: FSMContext) -> None:
    await state.set_state(RegistrationState.nickname)
    await message.answer("Ок, введи никнейм", reply_markup=ReplyKeyboardRemove())


@router.message(F.text == "Изменить фото/видео")
async def change_media_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(ProfileEditState.media)
    await message.answer("Пришли новое фото или видео", reply_markup=ReplyKeyboardRemove())


@router.message(F.text == "Изменить био")
async def change_bio_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(ProfileEditState.bio)
    await message.answer("Пришли новое био (10..400)", reply_markup=ReplyKeyboardRemove())


@router.message(ProfileEditState.bio)
async def save_new_bio(message: Message, state: FSMContext) -> None:
    bio = (message.text or "").strip()
    if len(bio) < 10 or len(bio) > 400:
        await message.answer("Описание должно быть от 10 до 400 символов")
        return

    await _update_profile_partial(message.from_user.id, bio=bio)
    await state.clear()
    await message.answer("Био обновлено ✅", reply_markup=MAIN_MENU)


@router.message(ProfileEditState.media)
async def save_new_media(message: Message, state: FSMContext) -> None:
    media_type = ""
    media_file_id = ""

    if message.photo:
        media_type = "photo"
        media_file_id = message.photo[-1].file_id
    elif message.video:
        media_type = "video"
        media_file_id = message.video.file_id
    else:
        await message.answer("Нужны фото или видео")
        return

    await _update_profile_partial(message.from_user.id, media_type=media_type, media_file_id=media_file_id)
    await state.clear()
    await message.answer("Медиа обновлено ✅", reply_markup=MAIN_MENU)


@router.message(F.text == "Мэтчи")
async def matches_open(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    rows = await backend.get("/matches", tg_id)
    if not rows:
        await message.answer("Пока нет мэтчей", reply_markup=MAIN_MENU)
        return

    matches_cache[tg_id] = rows
    matches_index[tg_id] = 0
    await state.set_state(MatchesState.viewing)
    first = rows[0]
    username_text = f"@{first['username']}" if first.get("username") else "Open in WebApp"
    await message.answer(
        f"{first['nickname']} • {first['game_name']}\n{username_text}",
        reply_markup=MAIN_MENU,
    )
    await message.answer("Навигация", reply_markup=matches_nav(1, len(rows)))


@router.callback_query(F.data.in_(["match_prev", "match_next", "match_idx"]))
async def match_nav(callback: CallbackQuery) -> None:
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
    username_text = f"@{item['username']}" if item.get("username") else "Open in WebApp"
    await callback.message.edit_text(
        f"{item['nickname']} • {item['game_name']}\n{username_text}",
        reply_markup=matches_nav(idx + 1, len(rows)),
    )
    await callback.answer()


@router.message(F.text == "Настройки")
async def settings_menu(message: Message, state: FSMContext) -> None:
    await state.set_state(SettingsState.menu)
    await message.answer(SETTINGS_TEXT, reply_markup=SETTINGS_KB)


@router.message(SettingsState.menu, F.text == "Данные аккаунта")
async def account_data(message: Message) -> None:
    await message.answer("Привязка аккаунтов", reply_markup=ACCOUNT_DATA_KB)


@router.message(F.text == "Riot ID")
async def riot_start(message: Message, state: FSMContext) -> None:
    await state.set_state(SettingsState.riot)
    await message.answer("Введи Riot ID")


@router.message(SettingsState.riot)
async def riot_save(message: Message, state: FSMContext) -> None:
    await backend.post("/account/link/riot", message.from_user.id, {"account_ref": message.text.strip()})
    await state.set_state(SettingsState.menu)
    await message.answer("Riot ID сохранен", reply_markup=ACCOUNT_DATA_KB)


@router.message(F.text == "Steam")
async def steam_start(message: Message, state: FSMContext) -> None:
    await state.set_state(SettingsState.steam)
    await message.answer("Введи steam64 или vanity")


@router.message(SettingsState.steam)
async def steam_save(message: Message, state: FSMContext) -> None:
    await backend.post("/account/link/steam", message.from_user.id, {"account_ref": message.text.strip()})
    await state.set_state(SettingsState.menu)
    await message.answer("Steam сохранен", reply_markup=ACCOUNT_DATA_KB)


@router.message(F.text == "Обновить статистику")
async def refresh_stats(message: Message) -> None:
    result = await backend.post("/account/refresh-stats", message.from_user.id)
    await message.answer(result.get("message", "Обновлено"), reply_markup=ACCOUNT_DATA_KB)


@router.message(F.text == "Назад")
async def back_settings(message: Message, state: FSMContext) -> None:
    await state.set_state(SettingsState.menu)
    await message.answer("Настройки", reply_markup=SETTINGS_KB)


@router.message(F.text == "Премиум")
async def premium(message: Message) -> None:
    await message.answer("Premium coming soon: больше лайков и писем в день.")


@router.message(F.text == "Поддержка")
async def support(message: Message) -> None:
    await message.answer("Поддержка: @elyx_support")
