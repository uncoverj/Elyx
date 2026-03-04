from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from backend.database import async_session_maker
from backend.models.user import User
from backend.models.profile import Profile
from backend.models.stats import StatsSnapshot
from backend.models.swipe import Swipe
from backend.models.match import Match
from backend.services.matching import get_next_profile
from bot.states import SearchStates
from bot.keyboards.reply import get_main_menu
from bot.keyboards.search import get_search_kb, get_letter_kb, get_incoming_like_kb, get_reaction_kb
from bot.utils.render import render_profile_text

router = Router()

async def show_next_profile(message: Message, state: FSMContext, session: AsyncSession, from_user: User):
    """Вспомогательная функция для показа следующей анкеты"""
    # Получаем профиль того, кто ищет
    user_prof_stmt = select(Profile).where(Profile.user_id == from_user.id)
    user_prof_res = await session.execute(user_prof_stmt)
    user_prof = user_prof_res.scalar_one_or_none()
    
    if not user_prof:
        await message.answer("Сначала нужно заполнить профиль!", reply_markup=get_main_menu())
        await state.clear()
        return

    # Получаем стату ищущего (для подбора по Score)
    user_stat_stmt = select(StatsSnapshot).where(
        and_(StatsSnapshot.user_id == from_user.id, StatsSnapshot.game == user_prof.game_primary)
    )
    user_stat_res = await session.execute(user_stat_stmt)
    user_stat = user_stat_res.scalar_one_or_none()
    
    user_score = user_stat.unified_score if user_stat else None
    
    # Ищем анкету
    target_prof, target_stat, target_user = await get_next_profile(
        session, from_user.id, user_prof.game_primary, user_score
    )
    
    if not target_prof:
        await message.answer(
            f"В игре {user_prof.game_primary} пока нет новых анкет 😔\nПопробуй зайти позже!",
            reply_markup=get_main_menu()
        )
        await state.clear()
        return
        
    # Рендерим и отправляем
    text = render_profile_text(
        target_prof, target_stat, 
        target_user.is_premium, 
        trust_up=12, trust_down=2 # TODO: подтягивать реальный траст
    )
    
    # Сохраняем в state кого мы сейчас смотрим
    await state.update_data(current_target_id=target_user.id)
    
    if target_prof.photo_file_id:
        # Проверяем фото или видео по расширению/метаданным (упрощенно шлем как фото)
        # В реальном коде можно хранить тип медиа
        try:
            await message.answer_photo(
                photo=target_prof.photo_file_id,
                caption=text,
                reply_markup=get_search_kb()
            )
        except Exception:
             await message.answer(text, reply_markup=get_search_kb())
    else:
        await message.answer(text, reply_markup=get_search_kb())

@router.message(F.text == "🔍 Поиск")
async def start_search(message: Message, state: FSMContext, db_user: User, has_profile: bool):
    if not db_user or not has_profile:
        await message.answer("Сначала пройди регистрацию /start !")
        return
        
    await state.set_state(SearchStates.browsing)
    async with async_session_maker() as session:
        await show_next_profile(message, state, session, db_user)

