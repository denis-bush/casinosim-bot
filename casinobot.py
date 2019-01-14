import telebot
import bs4
import parser
import dice

#Токен
TOKEN = "631046420:AAHgOJwxSO8g1-hN9boIJYOC-nPEWKN-mDc"
bot = telebot.TeleBot(TOKEN)

#Функции
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
        msg = bot.send_message(chat_id, 'Добро пожаловать в игру "Кости"! 🎲')
        bot.register_next_step_handler(msg, dice.startGame)
    elif text == "2":
        msg = bot.send_message(chat_id, 'Данная функция всё ещё находится в разработке')
        bot.register_next_step_handler(msg, askGame)
        return