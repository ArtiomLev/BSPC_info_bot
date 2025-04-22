import locale
import logging
import asyncio
from datetime import datetime, date, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
# Компоненты проекта
from configs.config_reader import config
from core.replacements import ReplacementSchedule
import database.database as database
# Обработчики
from handlers.basic import router as basic_router
from handlers.bells import router as bells_router
from handlers.week import router as week_router
from handlers.registration import router as register_router

# Логирование
logging.basicConfig(level=logging.INFO)

# Установка локали
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')  # Для Unix/Linux
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')  # Для Windows

# Переменные для замен
today_replacements = None
next_working_day_replacements = None
replacements_parser = ReplacementSchedule(config.changes["base_url"], config.changes["base_link"])


async def update_replacements():
    """Получение замен"""
    global today_replacements, next_working_day_replacements

    logging.log(logging.INFO, "Updating changes!")

    today = datetime.now().date()
    if today.weekday() == 5:
        next_working_day = today + timedelta(days=2)
    else:
        next_working_day = today + timedelta(days=1)

    today_replacements = replacements_parser.get_replacements(today.strftime('%A').capitalize())
    next_working_day_replacements = replacements_parser.get_replacements(next_working_day.strftime('%A').capitalize())

    logging.log(logging.INFO, "Changes updated!")


async def replacements_always_update(period_min: int):
    """Автоматическое обновление замен.
    `period_min` - период обновления в минутах"""
    while True:
        await update_replacements()
        await asyncio.sleep(period_min * 60)  # Спать 30 минут


bot = Bot(token=config.bot_token.get_secret_value(),
          default=DefaultBotProperties(
              parse_mode=ParseMode.MARKDOWN_V2
          ))

dp = Dispatcher()
dp.include_router(basic_router)
dp.include_router(bells_router)
dp.include_router(week_router)
dp.include_router(register_router)


async def main():
    await database.init_users_db("database/users.sqlite")
    asyncio.create_task(replacements_always_update(30))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
