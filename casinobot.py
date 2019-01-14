import telebot
import bs4
import parser

#main variables
TOKEN = "631046420:AAHgOJwxSO8g1-hN9boIJYOC-nPEWKN-mDc"
bot = telebot.TeleBot(TOKEN)

#handlers
@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    global isRunning
    isRunning=False
    if not isRunning:
        chat_id = message.chat.id
        bot.send_message(chat_id, 'Привет! Я - бот, симулятор казино!')
        text = message.text
        msg = bot.send_message(chat_id, 'Во что сыграем? 1 - кости, 2 - слот-машина')
        bot.register_next_step_handler(msg, askGame) #Выбираем игру
        isRunning = True

def askGame(message):
    chat_id = message.chat.id
    text = message.text
    if text == "1":
        msg = bot.send_message(chat_id, 'Запускаю...')
        bot.register_next_step_handler(msg, dice)
    elif text == "2":
        msg = bot.send_message(chat_id, 'Данная функция всё ещё находится в разработке')
        bot.register_next_step_handler(msg, askGame)
        return
    else:
        msg = bot.send_message(chat_id, 'Неверная команда, попробуйте ещё раз')	
        bot.register_next_step_handler(msg, askGame)
        return

def dice(message):
    chat_id = message.chat.id
    text = message.text
    bot.send_message(chat_id, 'Добро пожаловать в игру "Кости"! Press any key to continue')
    msg = bot.send_message(chat_id, 'Принято, ' + text + '!')	
    isRunning=False
    bot.register_next_step_handler(msg, start_handler)

@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text.lower()
    chat_id = message.chat.id
    if text == "привет":
        bot.send_message(chat_id, 'Привет, я бот - симулятор казино.')
    elif text == "сыграем?":
        bot.send_message(chat_id, 'Мы ещё закрыты, пожалуйста, приходите позже')
    elif text == "стоп":
        msg = bot.send_message(chat_id, 'Возвращаюсь в главное меню')
        bot.register_next_step_handler(msg, start_handler)
    else:
        bot.send_message(chat_id, 'Я тебя не понимаю')
		
bot.polling(none_stop=True)