from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.enums import ParseMode
# Настройки
from configs.config_reader import config
# Компоненты проекта
from core.my_utils import escape_for_telegram

router = Router()
