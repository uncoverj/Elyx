from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from backend.database import async_session_maker
from backend.models.user import User
from backend.models.accounts_link import AccountLink
from bot.states import SettingsStates
from bot.keyboards.profile import get_settings_kb
from bot.keyboards.reply import get_main_menu

router = Router()

@router.message(F.text == "⚙️ Настройки")
async def show_settings(message: Message, db_user: User, has_profile: bool):
    if not db_user or not has_profile:
        await message.answer("Сначала пройди регистрацию /start !")
        return
        
    await message.answer("Раздел настроек:", reply_markup=get_settings_kb())

@router.message(F.text == "🏠 Главное меню")
async def back_to_main(message: Message):
    await message.answer("Главное меню", reply_markup=get_main_menu())

@router.message(F.text == "🆘 Поддержка")
async def show_support(message: Message):
    await message.answer("Если у вас возникли проблемы, напишите в @UserSupport")

@router.message(F.text == "⭐ Premium")
async def show_premium(message: Message):
    # Заглушка до ШАГА 9
    text = (
        "<b>⭐ Premium статус</b>\n\n"
        "Дает больше свайпов (150/день) и значок ⭐ в профиле!\n"
        "<i>Раздел в разработке...</i>"
    )
    await message.answer(text, reply_markup=get_settings_kb())

@router.message(F.text == "🎮 Данные аккаунта")
async def show_accounts(message: Message, db_user: User):
    async with async_session_maker() as session:
        acc_stmt = select(AccountLink).where(AccountLink.user_id == db_user.id)
        accounts = (await session.execute(acc_stmt)).scalars().all()
        
        if not accounts:
            await message.answer("У вас нет привязанных аккаунтов.", reply_markup=get_settings_kb())
            return
            
        text = "<b>Твои привязанные аккаунты:</b>\n\n"
        for acc in accounts:
            status = "✅" if acc.verified else "⏳ (проверка)"
            text += f"🎮 {acc.game.upper()}: {acc.game_id} {status}\n"
            
        text += "\n<i>Для изменения аккаунта пройди регистрацию заново в профиле.</i>"
        
        await message.answer(text, reply_markup=get_settings_kb())
