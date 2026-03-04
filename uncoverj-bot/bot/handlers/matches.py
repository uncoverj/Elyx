from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, and_, or_

from backend.database import async_session_maker
from backend.models.user import User
from backend.models.profile import Profile
from backend.models.stats import StatsSnapshot
from backend.models.match import Match
from bot.keyboards.reply import get_main_menu
from bot.keyboards.search import get_match_pagination_kb
from bot.utils.render import render_profile_text

router = Router()


async def _get_matches_for_user(session, user_id: int) -> list[Match]:
    """Получить все активные мэтчи пользователя"""
    stmt = select(Match).where(
        and_(
            or_(Match.user1_id == user_id, Match.user2_id == user_id),
            Match.status == "active"
        )
    ).order_by(Match.created_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()


async def _render_match_card(session, match: Match, current_user_id: int) -> tuple[str, str | None, str | None]:
    """
    Рендерит карточку мэтча.
    Возвращает (text, photo_file_id, partner_username).
    """
    partner_id = match.user2_id if match.user1_id == current_user_id else match.user1_id

    partner_user = await session.get(User, partner_id)
    if not partner_user:
        return "Пользователь удалён.", None, None

    prof_stmt = select(Profile).where(Profile.user_id == partner_id)
    profile = (await session.execute(prof_stmt)).scalar_one_or_none()
    if not profile:
        return "Профиль удалён.", None, None

    stat_stmt = select(StatsSnapshot).where(
        and_(StatsSnapshot.user_id == partner_id, StatsSnapshot.game == profile.game_primary)
    )
    stats = (await session.execute(stat_stmt)).scalar_one_or_none()

    text = render_profile_text(profile, stats, partner_user.is_premium, trust_up=0, trust_down=0)
    return text, profile.photo_file_id, partner_user.username


def _get_matches_reply_kb(partner_username: str | None) -> ReplyKeyboardMarkup:
    """Reply-клавиатура для мэтча"""
    username_btn = f"@{partner_username}" if partner_username else "Нет username"
    kb = [
        [KeyboardButton(text=username_btn)],
        [KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


@router.message(F.text == "💞 Мэтчи")
async def show_matches(message: Message, state: FSMContext, db_user: User, has_profile: bool):
    if not db_user or not has_profile:
        await message.answer("Сначала пройди регистрацию /start !")
        return

    async with async_session_maker() as session:
        matches = await _get_matches_for_user(session, db_user.id)

        if not matches:
            await message.answer("У тебя пока нет мэтчей 😔\nПопробуй поискать тиммейтов!", reply_markup=get_main_menu())
            return

        # Показываем первый мэтч
        match = matches[0]
        text, photo_id, username = await _render_match_card(session, match, db_user.id)
        total = len(matches)
        page = 1

        # Сохраняем список ID мэтчей в state для пагинации
        await state.update_data(
            match_ids=[m.id for m in matches],
            match_page=1
        )

        pagination_kb = get_match_pagination_kb(match.id, page, total)

        if photo_id:
            try:
                msg = await message.answer_photo(
                    photo=photo_id,
                    caption=text,
                    reply_markup=pagination_kb
                )
            except Exception:
                msg = await message.answer(text, reply_markup=pagination_kb)
        else:
            msg = await message.answer(text, reply_markup=pagination_kb)

        # Сохраняем message_id для edit_message
        await state.update_data(match_msg_id=msg.message_id)

        # Reply клавиатура с @username
        await message.answer("⬆️ Листай мэтчи кнопками выше", reply_markup=_get_matches_reply_kb(username))


@router.callback_query(F.data.startswith("mpage_"))
async def paginate_matches(callback: CallbackQuery, state: FSMContext, db_user: User):
    """Пагинация мэтчей через edit_message (не новое сообщение!)"""
    page = int(callback.data.split("_")[1])
    data = await state.get_data()
    match_ids = data.get("match_ids", [])

    if not match_ids or page < 1 or page > len(match_ids):
        await callback.answer("Ошибка пагинации")
        return

    match_id = match_ids[page - 1]
    await state.update_data(match_page=page)

    async with async_session_maker() as session:
        match = await session.get(Match, match_id)
        if not match:
            await callback.answer("Мэтч не найден")
            return

        text, photo_id, username = await _render_match_card(session, match, db_user.id)
        total = len(match_ids)
        pagination_kb = get_match_pagination_kb(match.id, page, total)

        # Редактируем сообщение (edit_message, не новое!)
        try:
            if photo_id:
                from aiogram.types import InputMediaPhoto
                await callback.message.edit_media(
                    media=InputMediaPhoto(media=photo_id, caption=text, parse_mode="HTML"),
                    reply_markup=pagination_kb
                )
            else:
                await callback.message.edit_text(
                    text=text,
                    reply_markup=pagination_kb
                )
        except Exception:
            # Если не удалось отредактировать (например, тип сообщения изменился),
            # просто отвечаем
            await callback.message.answer(text, reply_markup=pagination_kb)

    await callback.answer()


@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    """Обработчик для неактивной кнопки (счётчик страниц)"""
    await callback.answer()


# --- Обработка входящих лайков: "Посмотреть" и реакция ---

@router.callback_query(F.data.startswith("view_"))
async def view_liker_profile(callback: CallbackQuery, db_user: User):
    """Посмотреть профиль того, кто лайкнул"""
    from_user_id = int(callback.data.split("_")[1])

    async with async_session_maker() as session:
        from_user = await session.get(User, from_user_id)
        if not from_user:
            await callback.answer("Пользователь не найден")
            return

        prof_stmt = select(Profile).where(Profile.user_id == from_user_id)
        profile = (await session.execute(prof_stmt)).scalar_one_or_none()
        if not profile:
            await callback.answer("Профиль не найден")
            return

        stat_stmt = select(StatsSnapshot).where(
            and_(StatsSnapshot.user_id == from_user_id, StatsSnapshot.game == profile.game_primary)
        )
        stats = (await session.execute(stat_stmt)).scalar_one_or_none()

        text = render_profile_text(profile, stats, from_user.is_premium, trust_up=0, trust_down=0)

        from bot.keyboards.search import get_reaction_kb
        reaction_kb = get_reaction_kb(from_user_id)

        if profile.photo_file_id:
            try:
                await callback.message.answer_photo(
                    photo=profile.photo_file_id,
                    caption=text,
                    reply_markup=reaction_kb
                )
            except Exception:
                await callback.message.answer(text, reply_markup=reaction_kb)
        else:
            await callback.message.answer(text, reply_markup=reaction_kb)

    await callback.answer()


@router.callback_query(F.data.startswith("match_"))
async def accept_like(callback: CallbackQuery, db_user: User):
    """Принять лайк -> создать Match"""
    from_user_id = int(callback.data.split("_")[1])

    async with async_session_maker() as session:
        from sqlalchemy.dialects.postgresql import insert as pg_insert

        # Определяем игру
        prof_stmt = select(Profile.game_primary).where(Profile.user_id == db_user.id)
        game = (await session.execute(prof_stmt)).scalar()

        # Создаём мэтч (UNIQUE constraint защитит от дублирования)
        match_stmt = pg_insert(Match).values(
            user1_id=min(db_user.id, from_user_id),
            user2_id=max(db_user.id, from_user_id),
            game=game
        ).on_conflict_do_nothing()
        await session.execute(match_stmt)
        await session.commit()

        # Уведомляем обоих
        bot: Bot = callback.bot
        from_user = await session.get(User, from_user_id)
        if from_user:
            try:
                await bot.send_message(from_user.telegram_id, "Это мэтч! 🎉\nПроверь раздел '💞 Мэтчи'")
            except Exception:
                pass

    await callback.message.edit_text("Это мэтч! 🎉\nПроверь раздел '💞 Мэтчи'", reply_markup=None)
    await callback.answer("Мэтч создан!")


@router.callback_query(F.data.startswith("rej_"))
async def reject_like(callback: CallbackQuery):
    """Отклонить лайк / письмо"""
    await callback.message.edit_text("Ты скипнул этого игрока.", reply_markup=None)
    await callback.answer()
