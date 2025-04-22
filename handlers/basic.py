from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.enums import ParseMode
# Компоненты проекта
from core.my_utils import escape_for_telegram

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Приветственное сообщение"""
    await message.answer(escape_for_telegram("Привет!\n"
                                             "Для работы бота требуется зарегистрироваться:\n"
                                             "/register"
                                             "\n"
                                             "/help для справки"),
                         parse_mode=ParseMode.MARKDOWN_V2)


@router.message(Command("help"))
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
