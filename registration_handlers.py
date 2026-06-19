
# registration_handlers.py

import sqlite3

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import WorkerRegistration, EmployerRegistration

router = Router()

from dotenv import load_dotenv
import os

load_dotenv()

DB_NAME = os.getenv("DB_NAME")


# ==========================================
# РЕГИСТРАЦИЯ РАБОТНИКА
# ==========================================

@router.message(F.text == "/worker")
async def start_worker_registration(message: Message, state: FSMContext):
    await state.set_state(WorkerRegistration.name)
    await message.answer("Введите ваше имя:")


@router.message(WorkerRegistration.name)
async def worker_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(WorkerRegistration.skills)
    await message.answer("Введите ваши навыки:")


@router.message(WorkerRegistration.skills)
async def worker_skills(message: Message, state: FSMContext):
    await state.update_data(skills=message.text)
    await state.set_state(WorkerRegistration.experience)
    await message.answer("Опишите ваш опыт работы:")


@router.message(WorkerRegistration.experience)
async def worker_experience(message: Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await state.set_state(WorkerRegistration.salary)
    await message.answer("Введите желаемую зарплату:")


@router.message(WorkerRegistration.salary)
async def worker_salary(message: Message, state: FSMContext):
    try:
        salary = int(message.text)
    except ValueError:
        await message.answer("Введите зарплату числом.")
        return

    data = await state.get_data()

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE telegram_id = ?",
            (message.from_user.id,)
        )

        user = cursor.fetchone()

        if not user:
            await message.answer(
                "Сначала зарегистрируйте пользователя в таблице users."
            )
            await state.clear()
            return

        user_id = user[0]

        cursor.execute(
            """
            INSERT INTO resumes
            (user_id, name, skills, experience, salary, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (
                user_id,
                data["name"],
                data["skills"],
                data["experience"],
                salary
            )
        )

        conn.commit()

    await message.answer("✅ Резюме успешно сохранено.")
    await state.clear()


# ==========================================
# РЕГИСТРАЦИЯ РАБОТОДАТЕЛЯ
# ==========================================

@router.message(F.text == "/employer")
async def start_employer_registration(message: Message, state: FSMContext):
    await state.set_state(EmployerRegistration.company_name)
    await message.answer("Введите название компании:")


@router.message(EmployerRegistration.company_name)
async def employer_company_name(message: Message, state: FSMContext):
    await state.update_data(company_name=message.text)
    await state.set_state(EmployerRegistration.vacancy_title)
    await message.answer("Введите название вакансии:")


@router.message(EmployerRegistration.vacancy_title)
async def employer_vacancy_title(message: Message, state: FSMContext):
    await state.update_data(vacancy_title=message.text)
    await state.set_state(EmployerRegistration.requirements)
    await message.answer("Введите требования к кандидату:")


@router.message(EmployerRegistration.requirements)
async def employer_requirements(message: Message, state: FSMContext):
    await state.update_data(requirements=message.text)
    await state.set_state(EmployerRegistration.salary)
    await message.answer("Введите предлагаемую зарплату:")


@router.message(EmployerRegistration.salary)
async def employer_salary(message: Message, state: FSMContext):
    try:
        salary = int(message.text)
    except ValueError:
        await message.answer("Введите зарплату числом.")
        return

    data = await state.get_data()

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE telegram_id = ?",
            (message.from_user.id,)
        )

        user = cursor.fetchone()

        if not user:
            await message.answer(
                "Сначала зарегистрируйте пользователя в таблице users."
            )
            await state.clear()
            return

        user_id = user[0]

        cursor.execute(
            """
            INSERT INTO vacancies
            (
                user_id,
                company_name,
                title,
                requirements,
                salary,
                is_active
            )
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (
                user_id,
                data["company_name"],
                data["vacancy_title"],
                data["requirements"],
                salary
            )
        )

        conn.commit()

    await message.answer("✅ Вакансия успешно опубликована.")
    await state.clear()

