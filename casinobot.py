import random
import os
from time import sleep

from telebot import types
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

database = {}


def startBot(bot, update):
    bot.send_message(chat_id=update.message.chat.id, 
                     text='Привет! Я - бот, симулятор казино! Как к тебе можно обращаться?')
    user_id = update.message.from_user.id
    username = update.message.text
    
    bot.send_message(chat_id=update.message.chat.id, text=username + '? Хорошо, я запомнил!')
    database[user_id] = {"balance": 1000, 'dice_won': 0, 'dice_lost': 0}
    sleep(1.5)
    bot.send_message(chat_id=update.message.chat.id, 
                     text=username + ', твой стартовый баланс: ' + database[user_id]['balance'])


def mainMenu(bot, update):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    b_dice = types.KeyboardButton(text='Сыграть в "Кости"')
    b_slot = types.KeyboardButton(text='Сыграть в слот-машину')
    b_stat = types.KeyboardButton(text='Статистика профиля')
    b_help = types.KeyboardButton(text='Справка')
    b_reset = types.KeyboardButton(text='Сброс данных')
    keyboard.row(b_dice, b_slot)
    keyboard.row(b_stat)
    keyboard.row(b_help, b_reset)
     
    if update.message.text == 'Сыграть в "Кости"':
        return diceStart
    elif update.message.text == 'Сыграть в слот-машину':
        return slotStart
    elif update.message.text == 'Статистика профиля':
        return printStats
    elif update.message.text == 'Справка':
        return helpMenu
    elif update.message.text == 'Сброс данных':
        return resetBot
    else:
        bot.send_message(chat_id=update.message.chat.id, 
                         text='Прости, я тебя не понимаю. Попробуй выбрать команду из меню.')
        return mainMenu


def diceStart(bot, update):
    bot.send_message(chat_id=update.message.chat.id, text='Кости')


def slotStart(bot, update):
    bot.send_message(chat_id=update.message.chat.id, text='Слоты')


def printStats(bot, update):
    bot.send_message(chat_id=update.message.chat.id, text='Слоты')

def helpMenu(bot, update):
    bot.send_message(chat_id=update.message.chat.id, text='Справка')


def resetBot(bot, update):
    bot.send_message(chat_id=update.message.chat.id, text='Сброс')  

# update.message.reply_text(text="Чем могу быть полезен?",      
# @bot.message_handler(content_types=['text'])
# def askGame(message):
#   text=message.text
#    if text == "1":
#        msg = bot.send_message(chat_id=update.message.chat.id, 'Добро пожаловать в игру "Кости"! 🎲')
#        bot.register_next_step_handler(msg, diceStart)
#    elif text == "2":
#        msg = bot.send_message(chat_id, 'Данная функция всё ещё находится в разработке')
#        bot.register_next_step_handler(msg, askGame) 
#        return
#    else:
#        msg = bot.send_message(chat_id, 'Неверная команда, попробуйте ещё раз')	
#        bot.register_next_step_handler(msg, askGame)
#        return


def textHandler(bot, update):
    user_id = update.message.from_user.id
    if user_id not in database.keys():
        return bot.send_message(chat_id=update.message.chat_id, 
                                text="Пожалуйста, зарегистрируйся с помощью команды /start")
    text = update.message.text.lower()
    
    if text == "привет":
        bot.send_message(chat_id=update.message.chat_id, text='Привет! :)')
    elif text == "пока":
        bot.send_message(chat_id=update.message.chat_id, text='До встречи!')
    else:
        bot.send_message(chat_id=update.message.chat.id, 
                         text='Прости, я тебя не понимаю. Попробуй выбрать команду из меню.')
        return mainMenu

if __name__ == '__main__':
    token = os.getenv("token")
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", startBot))
    dispatcher.add_handler(MessageHandler(Filters.text, textHandler))
    
    updater.start_polling()
    updater.idle()