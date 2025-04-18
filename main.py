import asyncio
import logging
from datetime import date
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command, CommandObject
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config_reader import config
from bells import BellSchedule
from my_escape_function import escape_for_telegram

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value(),
          default=DefaultBotProperties(
              parse_mode=ParseMode.MARKDOWN_V2
          )
          )

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
                                             "/help для справки")
                         )


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
                                             "/week - получить текущую неделю (верхняя/нижняя)"))


@dp.message(Command("bells"))
async def cmd_bells(message: types.Message, command: CommandObject):
    """Вывод расписания звонков"""
    if command.args is None:
        if date.today().weekday() == 7:
            await message.answer("Сегодня воскресенье. \n"
                                 "Для того чтобы получить звонки на конкретный день напиши:\n"
                                 "/bells [день]\n"
                                 "`0`|`рабочий` - расписание для рабочего дня\n"
                                 "`1`|`выходной` - расписание для выходного дня\n"
                                 "`2`|`сокращённый` - расписание для сокращённого дня")
            return
        else:
            if date.today().weekday() == 6:
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


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
