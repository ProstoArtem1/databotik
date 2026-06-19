# database.py

import sqlite3

DB_NAME = "job_bot.db"


def create_tables():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # Пользователи
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            role TEXT NOT NULL,
            username TEXT
        )
        """)

        # Резюме
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            skills TEXT,
            experience TEXT,
            salary INTEGER,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)

        # Вакансии
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vacancies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            company_name TEXT NOT NULL,
            title TEXT NOT NULL,
            requirements TEXT,
            salary INTEGER,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)

        # Матчи (связи работодатель ↔ работник)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_id INTEGER NOT NULL,
            worker_id INTEGER NOT NULL,
            status TEXT NOT NULL CHECK (
                status IN ('pending', 'connected')
            ),
            FOREIGN KEY (employer_id) REFERENCES users(id),
            FOREIGN KEY (worker_id) REFERENCES users(id)
        )
        """)

        conn.commit()


if __name__ == "__main__":
    create_tables()
    print("База данных успешно создана.")