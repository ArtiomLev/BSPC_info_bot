from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from my_escape_function import escape_for_telegram
import database

router = Router()


# ================================
# 1. Описание состояний FSM
# ================================
class RegStates(StatesGroup):
    role = State()  # выбор роли: student/teacher
    # состояния для студента
    group_select = State()  # выбор группы по ID из списка
    subgroup = State()  # выбор подгруппы (1 или 2)
    first_name = State()  # ввод/пропуск имени
    last_name = State()  # ввод фамилии
    # состояния для преподавателя
    t_first_name = State()  # ввод/пропуск имени
    t_last_name = State()  # ввод фамилии


# ================================
# 2. Старт регистрации
# ================================
@router.message(Command("register"))
async def cmd_register(message: types.Message, state: FSMContext):
    """
    Начало процесса регистрации.
    Очищаем предыдущий контекст и просим выбрать роль.
    """
    await state.clear()

    # Проверка наличия пользователя
    if await database.user_exists(message.from_user.id, database.users_db_file):
        await message.answer(escape_for_telegram("❌ Вы уже зарегистрированы!"))
        return

    # Строим две кнопки: студент / преподаватель
    kb = InlineKeyboardBuilder()
    kb.button(text="👩‍🎓 Студент", callback_data="reg:student")
    kb.button(text="👨‍🏫 Преподаватель", callback_data="reg:teacher")
    kb.adjust(2)

    await message.answer(
        "*Регистрация*\nВыберите вашу роль:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=kb.as_markup()
    )
    await state.set_state(RegStates.role)


# ================================
# 3. Обработка выбора роли
# ================================
@router.callback_query(lambda cb: cb.data and cb.data.startswith("reg:"), RegStates.role)
async def process_role(cb: types.CallbackQuery, state: FSMContext):
    """
    Сохраняем роль и показываем список требуемых полей.
    Для студента запрашиваем группу.
    Для преподавателя запрашиваем имя.
    """
    role = cb.data.split(":", 1)[1]
    await state.update_data(role=role)

    if role == "student":
        # Описание обязательных и опциональных полей
        text = escape_for_telegram(
            "*Поля для студента:*\n"
            "• группа\n"
            "• подгруппа\n"
            "• _имя_\n"
            "• _фамилия_\n"
            "\n"
            "\"_Необязательные поля_\""
        )
        await cb.message.edit_text(text, parse_mode=ParseMode.MARKDOWN)

        # Вывод списка групп
        rows = await database.get_groups(database.users_db_file)
        kb = InlineKeyboardBuilder()
        for gid, faculty, name in rows:
            kb.button(text=f"{name}", callback_data=f"grp_id:{gid}|grp_name:{name}")
        kb.adjust(4)
        await cb.message.answer(
            "Выберите группу из списка:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=kb.as_markup()
        )
        await state.set_state(RegStates.group_select)

    else:
        # Для преподавателя
        text = escape_for_telegram(
            "*Поля для преподавателя:*\n"
            "• фамилия\n"
            "• _имя_\n"
            "\n"
            "\"_Необязательные поля_\""
        )
        await cb.message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
        kb = InlineKeyboardBuilder()
        kb.button(text="Пропустить", callback_data="skip:name")
        kb.adjust(1)
        await cb.message.answer(
            "Введите *имя* (необязательно):", parse_mode=ParseMode.MARKDOWN,
            reply_markup=kb.as_markup()
        )
        await state.set_state(RegStates.t_first_name)


# ================================
# 4. Получение группы и выбор подгруппы
# ================================
@router.callback_query(lambda cb: cb.data.startswith("grp_id:"), RegStates.group_select)
async def process_group_select(cb: types.CallbackQuery, state: FSMContext):
    """Сохраняем group_id и переходим к выбору подгруппы"""
    data = cb.data.split("|", 2)
    gid = int(data[0].split(":", 1)[1])
    gname = data[1].split(":", 1)[1]
    await state.update_data(group_id=gid)

    kb = InlineKeyboardBuilder()
    kb.button(text="1️⃣", callback_data="sub:1")
    kb.button(text="2️⃣", callback_data="sub:2")
    kb.adjust(2)

    await cb.message.edit_text(
        f"Выбрана группа *{gname}* _(ID={gid})_", parse_mode=ParseMode.MARKDOWN
    )
    await cb.message.answer(
        "Выберите *подгруппу*:", parse_mode=ParseMode.MARKDOWN,
        reply_markup=kb.as_markup()
    )
    await state.set_state(RegStates.subgroup)


