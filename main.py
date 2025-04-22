import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
# Компоненты проекта
from configs.config_reader import config
from core.replacements import replacements_manager
import database.database as database
# Обработчики
from handlers.basic import router as basic_router
from handlers.bells import router as bells_router
from handlers.week import router as week_router
from handlers.registration import router as register_router
from handlers.changes import router as changes_router


# Логирование
logging.basicConfig(level=logging.INFO)


# Объект бота
bot = Bot(token=config.bot_token.get_secret_value(),
          default=DefaultBotProperties(
              parse_mode=ParseMode.MARKDOWN_V2
          ))

# Объект диспетчера aiogram
dp = Dispatcher()
# Подключение роутеров обработчиков
dp.include_router(basic_router)
dp.include_router(bells_router)
dp.include_router(week_router)
dp.include_router(register_router)
dp.include_router(changes_router)


async def main():
    await database.init_users_db("database/users.sqlite")
    asyncio.create_task(replacements_manager.start_periodic_updates(30))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
