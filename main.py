import locale
import asyncio
import logging
from datetime import datetime, date, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command, CommandObject
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from configs.config_reader import config
from core.bells import BellSchedule
from core.week import Week
from core.my_utils import escape_for_telegram
from core.changes import ReplacementSchedule
import database.database as database
from handlers.registration import router as reg_router

# Логирование
logging.basicConfig(level=logging.INFO)

# Установка локали
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')  # Для Unix/Linux
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')  # Для Windows

# Переменные для замен
today_changes = None
next_working_day_changes = None
changes_parser = ReplacementSchedule(config.changes["base_url"], config.changes["base_link"])


async def update_changes():
    """Получение замен"""
    global today_changes, next_working_day_changes

    logging.log(logging.INFO, "Updating changes!")

    today = datetime.now().date()
    if today.weekday() == 5:
        next_working_day = today + timedelta(days=2)
    else:
        next_working_day = today + timedelta(days=1)

    today_changes = changes_parser.get_replacements(today.strftime('%A').capitalize())
    next_working_day_changes = changes_parser.get_replacements(next_working_day.strftime('%A').capitalize())

    logging.log(logging.INFO, "Changes updated!")


async def changes_always_update(period_min: int):
    """Автоматическое обновление замен.
    `period_min` - период обновления в минутах"""
    while True:
        await update_changes()
        await asyncio.sleep(period_min * 60)  # Спать 30 минут


bot = Bot(token=config.bot_token.get_secret_value(),
          default=DefaultBotProperties(
              parse_mode=ParseMode.MARKDOWN_V2
          ))

dp = Dispatcher()
dp.include_router(reg_router)

bells = BellSchedule(config.bells)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Приветственное сообщение"""
    await message.answer(escape_for_telegram("Привет!\n"
                                             "Для работы бота требуется зарегистрироваться:\n"
                                             "/register"
                                             "\n"
                                             "/help для справки"))


@dp.message(Command("help"))
async def cmd_start(message: types.Message):
    await message.answer(escape_for_telegram("Справка:\n"
                                             "\n"
                                             "/start - приветственное сообщение\n"
                                             "\n"
                                             "/help - справка (это сообщение)\n"
                                             "\n"
                                             "/register - регистрация с системе бота\n"
                                             "/unregister - удалить все записи из базы данных\n"
                                             "\n"
                                             "/bells [день] - расписание звонков, "
                                             "если не указать день - будет текущий\n"
                                             "`0`|`рабочий` - расписание для рабочего дня\n"
                                             "`1`|`выходной` - расписание для выходного дня\n"
                                             "`2`|`сокращённый` - расписание для сокращённого дня\n"
                                             "\n"
                                             "/week - получить текущую неделю, в воскресенье - следующую "
                                             "(верхняя/нижняя)\n"
                                             "/nextweek - получить следующую неделю (верхняя/нижняя)\n"
                                             "/currweek - получить текущую неделю в любом случае (верхняя/нижняя)"),
                         parse_mode=ParseMode.MARKDOWN_V2)


@dp.message(Command("bells"))
async def cmd_bells(message: types.Message, command: CommandObject):
    """Вывод расписания звонков"""
    if command.args is None:
        if date.today().weekday() == 6:
            await message.answer(escape_for_telegram("Сегодня воскресенье. \n"
                                                     "Для того чтобы получить звонки на конкретный день напиши:\n"
                                                     "/bells [день]\n"
                                                     "`0`|`рабочий` - расписание для рабочего дня\n"
                                                     "`1`|`выходной` - расписание для выходного дня\n"
                                                     "`2`|`сокращённый` - расписание для сокращённого дня"),
                                 parse_mode=ParseMode.MARKDOWN_V2)
            return
        else:
            if date.today().weekday() == 5:
                day = "weekend_day"
            else:
                day = "working_day"
    else:
        argument = command.args.strip()
        if argument == "0" or argument == "рабочий":
            day = "working_day"
        elif argument == "1" or argument == "выходной":
            day = "weekend_day"
        elif argument == "2" or argument == "сокращённый":
            day = "shortened_day"
        else:
            await message.answer(escape_for_telegram("Аргументы не верны!"))
            return
    await message.answer(escape_for_telegram(bells.format_day_bells(day)))


@dp.message(Command("week"))
async def cmd_week(message: types.Message):
    week = Week()
    if date.today().weekday() == 6:
        next_week = week.next_week()
        answer = "Сегодня воскресенье\n"
        answer += "Следующая неделя *" + next_week.week_type().upper() + "*"
    else:
        answer = "Сейчас *" + week.week_type().upper() + "* неделя"
    await message.answer(escape_for_telegram(answer))


@dp.message(Command("currweek"))
async def cmd_currweek(message: types.Message):
    week = Week()
    answer = "Сейчас *" + week.week_type().upper() + "* неделя"
    await message.answer(escape_for_telegram(answer))


@dp.message(Command("nextweek"))
async def cmd_nextweek(message: types.Message):
    week = Week()
    next_week = week.next_week()
    answer = "Следующая неделя *" + next_week.week_type().upper() + "*"
    await message.answer(escape_for_telegram(answer))


async def main():
    await database.init_users_db("database/users.sqlite")
    asyncio.create_task(changes_always_update(30))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
