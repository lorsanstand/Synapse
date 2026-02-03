import logging
from datetime import date
from typing import Dict, Any

from aiogram import Router, BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.services.schedule import ScheduleService, ScheduleAction
from app.models.user import UserModel

log = logging.getLogger(__name__)
router = Router()


class RegGroup(StatesGroup):
    group = State()


class UserCheckAccessMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: Dict[str, Any]) -> Any:

        user: UserModel = data["user"]

        if not user.is_verified:
            await event.answer("Вы не имете доступа к этой функции")
            log.info("User get not access %s", user.tg_id)
            return

        return await handler(event, data)

router.message.middleware(UserCheckAccessMiddleware())


@router.message(Command("schedule"))
async def command_help(message: Message):
    await ScheduleService.get_schedule(message)


@router.callback_query(ScheduleAction.filter())
async def process_schedule_navigation(callback: CallbackQuery, callback_data: ScheduleAction):
    target_date = date.fromisoformat(callback_data.date_str)
    await ScheduleService.get_schedule(callback, day=target_date)
    await callback.answer()


@router.message(Command("group"))
async def start_reg_group(message: Message, state: FSMContext, user: UserModel):
    await state.set_state(RegGroup.group)
    await  message.answer(f"Введите вашу группу. Сейчас ваша группа: {user.group}")


@router.message(RegGroup.group)
async def reg_group(message: Message, state: FSMContext):
    await ScheduleService.set_group(message.text, message)
    await state.clear()