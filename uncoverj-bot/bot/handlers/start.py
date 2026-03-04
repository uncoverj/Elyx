from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from backend.database import async_session_maker
from backend.models.user import User
from backend.models.profile import Profile
from backend.models.accounts_link import AccountLink
from bot.states import RegistrationStates
from bot.keyboards.reply import get_gender_kb, get_game_kb, get_main_menu, get_skip_bio_kb
from bot.keyboards.inline import get_tags_kb, AVAILABLE_TAGS

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Начало работы или старт регистрации"""
    # Сначала проверим, есть ли профиль через БД
    user_id = message.from_user.id
    
    async with async_session_maker() as session:
        # Пытаемся получить пользователя и профиль
        user = await session.get(User, user_id)
        if user:
             profile = await session.get(Profile, user.id)
             if profile:
                 await message.answer(
                     "Добро пожаловать обратно! Выбери действие в меню:",
                     reply_markup=get_main_menu()
                 )
                 return
                 
    # Если нет профиля, начинаем регистрацию
    await message.answer("Привет! Давай создадим твою анкету. Как тебя зовут? (Никнейм)", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegistrationStates.waiting_nickname)

@router.message(RegistrationStates.waiting_nickname, F.text)
async def process_nickname(message: Message, state: FSMContext):
    """Шаг 2: Никнейм -> Пол"""
    nickname = message.text.strip()
    if len(nickname) < 2 or len(nickname) > 64:
        await message.answer("Пожалуйста, введи никнейм от 2 до 64 символов.")
        return
        
    await state.update_data(nickname=nickname)
    await message.answer("Укажи свой пол:", reply_markup=get_gender_kb())
    await state.set_state(RegistrationStates.waiting_gender)

@router.message(RegistrationStates.waiting_gender, F.text.in_(["Парень", "Девушка", "Скрыть"]))
async def process_gender(message: Message, state: FSMContext):
    """Шаг 3: Пол -> Возраст"""
    gender_map = {"Парень": "male", "Девушка": "female", "Скрыть": "hidden"}
    await state.update_data(gender=gender_map[message.text])
    
    await message.answer("Сколько тебе лет? (введи число от 14 до 60)", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegistrationStates.waiting_age)

@router.message(RegistrationStates.waiting_age, F.text)
async def process_age(message: Message, state: FSMContext):
    """Шаг 4: Возраст -> Игра"""
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введи число.")
        return
        
    age = int(message.text)
    if age < 14 or age > 60:
        await message.answer("У нас можно зарегистрироваться только с 14 до 60 лет.")
        return
        
    await state.update_data(age=age)
    await message.answer("В какую игру будешь искать тиммейтов?", reply_markup=get_game_kb())
    await state.set_state(RegistrationStates.waiting_game)

@router.message(RegistrationStates.waiting_game, F.text.in_(["Valorant", "CS2", "Dota 2", "LoL"]))
async def process_game(message: Message, state: FSMContext):
    """Шаг 5: Игра -> Теги"""
    game_map = {"Valorant": "valorant", "CS2": "cs2", "Dota 2": "dota2", "LoL": "lol"}
    await state.update_data(game_primary=game_map[message.text])
    
    # Инициализируем пустой сет тегов
    await state.update_data(selected_tags=[])
    
    await message.answer(
        "Выбери теги своего стиля игры и поведения (можно несколько):",
        reply_markup=get_tags_kb(set())
    )
    await state.set_state(RegistrationStates.waiting_tags)

@router.callback_query(RegistrationStates.waiting_tags, F.data.startswith("tag_"))
async def process_tag_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора/отмены тега"""
    tag = callback.data.split("_", 1)[1]
    data = await state.get_data()
    selected = set(data.get("selected_tags", []))
    
    if tag in selected:
        selected.remove(tag)
    else:
        selected.add(tag)
        
    await state.update_data(selected_tags=list(selected))
    
    # Обновляем клавиатуру
    await callback.message.edit_reply_markup(reply_markup=get_tags_kb(selected))
    await callback.answer()

@router.callback_query(RegistrationStates.waiting_tags, F.data == "tags_done")
async def process_tags_done(callback: CallbackQuery, state: FSMContext):
    """Шаг 6: Теги -> Биография"""
    await callback.message.delete()
    await callback.message.answer(
        "Расскажи немного о себе (или нажми 'Пропустить'):",
        reply_markup=get_skip_bio_kb()
    )
    await state.set_state(RegistrationStates.waiting_bio)
    await callback.answer()

@router.message(RegistrationStates.waiting_bio, F.text)
async def process_bio(message: Message, state: FSMContext):
    """Шаг 7: Биография -> Фото"""
    bio_text = message.text.strip()
    if bio_text == "Пропустить":
        bio_text = None
        
    await state.update_data(bio_text=bio_text)
    await message.answer(
        "Отправь фото или небольшое видео для твоей анкеты:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(RegistrationStates.waiting_photo)

@router.message(RegistrationStates.waiting_photo, F.photo | F.video)
async def process_photo(message: Message, state: FSMContext):
    """Шаг 8: Фото -> Game ID"""
    file_id = ""
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.video:
        file_id = message.video.file_id
        
    await state.update_data(photo_file_id=file_id)
    
    data = await state.get_data()
    game = data.get("game_primary")
    
    hint = ""
    if game == "valorant" or game == "lol":
        hint = "Например: RiotName#TAG1"
    else:
        hint = "Например: Steam ID64"
        
    await message.answer(f"Последний шаг! Привяжи свой аккаунт {game}.\n{hint}")
    await state.set_state(RegistrationStates.waiting_game_id)

@router.message(RegistrationStates.waiting_game_id, F.text)
async def process_game_id(message: Message, state: FSMContext):
    """Шаг 9: Game ID -> Сохранение в БД"""
    game_id = message.text.strip()
    data = await state.get_data()
    
    tg_user = message.from_user
    
    # Сохраняем все в базу
    async with async_session_maker() as session:
        # 1. Создание или получение User
        user_stmt = pg_insert(User).values(
            telegram_id=tg_user.id,
            username=tg_user.username
        ).on_conflict_do_update(
            index_elements=['telegram_id'],
            set_={'username': tg_user.username, 'last_seen': User.last_seen}
        ).returning(User)
        
        result = await session.execute(user_stmt)
        user = result.scalar_one()
        
        # 2. Создание профиля
        profile = Profile(
            user_id=user.id,
            nickname=data["nickname"],
            age=data["age"],
            gender=data["gender"],
            game_primary=data["game_primary"],
            playstyle_tags=data["selected_tags"],  # Для простоты кладем все в playstyle
            bio_text=data.get("bio_text"),
            photo_file_id=data["photo_file_id"]
        )
        session.add(profile)
        
        # 3. Сохранение Game ID в accounts_link
        account_link = AccountLink(
            user_id=user.id,
            game=data["game_primary"],
            game_id=game_id
        )
        session.add(account_link)
        
        await session.commit()
        
    await state.clear()
    
    await message.answer(
        "Регистрация успешно завершена! 🎉\nМы начали сбор твоей статистики, скоро она появится в профиле.",
        reply_markup=get_main_menu()
    )
    # В будущем тут можно сразу вызвать функцию отображения своего профиля
