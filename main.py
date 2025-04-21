import locale
import asyncio
import logging
from datetime import datetime, date, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command, CommandObject
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config_reader import config
from bells import BellSchedule
from week import Week
from my_escape_function import escape_for_telegram
from changes_parser import ReplacementSchedule

# Установка локали
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')  # Для Unix/Linux
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')  # Для Windows

changes_parser = ReplacementSchedule(config.changes["base_url"], config.changes["base_link"])

today = datetime.now().date()
if today.weekday() == 5:
    next_working_day = today + timedelta(days=2)
else:
    next_working_day = today + timedelta(days=1)

today_changes = changes_parser.get_replacements(today.strftime('%A').capitalize())
next_working_day_changes = changes_parser.get_replacements(next_working_day.strftime('%A').capitalize())

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value(),
          default=DefaultBotProperties(
              parse_mode=ParseMode.MARKDOWN_V2
          ))

dp = Dispatcher()
bells = BellSchedule(config.bells)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Приветственное сообщение"""
    await message.answer(escape_for_telegram("Привет!\n"
                                             "Для работы бота требуется задать группу:\n"
                                             "/setgroup [группа]\n"
                                             "и (при желании) подгруппу:\n"
                                             "/setsubgroup [1/2]\n"
                                             "\n"
                                             "/help для справки"))


@dp.message(Command("help"))
async def cmd_start(message: types.Message):
    await message.answer(escape_for_telegram("*Справка:*\n"
                                             "\n"
                                             "/start - приветственное сообщение\n"
                                             "\n"
                                             "/help - справка (это сообщение)\n"
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
                                             "/currweek - получить текущую неделю в любом случае (верхняя/нижняя)"))


@dp.message(Command("bells"))
async def cmd_bells(message: types.Message, command: CommandObject):
    """Вывод расписания звонков"""
    if command.args is None:
        if date.today().weekday() == 6:
            await message.answer("Сегодня воскресенье. \n"
                                 "Для того чтобы получить звонки на конкретный день напиши:\n"
                                 "/bells [день]\n"
                                 "`0`|`рабочий` - расписание для рабочего дня\n"
                                 "`1`|`выходной` - расписание для выходного дня\n"
                                 "`2`|`сокращённый` - расписание для сокращённого дня")
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
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
