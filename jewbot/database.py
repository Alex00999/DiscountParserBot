import sqlite3
import os


class DataBase:
    def __init__(self, db_filename='database/users.db'):
        # Проверка наличия директории и создание при необходимости
        os.makedirs(os.path.dirname(db_filename), exist_ok=True)

        # Подключение к базе данных (если файл не существует, он будет создан)
        self.db = sqlite3.connect(db_filename)
        self.cursor = self.db.cursor()

        # SQL-запрос для создания таблицы, если она еще не существует
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY NOT NULL,
            filter TEXT NOT NULL
        );
        '''

        # Выполнение запроса для создания таблицы
        self.cursor.execute(create_table_query)
        self.db.commit()

    def add_user(self, telegram_id: int, user_filter: str):
        query = """
        INSERT OR REPLACE INTO users (telegram_id, filter) 
        VALUES (?, ?);
        """
        self.cursor.execute(query, (telegram_id, user_filter))
        self.db.commit()

    def get_users(self):
        query = """
        SELECT telegram_id, filter FROM users;
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_user_filter(self, user_id: int):
        query = """
        SELECT filter FROM users WHERE telegram_id = ?;
        """
        self.cursor.execute(query, (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None
