import re
from dateutil.parser import parse
from datetime import datetime
from database import db_insert

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart

from aiogram.types import (KeyboardButton, Message,
                           ReplyKeyboardRemove)
from aiogram.utils.keyboard import ReplyKeyboardBuilder


from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.base import StorageKey

from config import bot_token


bot = Bot(token=bot_token)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class FSMFillForm(StatesGroup):
    fix_simping = State()
    fill_simp_subject = State()
    fill_simp_object = State()
    fill_simp_description = State()
    validate_simping = State()

vadim_storage_key = StorageKey(bot.id, chat_id=812669559, user_id=812669559)

vadim_state = FSMContext(storage, key=vadim_storage_key)

valid_state = State()


but = KeyboardButton(text='Зафиксировать симпинг')

kb_builder = ReplyKeyboardBuilder()
kb_builder.row(but)
keyboard = kb_builder.as_markup(one_time_keyboard=True, resize_keyboard=True)

but_val_yes = KeyboardButton(text='Да')
but_val_no = KeyboardButton(text='Нет')
kb_builder_validate = ReplyKeyboardBuilder()
kb_builder_validate.row(but_val_yes, but_val_no)
keyboard_val = kb_builder_validate.as_markup(one_time_keyboard=True, resize_keyboard=True)


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        text = 'Привет, я антисимп бот. Зафиксировать симпинг?',
        reply_markup=keyboard
    )


@dp.message(Command(commands='cancel'))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Начинаем заново. Зафиксировать симпинг?',
        reply_markup=keyboard
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.set_state(default_state)


@dp.message(F.text == 'Зафиксировать симпинг', StateFilter(default_state))
async def other_date_income(message: Message, state: FSMContext):
    await message.answer(text='Кто симпил?',
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(FSMFillForm.fill_simp_subject)


@dp.message(StateFilter(FSMFillForm.fill_simp_subject))
async def other_date_income(message: Message, state: FSMContext):
    await message.answer(text='Кому симпил?')
    await state.update_data(user_id=message.from_user.id)
    await state.update_data(user_name=message.from_user.username)
    await state.update_data(dt=message.date)
    await state.update_data(subject=message.text)
    await state.set_state(FSMFillForm.fill_simp_object)


@dp.message(StateFilter(FSMFillForm.fill_simp_object))
async def other_date_income(message: Message, state: FSMContext):
    await message.answer(text='Как симпил?')
    await state.update_data(object=message.text)
    await state.set_state(FSMFillForm.fill_simp_description)


@dp.message(StateFilter(FSMFillForm.fill_simp_description))
async def other_date_income(message: Message, state: FSMContext):
    await message.answer(text='Симпинг зафиксирован. Благодарю за бдительность')
    await state.update_data(description=message.text)
    await state.set_state(default_state)

    
    d = await state.get_data()
    print(d)
    db_insert(d['user_id'], d['user_name'], d['dt'], d['subject'], d['object'], d['description'])

    await bot.send_message(chat_id=812669559, 
                           text=f'''
Зафиксирован симпинг. Необходима валидация.
Кто симпил: {d['subject']}
Кому симпил: {d['object']}
Как симпил: {d['description']} 
Это симпинг?                                           
''', 
                           reply_markup=keyboard_val)

    await vadim_state.set_state(valid_state)


@dp.message(StateFilter(valid_state))
async def other_date_income(message: Message, state: FSMContext):
    await message.answer(text='Провалидировано')
    await state.set_state(default_state)

    



dp.run_polling(bot)