import sqlite3


class DataBase:
    def __init__(self):
        self.db = sqlite3.connect('database/users.db')
        self.cursor = self.db.cursor()

    def add_user(self, telegram_id: int, user_filter: str):
        query = """
        INSERT OR IGNORE INTO users (telegram_id, filter) 
        VALUES (?, ?);
        """
        self.cursor.execute(query, (telegram_id, user_filter))
        self.db.commit()

    def get_users(self):
        query = """
        SELECT telegram_id, filter FROM users;
        """
        self.cursor.execute(query)
        self.db.commit()
        return self.cursor.fetchall()
