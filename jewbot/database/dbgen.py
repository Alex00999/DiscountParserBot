import sqlite3

# Название файла базы данных
db_filename = 'users.db'

# Подключение к базе данных (если файл не существует, он будет создан)
conn = sqlite3.connect(db_filename)

# Создание объекта курсора для выполнения SQL-запросов
cursor = conn.cursor()

# SQL-запрос для создания таблицы
create_table_query = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    filter TEXT NOT NULL
);
'''

# Выполнение запроса для создания таблицы
cursor.execute(create_table_query)

# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()

print(f"База данных '{db_filename}' и таблица 'users' успешно созданы.")
