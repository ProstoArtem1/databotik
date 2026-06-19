from aiogram.fsm.state import State, StatesGroup

class WorkerRegistration(StatesGroup):
    name = State()
    skills = State()
    experience = State()
    salary = State()

class EmployerRegistration(StatesGroup):
    company_name = State()
    vacancy_title = State()
    requirements = State()
    salary = State()