# ================================
# 5. Выбор подгруппы и запрос имени студента
# ================================
@router.callback_query(lambda cb: cb.data.startswith("sub:"), RegStates.subgroup)
async def process_subgroup(cb: types.CallbackQuery, state: FSMContext):
    """Сохраняем подгруппу и просим ввести имя"""
    sub = int(cb.data.split(":", 1)[1])
    await state.update_data(subgroup=sub)

    kb = InlineKeyboardBuilder()
    kb.button(text="Пропустить", callback_data="skip:fname")
    kb.adjust(1)

    await cb.message.edit_text(
        f"Подгруппа: *{sub}*", parse_mode=ParseMode.MARKDOWN
    )
    await cb.message.answer(
        "Введите *имя*:", parse_mode=ParseMode.MARKDOWN,
        reply_markup=kb.as_markup()
    )
    await state.set_state(RegStates.first_name)


# ================================
# 6. Обработка имени студента
# ================================
@router.callback_query(lambda cb: cb.data == "skip:fname", RegStates.first_name)
async def skip_fname(cb: types.CallbackQuery, state: FSMContext):
    """Пропуск ввода имени"""
    await state.update_data(first_name=None)

    kb = InlineKeyboardBuilder()
    kb.button(text="Пропустить", callback_data="skip:lname")
    kb.adjust(1)

    await cb.message.edit_text(
        escape_for_telegram("Имя пропущено.")
    )
    await cb.message.answer(
        "Введите *фамилию*:", parse_mode=ParseMode.MARKDOWN,
        reply_markup=kb.as_markup()
    )
    await state.set_state(RegStates.last_name)


@router.message(RegStates.first_name)
async def input_fname(message: types.Message, state: FSMContext):
    """Пользователь вводит имя"""
    await state.update_data(first_name=message.text.strip())
    await message.answer(
        f"Имя: *{message.text.strip()}*", parse_mode=ParseMode.MARKDOWN
    )

    kb = InlineKeyboardBuilder()
    kb.button(text="Пропустить", callback_data="skip:lname")
    kb.adjust(1)

    await message.answer(
        "Введите *фамилию* (обязательно):", parse_mode=ParseMode.MARKDOWN,
        reply_markup=kb.as_markup()
    )
    await state.set_state(RegStates.last_name)


# ================================
# 7. Получение фамилии и сохранение данных
# ================================

@router.callback_query(lambda cb: cb.data == "skip:lname", RegStates.last_name)
async def skip_lname(cb: types.CallbackQuery, state: FSMContext):
    """Пропуск ввода фамилии и сохранение данных"""
    await state.update_data(last_name=None)

    await cb.message.edit_text(
        escape_for_telegram("Фамилия пропущена.")
    )

    data = await state.get_data()
    role = data.get("role")

    if role == "student":
        # Сохраняем студента
        await database.save_student(
            user_id=cb.from_user.id,
            group_id=data.get("group_id"),
            subgroup=data.get("subgroup"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            db_path=database.users_db_file
        )
        await cb.message.answer(escape_for_telegram("✅ Регистрация завершена!"))
    else:
        await cb.message.edit_text(escape_for_telegram("❗ Преподаватель обязан ввести фамилию."))
        return


@router.message(RegStates.last_name)
async def input_last(message: types.Message, state: FSMContext):
    """
    Сохраняем пользователя в users,
    а затем в students или teachers через database
    """
    data = await state.get_data()
    role = data.get("role")
    last = message.text.strip()

    # Создаём или обновляем запись в users
    await database.create_user(message.from_user.id, role, database.users_db_file)

    if role == "student":
        # Сохраняем студента
        await database.save_student(
            user_id=message.from_user.id,
            group_id=data.get("group_id"),
            subgroup=data.get("subgroup"),
            first_name=data.get("first_name"),
            last_name=last,
            db_path=database.users_db_file
        )
    else:
        # Сохраняем преподавателя
        await database.save_teacher(
            user_id=message.from_user.id,
            first_name=data.get("first_name"),
            last_name=last,
            db_path=database.users_db_file
        )

    await message.answer(escape_for_telegram("✅ Регистрация завершена!"))

    # Завершаем FSM
    await state.clear()


# ================================
# Удаление пользователя
# ================================
@router.message(Command("unregister"))
async def cmd_unregister(message: types.Message):
    """Удаление пользователя из системы"""
    user_id = message.from_user.id

    if not await database.user_exists(user_id, database.users_db_file):
        await message.answer(escape_for_telegram("❌ Вы не зарегистрированы!"))
        return

    success = await database.delete_user(user_id, database.users_db_file)

    if success:
        await message.answer(escape_for_telegram("✅ Ваш аккаунт полностью удалён!"))
    else:
        await message.answer(escape_for_telegram("⚠️ Ошибка при удалении аккаунта\n"
                                                 "Обратитесь к администратору!"))
