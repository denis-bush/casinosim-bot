import telebot
import bs4
import parser

#main variables
TOKEN = "631046420:AAHgOJwxSO8g1-hN9boIJYOC-nPEWKN-mDc"
bot = telebot.TeleBot(TOKEN)

#handlers
@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    bot.send_message(message.chat.id, 'Привет, когда я вырасту, ты сможешь сыграть со мной в казино')


@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text.lower()
    chat_id = message.chat.id
    if text == "привет":
        bot.send_message(chat_id, 'Привет, я бот - симулятор казино.')
    elif text == "сыграем?":
        bot.send_message(chat_id, 'Мы ещё закрыты, пожалуйста, приходите позже')
    else:
        bot.send_message(chat_id, 'Говори понятнее')
		
bot.polling()