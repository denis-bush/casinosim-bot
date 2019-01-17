import random
import os
from time import sleep

import telebot
# from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

database = {}
# token = os.getenv("token")
bot = telebot.TeleBot("631046420:AAHgOJwxSO8g1-hN9boIJYOC-nPEWKN-mDc")

@bot.message_handler(commands=['start'])
def startBot(message):
    if message.from_user.id in database.keys():
        bot.send_message(message.chat.id, 'Привет! Я - бот, симулятор казино! Как к тебе можно обращаться?')
        bot.register_next_step_handler(message, registerUser)
    else:
        bot.send_message(message.chat.id, 'Ты уже зарегистрировался!')


@bot.message_handler(commands=['start'])
def registerUser(message):
    user_id = message.from_user.id
    username = message.text
    bot.send_message(message.chat.id, username + '? Хорошо, я запомнил!')
    database[user_id] = {"balance": 1000, 'dice_won': 0, 'dice_lost': 0}
    sleep(1)
    bot.send_message(message.chat.id, str(username) + ', твой стартовый баланс: ' + str(database[user_id]['balance']))
    mainMenu(message)

@bot.message_handler(commands=['menu'])
def mainMenu(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
    b_dice = telebot.types.KeyboardButton(text='Сыграть в "Кости"')
    b_slot = telebot.types.KeyboardButton(text='Сыграть в слот-машину')
    b_stat = telebot.types.KeyboardButton(text='Статистика профиля')
    b_help = telebot.types.KeyboardButton(text='Справка')
    b_reset = telebot.types.KeyboardButton(text='Сброс данных')
    keyboard.row(b_dice, b_slot)
    keyboard.row(b_stat)
    keyboard.row(b_help, b_reset)
    bot.send_message(message.chat.id, 'Чем могу помочь?', reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'Сыграть в "Кости"' and message.content_type == 'text')
def diceStart(message):
    bot.send_message(message.chat.id, text='Кости')


@bot.message_handler(func=lambda message: message.text == 'Сыграть в слот-машину' and message.content_type == 'text')
def slotStart(message):
    bot.send_message(message.chat.id, text='Слоты')


@bot.message_handler(func=lambda message: message.text == 'Статистика профиля' and message.content_type == 'text')
def printStats(message):
    bot.send_message(message.chat.id, text='Статистика')


@bot.message_handler(func=lambda message: message.text == 'Справка' and message.content_type == 'text')
def helpMenu(message):
    bot.send_message(message.chat.id, text='Справка')


@bot.message_handler(func=lambda message: message.text == 'Сброс данных' and message.content_type == 'text')
def resetBot(message):
    bot.send_message(message.chat.id, text='Сброс')
    database.pop(message.from_user.id)


# @bot.message_handler(content_types=['text'])
# def textHandler(message):
#    user_id = message.from_user.id
#    if user_id not in database.keys():
#        return bot.send_message(message.chat.id,
#                                text="Пожалуйста, зарегистрируйся с помощью команды /start")
#    text = message.text.lower()

#    if text == "привет":
#        bot.send_message(message.chat.id, text='Привет! :)')
#    elif text == "пока":
#        bot.send_message(message.chat.id, text='До встречи!')
#    else:
#        bot.send_message(message.chat.id,
#                         text='Прости, я тебя не понимаю. Попробуй выбрать команду из меню.')
#        return mainMenu(message)


if __name__ == '__main__':
    bot.polling(none_stop=True)