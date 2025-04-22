from aiogram import Router, types
from aiogram.filters.command import Command, CommandObject
from aiogram.enums import ParseMode
from datetime import date
# Настройки
from configs.config_reader import config
# Компоненты проекта
from core.my_utils import escape_for_telegram
from core.bells import BellSchedule

router = Router()

bells = BellSchedule(config.bells)


@router.message(Command("bells"))
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
