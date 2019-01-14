import telebot
import bs4
import casinobot

TOKEN = "631046420:AAHgOJwxSO8g1-hN9boIJYOC-nPEWKN-mDc"
bot = telebot.TeleBot(TOKEN)

def startGame(message):
    chat_id = message.chat.id
    text = message.text
    
    msg = bot.send_message(chat_id, 'Принято, ' + text + '!')	
    isRunning=False
    bot.register_next_step_handler(msg, casinobot.start_handler)