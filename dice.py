import telebot
import bs4


def startGame(message):
    from casinobot import TOKEN, bot
    chat_id = message.chat.id
    text = message.text
    
    msg = bot.send_message(chat_id, 'Принято, ' + text + '!')	
    bot.send_message(chat_id, 'Напишите /start, чтобы начать')
    isRunning=False
    bot.register_next_step_handler(msg, endGame)

def endGame (message):
    from casinobot import start_handler 
    return start_handler()
    