@router.message(SearchStates.browsing, F.text.in_(["❤️ Лайк", "👎 Скип"]))
async def process_swipe(message: Message, state: FSMContext, db_user: User):
    data = await state.get_data()
    target_user_id = data.get("current_target_id")
    
    if not target_user_id:
        await message.answer("Ошибка сессии.", reply_markup=get_main_menu())
        await state.clear()
        return

    action = "like" if message.text == "❤️ Лайк" else "skip"
    
    async with async_session_maker() as session:
        # Получаем игру юзера
        prof_stmt = select(Profile.game_primary).where(Profile.user_id == db_user.id)
        game = (await session.execute(prof_stmt)).scalar()
        
        # Сохраняем свайп
        swipe = Swipe(
            from_user_id=db_user.id,
            to_user_id=target_user_id,
            game=game,
            action=action
        )
        session.add(swipe)
        
        if action == "like":
            # Проверяем, есть ли встречный лайк (Match)
            stmt_reverse = select(Swipe).where(
                and_(
                    Swipe.from_user_id == target_user_id,
                    Swipe.to_user_id == db_user.id,
                    Swipe.action == "like",
                    Swipe.game == game
                )
            )
            reverse_swipe = (await session.execute(stmt_reverse)).scalar_one_or_none()
            
            if reverse_swipe:
                # ВЗАИМНЫЙ ЛАЙК! СОЗДАЕМ MATCH
                match_stmt = pg_insert(Match).values(
                    user1_id=min(db_user.id, target_user_id),
                    user2_id=max(db_user.id, target_user_id),
                    game=game
                ).on_conflict_do_nothing()
                
                await session.execute(match_stmt)
                await session.commit()
                
                # Уведомляем обоих
                bot: Bot = message.bot
                
                # Получаем telegram_id таргета
                target_tg_id = (await session.execute(select(User.telegram_id).where(User.id == target_user_id))).scalar()
                
                try:
                    await bot.send_message(target_tg_id, "Это мэтч! 🎉\nПроверь раздел '💞 Мэтчи'")
                except Exception:
                    pass # Юзер мог блокнуть бота
                    
                await message.answer("Это мэтч! 🎉\nПроверь раздел '💞 Мэтчи'")
            else:
                await session.commit()
                # Уведомляем получателя о новом лайке
                bot: Bot = message.bot
                target_tg_id = (await session.execute(select(User.telegram_id).where(User.id == target_user_id))).scalar()
                try:
                    await bot.send_message(
                        target_tg_id, 
                        "У вас новый лайк 🔥",
                        reply_markup=get_incoming_like_kb(db_user.id)
                    )
                except Exception:
                    pass
        else:
            await session.commit() # Для skip
            
        # Показываем следующего
        await show_next_profile(message, state, session, db_user)

@router.message(SearchStates.browsing, F.text == "⛔ Стоп")
async def process_stop(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Поиск остановлен.", reply_markup=get_main_menu())

@router.message(SearchStates.browsing, F.text == "✉️ Письмо")
async def start_letter(message: Message, state: FSMContext):
    await message.answer("Напишите сообщение для этого игрока:", reply_markup=get_letter_kb())
    await state.set_state(SearchStates.waiting_letter)

@router.message(SearchStates.waiting_letter, F.text)
async def process_letter(message: Message, state: FSMContext, db_user: User):
    if message.text == "Отмена":
        await state.set_state(SearchStates.browsing)
        await message.answer("Продолжаем поиск...", reply_markup=get_search_kb())
        return
        
    data = await state.get_data()
    target_user_id = data.get("current_target_id")
    letter_text = message.text
    
    async with async_session_maker() as session:
        # Узнаем игру
        prof_stmt = select(Profile.game_primary).where(Profile.user_id == db_user.id)
        game = (await session.execute(prof_stmt)).scalar()
        
        # Сохраняем свайп (action = letter)
        swipe = Swipe(
            from_user_id=db_user.id,
            to_user_id=target_user_id,
            game=game,
            action="letter"
        )
        session.add(swipe)
        await session.commit()
        
        # Уведомляем получателя
        bot: Bot = message.bot
        target_tg_id = (await session.execute(select(User.telegram_id).where(User.id == target_user_id))).scalar()
        
        try:
            await bot.send_message(
                target_tg_id, 
                f"Вам оставили письмо 💌\n\n💬 <i>{letter_text}</i>",
                reply_markup=get_incoming_like_kb(db_user.id)
            )
        except Exception:
            pass
            
        await message.answer("Письмо успешно отправлено!")
        
        # Возвращаемся в поиск и показываем некст
        await state.set_state(SearchStates.browsing)
        await show_next_profile(message, state, session, db_user)
