from aiogram import types

empty = types.ReplyKeyboardRemove()


aggreement = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[])
aggreement.keyboard.append([types.KeyboardButton(text='Да!')])