import telebot
import bs4
from casinobot import start_handler, TOKEN, bot

def startGame(message):
    chat_id = message.chat.id
    text = message.text
    
    msg = bot.send_message(chat_id, 'Принято, ' + text + '!')	
    bot.send_message(chat_id, 'Напишите /start, чтобы начать')
    isRunning=False
    bot.register_next_step_handler(msg, start_handler)