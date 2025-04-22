import aiosqlite

# Файл базы данных
users_db_file = None


async def init_users_db(file: str = None):
    global users_db_file
    if file is not None:
        db_file = file
        if users_db_file is None:
            users_db_file = file
    elif users_db_file is not None:
        db_file = users_db_file
    else:
        raise ValueError("Not selected name of SQLite database file")
    async with aiosqlite.connect(db_file) as db:
        # Разрешение ключей из других таблиц
        await db.execute("PRAGMA foreign_keys = ON;")
        # Создание таблицы пользователей если отсутствует
        await db.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER primary key,
                        role VARCHAR(10) CHECK ( role IN ('student', 'teacher') ) DEFAULT NULL,
                        register_date DATE DEFAULT CURRENT_DATE NOT NULL,
                        notify_enabled BOOLEAN DEFAULT 1 NOT NULL 
                    )
                ''')
        # Создание таблицы учащихся если отсутствует
        await db.execute('''
                    CREATE TABLE IF NOT EXISTS students (
                        user_id INTEGER primary key,
                        group_id INTEGER NOT NULL,
                        subgroup INTEGER CHECK ( subgroup IN (1, 2) ),
                        first_name TEXT,
                        last_name TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                        FOREIGN KEY (group_id) REFERENCES groups(group_id) ON DELETE CASCADE 
                    )
                ''')
        # Создание таблицы учителей если отсутствует
        await db.execute('''
                    CREATE TABLE IF NOT EXISTS teachers (
                        user_id INTEGER primary key,
                        first_name TEXT,
                        last_name TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                    )
                ''')
        # Создание таблицы админов если отсутствует
        await db.execute('''
                    CREATE TABLE IF NOT EXISTS admins (
                        user_id INTEGER primary key,
                        control_admins BOOLEAN DEFAULT 0 NOT NULL,
                        manage_groups BOOLEAN DEFAULT 0 NOT NULL,
                        update_rights BOOLEAN DEFAULT 0 NOT NULL,
                        update_changes BOOLEAN DEFAULT 1 NOT NULL,
                        global_messages BOOLEAN DEFAULT 0 NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                    )
                ''')
        # Создание таблицы групп если отсутствует
        await db.execute('''
                    CREATE TABLE IF NOT EXISTS groups (
                        group_id INTEGER primary key autoincrement,
                        group_name VARCHAR(5) UNIQUE NOT NULL,
                        start_date DATE,
                        course INTEGER CHECK ( course BETWEEN 1 AND  4 ),
                        faculty_id INTEGER NOT NULL,
                        FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE 
                    )
                ''')
        # Создание таблицы с отделениями если отсутствует
        await db.execute('''
                    CREATE TABLE IF NOT EXISTS faculty (
                        faculty_id INTEGER primary key autoincrement,
                        faculty_name TEXT UNIQUE NOT NULL
                    )
                ''')
        # Если таблица с отделениями пуста заполнить по умолчанию
        cursor = await db.execute('SELECT COUNT(*) FROM faculty')
        count = (await cursor.fetchone())[0]
        if count == 0:
            await db.executemany(
                'INSERT INTO faculty (faculty_name) VALUES (?)',
                [
                    ('Радиотехническое',),
                    ('Машиностроительное',),
                    ('Юридическое',)
                ]
            )
        # Сохранить изменения
        await db.commit()
