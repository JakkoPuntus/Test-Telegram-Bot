from aiogram import types


aggreement = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[])
aggreement.keyboard.append([types.KeyboardButton(text='Да!')])