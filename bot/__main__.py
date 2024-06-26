# 1. На команду /start отправляется сообщение: «user_name, Добро пожаловать в компанию DamnIT»
# 2. После этого сообщение спрашиваем: «Напишите свое ФИО» - тут нельзя написать цифры
# 3. После этого сообщения: «Укажите Ваш номер телефона» - формат 7 999 999 99 99
# 4. После этого сообщения: «Напишите любой комментарий» - можно написать любое сообщение
# 5. Сообщение: «Последний шаг! Ознакомься с вводными положениями» + файл (отправлю вместе с заданием) + кнопка «Далее»
# 6. Сообщение «Ознакомился» + кнопка «ДА!» - если нажимаем, то п.7
# 7. Последнее сообщение: «Спасибо за успешную регистрацию» + фото (отправлю вместе с заданием)
# 8. Заявки приходят на Ваш личный id чата

import asyncio
from aiogram import Bot, Dispatcher, types, Router
from bot.config import TOKEN, ADMIN_ID
from api.models import User
from api.requests import create_user
from bot import markups 
from aiogram.filters.command import CommandStart 
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import re

bot = Bot(token=TOKEN)
router = Router()

class UserState(StatesGroup):
    choosing_fio = State()
    choosing_phone = State()
    choosing_comment = State()
    finishing = State()


@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await message.answer(message.from_user.username + ', Добро пожаловать в компанию DamnIT')
    await message.answer('Напишите свое ФИО')

    await state.update_data(user_id=message.from_user.id,username=message.from_user.username)
    await state.set_state(UserState.choosing_fio)

@router.message(UserState.choosing_fio)
async def get_fio(message: types.Message, state: FSMContext):

    if not any(char.isdigit() for char in message.text):
        await state.update_data(fio=message.text)

        await message.answer('Укажите Ваш номер телефона (в формате 7 999 999 99 99)')
        await state.set_state(UserState.choosing_phone)
    else:
        await message.answer('ФИО не должно содержать цифры')

@router.message(UserState.choosing_phone)
async def get_phone(message: types.Message, state: FSMContext):
    if re.match(r'^7\s\d{3}\s\d{3}\s\d{2}\s\d{2}$', message.text):
        await state.update_data(phone=message.text)

        await message.answer('Напишите любой комментарий')
        await state.set_state(UserState.choosing_comment)
    else:
        await message.answer('Номер телефона должен быть в формате 7 999 999 99 99')

@router.message(UserState.choosing_comment)
async def get_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)

    await message.answer('Последний шаг! Ознакомься с вводными положениями')
    file = types.FSInputFile('bot/content/test.pdf')
    await message.answer_document(file)
    await message.answer('Ознакомился?', reply_markup=markups.aggreement)
    await state.set_state(UserState.finishing)



@router.message(UserState.finishing)
async def get_confirmation(message: types.Message, state: FSMContext):
    if message.text == 'Да!':

        photo = types.FSInputFile('bot/content/photo.jpg')
        await message.answer_photo(photo, caption='Спасибо за успешную регистрацию', reply_markup = markups.empty)
        user = User(** await state.get_data())
        create_user(user) # Заглушка для создания пользователя в базе данных
        await bot.send_message(ADMIN_ID, f'Пришла новая заявка от @{user.username}\nЕго ФИО: {user.fio}\nномер телефона: {user.phone}\nкомментарий: {user.comment}')

        await state.clear()
    else:
        await message.answer('Для завершения регистрации ознакомьтесь с вводными положениями')
        
        file = types.FSInputFile('bot/content/test.pdf')
        await message.answer_document(file)
        

    

async def main():
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())