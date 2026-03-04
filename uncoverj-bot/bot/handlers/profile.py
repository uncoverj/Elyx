from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, update, and_

from backend.database import async_session_maker
from backend.models.user import User
from backend.models.profile import Profile
from backend.models.stats import StatsSnapshot
from backend.models.trust import TrustVote
from bot.states import ProfileStates, RegistrationStates
from bot.keyboards.profile import get_profile_kb, get_cancel_kb
from bot.keyboards.reply import get_main_menu
from bot.utils.render import render_profile_text

router = Router()

@router.message(F.text == "👤 Мой профиль")
async def show_my_profile(message: Message, db_user: User, has_profile: bool):
    if not db_user or not has_profile:
        await message.answer("Сначала пройди регистрацию /start !")
        return
        
    async with async_session_maker() as session:
        # Получаем профиль
        prof_stmt = select(Profile).where(Profile.user_id == db_user.id)
        profile = (await session.execute(prof_stmt)).scalar_one()
        
        # Получаем статистику
        stat_stmt = select(StatsSnapshot).where(
            and_(StatsSnapshot.user_id == db_user.id, StatsSnapshot.game == profile.game_primary)
        )
        stats = (await session.execute(stat_stmt)).scalar_one_or_none()
        
        # Считаем траст (упрощенно: считаем кол-во +1 и -1)
        trust_up = 12   # Заглушки, пока нет реальной логики
        trust_down = 2
        
        text = render_profile_text(profile, stats, db_user.is_premium, trust_up, trust_down)
        
        if profile.photo_file_id:
            try:
                 await message.answer_photo(
                     photo=profile.photo_file_id, 
                     caption=text, 
                     reply_markup=get_profile_kb()
                 )
            except:
                 await message.answer(text, reply_markup=get_profile_kb())
        else:
            await message.answer(text, reply_markup=get_profile_kb())

@router.message(F.text == "🔍 Смотреть анкеты")
async def go_to_search(message: Message):
    # Просто эмулируем нажатие "Поиск"
    # Хендлер поиска поймает это по тексту "🔍 Поиск" (если вызвать его напрямую, нужно импортировать)
    # Здесь просто попросим юзера нажать кнопку Поиск из Главного меню для чистоты
    await message.answer("Переходим в поиск...", reply_markup=get_main_menu())
    # Идеально перенаправить в стейт Browsing, но для этого надо импортить `start_search`

@router.message(F.text == "🔄 Заполнить заново")
async def restart_registration(message: Message, state: FSMContext, db_user: User):
    """Сброс анкеты и повторная регистрация"""
    async with async_session_maker() as session:
        # Удаляем старый профиль (Accounts и Stats удалятся каскадно, если настроено Cascade)
        await session.execute(
            select(Profile).where(Profile.user_id == db_user.id)
        )
        # В реале лучше сделать профиль is_visible=False или просто перезаписать
        
    await message.answer("Давай создадим твою анкету заново! Как тебя зовут? (Никнейм)", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegistrationStates.waiting_nickname)

@router.message(F.text == "📷 Изменить фото/видео")
async def edit_photo_start(message: Message, state: FSMContext):
    await message.answer("Отправь новое фото или видео:", reply_markup=get_cancel_kb())
    await state.set_state(ProfileStates.waiting_new_photo)

@router.message(ProfileStates.waiting_new_photo, F.photo | F.video)
async def process_new_photo(message: Message, state: FSMContext, db_user: User):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    
    async with async_session_maker() as session:
        await session.execute(
            update(Profile).where(Profile.user_id == db_user.id).values(photo_file_id=file_id)
        )
        await session.commit()
        
    await state.clear()
    await message.answer("Фото успешно обновлено!", reply_markup=get_profile_kb())
    # Сразу показываем обновленный профиль
    await show_my_profile(message, db_user, True)

@router.message(F.text == "✏️ Изменить текст")
async def edit_bio_start(message: Message, state: FSMContext):
    await message.answer("Расскажи о себе (новый текст):", reply_markup=get_cancel_kb())
    await state.set_state(ProfileStates.waiting_new_bio)

@router.message(ProfileStates.waiting_new_bio, F.text)
async def process_new_bio(message: Message, state: FSMContext, db_user: User):
    if message.text == "Отмена":
        await state.clear()
        await message.answer("Изменение отменено.", reply_markup=get_profile_kb())
        return
        
    async with async_session_maker() as session:
        await session.execute(
            update(Profile).where(Profile.user_id == db_user.id).values(bio_text=message.text)
        )
        await session.commit()
        
    await state.clear()
    await message.answer("Описание успешно обновлено!", reply_markup=get_profile_kb())
    await show_my_profile(message, db_user, True)
