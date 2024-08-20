import sqlite3


class DataBase:
    def __init__(self):
        self.db = sqlite3.connect('database/users.db')
        self.cursor = self.db.cursor()

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
        return result[0] if result else 'фильтр не задан'
