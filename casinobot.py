import random
import os
from time import sleep

import telebot
# from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

database = {}
bot = telebot.TeleBot("631046420:AAHgOJwxSO8g1-hN9boIJYOC-nPEWKN-mDc")

@bot.message_handler(commands=['start'])
def startBot(message):
    bot.send_message(message.chat.id, 'Привет! Я - бот, симулятор казино! Как к тебе можно обращаться?')
    bot.register_next_step_handler(message, registerUser)


@bot.message_handler(commands=['start'])
def registerUser(message):
    user_id = message.from_user.id
    username = message.text
    bot.send_message(message.chat.id, username + '? Хорошо, я запомнил!')
    database[user_id] = {"balance": 1000, 'dice_won': 0, 'dice_lost': 0}
    sleep(1.5)
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


@bot.message_handler(commands=['Сыграть в "Кости"'])
def diceStart(message):
    bot.send_message(message.chat.id, text='Кости')


@bot.message_handler(commands=['Сыграть в слот-машину'])
def slotStart(message):
    bot.send_message(message.chat.id, text='Слоты')


@bot.message_handler(commands=['Статистика профиля'])
def printStats(message):
    bot.send_message(message.chat.id, text='Статистика')


@bot.message_handler(commands=['Справка'])
def helpMenu(message):
    bot.send_message(message.chat.id, text='Справка')


@bot.message_handler(commands=['Сброс данных'])
def resetBot(message):
    bot.send_message(message.chat.id, text='Сброс')  


@bot.message_handler(content_types=['text'])
def textHandler(message):
    user_id = message.from_user.id
    if user_id not in database.keys():
        return bot.send_message(message.chat.id,
                                text="Пожалуйста, зарегистрируйся с помощью команды /start")
    text = message.text.lower()

    if text == "привет":
        bot.send_message(message.chat.id, text='Привет! :)')
    elif text == "пока":
        bot.send_message(message.chat.id, text='До встречи!')
    else:
        bot.send_message(message.chat.id,
                         text='Прости, я тебя не понимаю. Попробуй выбрать команду из меню.')
        return mainMenu(message)

# update.message.reply_text(text="Чем могу быть полезен?",      
# @bot.message_handler(content_types=['text'])
# def askGame(message):
#   text=message.text
#    if text == "1":
#        msg = bot.send_message(message.chat.id, 'Добро пожаловать в игру "Кости"! 🎲')
#        bot.register_next_step_handler(msg, diceStart)
#    elif text == "2":
#        msg = bot.send_message(chat.id, 'Данная функция всё ещё находится в разработке')
#        bot.register_next_step_handler(msg, askGame) 
#        return
#    else:
#        msg = bot.send_message(chat.id, 'Неверная команда, попробуйте ещё раз')	
#        bot.register_next_step_handler(msg, askGame)
#        return




if __name__ == '__main__':
    bot.polling(none_stop=True)