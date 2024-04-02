# 1. На команду /start отправляется сообщение: «user_name, Добро пожаловать в компанию DamnIT»
# 2. После этого сообщение спрашиваем: «Напишите свое ФИО» - тут нельзя написать цифры
# 3. После этого сообщения: «Укажите Ваш номер телефона» - формат 7 999 999 99 99
# 4. После этого сообщения: «Напишите любой комментарий» - можно написать любое сообщение
# 5. Сообщение: «Последний шаг! Ознакомься с вводными положениями» + файл (отправлю вместе с заданием) + кнопка «Далее»
# 6. Сообщение «Ознакомился» + кнопка «ДА!» - если нажимаем, то п.7
# 7. Последнее сообщение: «Спасибо за успешную регистрацию» + фото (отправлю вместе с заданием)
# 8. Заявки приходят на Ваш личный id чата

from aiogram import Bot, Dispatcher, types
from config import TOKEN
from api.models import User
from api.requests import save_user

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user = User(user_id=message.from_user.id, username=message.from_user.username)

    await message.answer(message.from_user.username, ', Добро пожаловать в компанию DamnIT')
    await message.answer('Напишите свое ФИО')
    dp.register_message_handler(get_fio, content_types=types.ContentTypes.TEXT, user = user)

async def get_fio(message: types.Message, user: User):
    user.fio = message.text

    await message.answer('Укажите Ваш номер телефона')
    dp.register_message_handler(get_phone, content_types=types.ContentTypes.TEXT)

async def get_phone(message: types.Message, user: User):
    user.phone = message.text

    await message.answer('Напишите любой комментарий')
    dp.register_message_handler(get_comment, content_types=types.ContentTypes.TEXT, user = user)

async def get_comment(message: types.Message, user: User):
    user.comment = message.text

    await message.answer('Последний шаг! Ознакомься с вводными положениями')
    await message.answer_document('file_id')
    await message.answer('Далее')
    dp.register_message_handler(get_confirmation, content_types=types.ContentTypes.TEXT, user = user)

async def get_confirmation(message: types.Message, user: User):
    if message.text == 'Ознакомился':
        await message.answer('Спасибо за успешную регистрацию')
        save_user(user) #делаем вид, что сохраняем пользователя в базу данных
        await message.answer_photo('photo_id')
    else:
        await message.answer('Для завершения регистрации ознакомьтесь с вводными положениями')
        await message.answer_document('file_id')
        await message.answer('Далее')
        dp.register_message_handler(get_confirmation, content_types=types.ContentTypes.TEXT)

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)