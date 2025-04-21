import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from src.bot import bot
from src.middleware import AuthMiddleware
from src.routers.base import router as base_router
from src.routers.resume import router as resume_router


async def main() -> None:
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware.register(AuthMiddleware())
    dp.include_router(router=base_router)
    dp.include_router(router=resume_router)
    await bot.set_my_commands(
        commands=[
            BotCommand(
                command="/start",
                description="Начать работу",
            ),
            BotCommand(
                command="/add_project",
                description="Добавить проект",
            ),
            BotCommand(
                command="/update_profile",
                description="Обновить профиль",
            ),
        ]
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.new_event_loop()
    loop.create_task(main())
    asyncio.set_event_loop(loop)
    loop.run_forever()
