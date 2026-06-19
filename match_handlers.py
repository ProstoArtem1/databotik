
# match_handlers.py

import sqlite3

from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

router = Router()

from dotenv import load_dotenv
import os

load_dotenv()

DB_NAME = os.getenv("DB_NAME")


# =====================================
# ОТПРАВКА ЗАПРОСА НА СВЯЗЬ
# =====================================

@router.callback_query(F.data.startswith("connect_request:"))
async def send_connect_request(callback: CallbackQuery, bot: Bot):

    worker_id = int(callback.data.split(":")[1])

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # Работодатель
        cursor.execute(
            "SELECT id FROM users WHERE telegram_id = ?",
            (callback.from_user.id,)
        )

        employer = cursor.fetchone()

        if not employer:
            await callback.answer("Работодатель не найден")
            return

        employer_id = employer[0]

        # Создаем match
        cursor.execute(
            """
            INSERT INTO matches
            (employer_id, worker_id, status)
            VALUES (?, ?, 'pending')
            """,
            (employer_id, worker_id)
        )

        # Информация о работодателе
        cursor.execute(
            """
            SELECT telegram_id, username
            FROM users
            WHERE id = ?
            """,
            (employer_id,)
        )

        employer_data = cursor.fetchone()

        # Информация о работнике
        cursor.execute(
            """
            SELECT telegram_id
            FROM users
            WHERE id = ?
            """,
            (worker_id,)
        )

        worker_data = cursor.fetchone()

        conn.commit()

    employer_username = employer_data[1] or "Без username"
    worker_telegram_id = worker_data[0]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Підтвердити контакт",
                    callback_data=f"accept_contact:{employer_id}"
                )
            ]
        ]
    )

    await bot.send_message(
        worker_telegram_id,
        f"Вами заинтересовалась компания @{employer_username}",
        reply_markup=keyboard
    )

    await callback.answer("Запрос отправлен")

# =====================================
# ПОДТВЕРЖДЕНИЕ КОНТАКТА
# =====================================

@router.callback_query(F.data.startswith("accept_contact:"))
async def accept_contact(callback: CallbackQuery, bot: Bot):

    employer_id = int(callback.data.split(":")[1])

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # Работник
        cursor.execute(
            """
            SELECT id, username
            FROM users
            WHERE telegram_id = ?
            """,
            (callback.from_user.id,)
        )

        worker = cursor.fetchone()

        if not worker:
            await callback.answer("Работник не найден")
            return

        worker_id = worker[0]
        worker_username = worker[1]

        # Работодатель
        cursor.execute(
            """
            SELECT telegram_id, username
            FROM users
            WHERE id = ?
            """,
            (employer_id,)
        )

        employer = cursor.fetchone()

        if not employer:
            await callback.answer("Работодатель не найден")
            return

        employer_telegram_id = employer[0]
        employer_username = employer[1]

        # Меняем статус
        cursor.execute(
            """
            UPDATE matches
            SET status = 'connected'
            WHERE employer_id = ?
            AND worker_id = ?
            """,
            (employer_id, worker_id)
        )

        conn.commit()

    worker_link = (
        f"https://t.me/{worker_username}"
        if worker_username else "Username отсутствует"
    )

    employer_link = (
        f"https://t.me/{employer_username}"
        if employer_username else "Username отсутствует"
    )

    await bot.send_message(
        employer_telegram_id,
        f"""
✅ Контакт подтвержден!

Работник:
{worker_link}
"""
    )

    await bot.send_message(
        callback.from_user.id,
        f"""
✅ Контакт подтвержден!

Работодатель:
{employer_link}
"""
    )

    await callback.message.edit_text(
        "✅ Контакт успешно подтвержден."
    )

    await callback.answer()

