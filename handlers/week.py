from aiogram import Router, types
from aiogram.filters.command import Command
from datetime import date
# Компоненты программы
from core.my_utils import escape_for_telegram
from core.week import Week

router = Router()


@router.message(Command("week"))
async def cmd_week(message: types.Message):
    week = Week()
    if date.today().weekday() == 6:
        next_week = week.next_week()
        answer = "Сегодня воскресенье\n"
        answer += "Следующая неделя *" + next_week.week_type().upper() + "*"
    else:
        answer = "Сейчас *" + week.week_type().upper() + "* неделя"
    await message.answer(escape_for_telegram(answer))


@router.message(Command("currweek"))
async def cmd_currweek(message: types.Message):
    week = Week()
    answer = "Сейчас *" + week.week_type().upper() + "* неделя"
    await message.answer(escape_for_telegram(answer))


@router.message(Command("nextweek"))
async def cmd_nextweek(message: types.Message):
    week = Week()
    next_week = week.next_week()
    answer = "Следующая неделя *" + next_week.week_type().upper() + "*"
    await message.answer(escape_for_telegram(answer))
