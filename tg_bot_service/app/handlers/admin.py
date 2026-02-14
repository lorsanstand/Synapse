from app.models.user import UserModel
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


class UserCheckAccessMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: Dict[str, Any]) -> Any:

        user: UserModel = data["user"]

        if not user.is_admin:
            await event.answer("Вы не имеете доступа к этой фунеции т.к. вы не админ")
            log.info("User get not access %s", user.tg_id)
            return

        return await handler(event, data)

router.message.middleware(UserCheckAccessMiddleware())


@router.message(Command("test_admin"))
async def test_admin(message: Message):
    await message.answer("Поздравляю вы админ")


@router.message(Command("create_link"))
async def create_link(message: Message):
    pass