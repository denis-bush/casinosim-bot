import random
# import os
from time import sleep

import telebot

# Инициализируем базу данных в виде словаря
database = {}
# token = os.getenv("token")
bot = telebot.TeleBot("631046420:AAHgOJwxSO8g1-hN9boIJYOC-nPEWKN-mDc")


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def startBot(message):
    if message.from_user.id not in database.keys():
        bot.send_message(message.chat.id, 'Привет! Я - бот, симулятор казино! Как к Вам можно обращаться?')
        bot.register_next_step_handler(message, registerUser)
    else:
        bot.send_message(message.chat.id, 'Вы уже зарегистрированы!')


# Регистрация нового пользователя
def registerUser(message):
    user_id = message.from_user.id
    username = message.text
    bot.send_message(message.chat.id, username + '? Хорошо, я запомнил!')
    # Внесение в БД и вызов главного меню
    database[user_id] = {'name': username, 'balance': 1000, 'bet': 0, 'score': 0, 'dice_won': 0, 'dice_lost': 0,
                         'slot_won': 0, 'slot_lost': 0}
    sleep(0.5)
    bot.send_message(message.chat.id, str(username) + ', Ваш стартовый баланс: ' +
                     str(database[user_id]['balance']) + ' очков')
    sleep(0.5)
    mainMenu(message)


# Клавиатура главного меню
def mainMenu(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
    b_dice = telebot.types.KeyboardButton(text='Сыграть в "Кости"')
    b_slot = telebot.types.KeyboardButton(text='Сыграть в Слот-машину')
    b_stat = telebot.types.KeyboardButton(text='Статистика профиля')
    b_help = telebot.types.KeyboardButton(text='Справка')
    b_reset = telebot.types.KeyboardButton(text='Сброс данных')
    keyboard.row(b_dice, b_slot)
    keyboard.row(b_stat)
    keyboard.row(b_help, b_reset)
    bot.send_message(message.chat.id, 'Чем могу помочь?', reply_markup=keyboard)


# Запуск игры в "Кости"
@bot.message_handler(func=lambda message: message.text == 'Сыграть в "Кости"' and message.content_type == 'text')
def diceStart(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    b_start = telebot.types.KeyboardButton(text='Начать игру в "Кости"')
    b_back = telebot.types.KeyboardButton(text='Вернуться в главное меню')
    keyboard.row(b_start, b_back)
    bot.send_message(message.chat.id, text='Добро пожаловать в игру кости!', reply_markup=keyboard)


# Кости
@bot.message_handler(func=lambda message: message.text == 'Начать игру в "Кости"' and message.content_type == 'text')
def askBet(message):
    bot.send_message(message.chat.id, text='Выберите свою ставку (макс. ставка - 100 очков)',
                     reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, setBet)


def setBet(message):
    bet = message.text
    if not str.isdigit(bet):
        bot.send_message(message.chat.id, text='Неккорректное значение, попробуйте ещё раз')
        askBet(message)
    elif int(bet) < 1 or int(bet) > 100:
        bot.send_message(message.chat.id, text='Неккорректное значение, попробуйте ещё раз')
        askBet(message)
    else:
        database[message.from_user.id]['bet'] = int(bet)
        dicePlay(message)


def dicePlay(message):
    die_faces = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅']
    die1 = random.randint(0, 5)
    die2 = random.randint(0, 5)
    die3 = random.randint(0, 5)
    die4 = random.randint(0, 5)
    diesum1 = die1 + die2
    diesum2 = die3 + die4
    user_id = message.from_user.id

    # Бросаем кости
    bot.send_message(message.chat.id, text='Бросок...', reply_markup=telebot.types.ReplyKeyboardRemove())
    sleep(1)
    bot.send_message(message.chat.id, text= str(database[user_id]['name']) + ': ' + die_faces[die1] + die_faces[die2]
                                            + '\n' + 'Бот: ' + die_faces[die3] + die_faces[die4])
    sleep(0.5)

    # Проверяем результат и зачисляем или снимаем очки
    if diesum1 > diesum2:
        database[user_id]['balance'] += database[user_id]['bet']
        database[user_id]['score'] += database[user_id]['bet']
        bot.send_message(message.chat.id, text='Поздравляю! Вы выиграли ' + str(database[user_id]['bet']) + ' очков!')
        sleep(0.5)
        bot.send_message(message.chat.id, text='Ваш баланс: ' + str(database[user_id]['balance']) + ' очков.')
    elif diesum1 < diesum2:
        database[user_id]['balance'] -= database[user_id]['bet']
        database[user_id]['score'] -= database[user_id]['bet']
        bot.send_message(message.chat.id, text='Неудача. Вы проиграли ' + str(database[user_id]['bet']) + ' очков.')
        sleep(0.5)
        bot.send_message(message.chat.id, text='Ваш баланс: ' + str(database[user_id]['balance']) + ' очков.')
    else:
        bot.send_message(message.chat.id, text='Ничья.')
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    b_again = telebot.types.KeyboardButton(text='Бросить ещё раз')
    b_stop = telebot.types.KeyboardButton(text='Закончить игру в "Кости"')
    keyboard.row(b_again, b_stop)
    sleep(0.5)
    bot.send_message(message.chat.id, text='Сыграем ещё?', reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'Бросить ещё раз' and message.content_type == 'text')
def diceAgain(message):
    dicePlay(message)


@bot.message_handler(func=lambda message: message.text == 'Закончить игру в "Кости"' and message.content_type == 'text')
def diceStop(message):
    user_id = message.from_user.id
    score = database[user_id]['score']
    if score >= 0:
        database[user_id]['dice_won'] += score
        bot.send_message(message.chat.id, text='Вы выиграли ' + str(score) + ' очков')
    else:
        database[user_id]['dice_lost'] += abs(score)
        bot.send_message(message.chat.id, text='Вы проиграли ' + str(abs(score)) + ' очков')
    database[user_id]['score'] = 0
    mainMenu(message)


# Возврат в главное меню
@bot.message_handler(func=lambda message: message.text == 'Вернуться в главное меню' and message.content_type == 'text')
def backToMenu(message):
    mainMenu(message)


# Запуск игры в слот-машину
@bot.message_handler(func=lambda message: message.text == 'Сыграть в Слот-машину' and message.content_type == 'text')
def slotStart(message):
    bot.send_message(message.chat.id, text='Слоты')


# Вывод статистики профиля
@bot.message_handler(func=lambda message: message.text == 'Статистика профиля' and message.content_type == 'text')
def printStats(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, text='Имя игрока: ' + str(database[user_id]['name']) + '\n' +
                     'Баланс: ' + str(database[user_id]['balance']) + ' очков' + '\n' +
                     'Выиграно в "Кости": ' + str(database[user_id]['dice_won']) + ' очков' + '\n' +
                     'Проиграно в "Кости": ' + str(database[user_id]['dice_lost']) + ' очков' + '\n' +
                     'Выиграно в Слот-машине: ' + str(database[user_id]['slot_won']) + ' очков' + '\n' +
                     'Проиграно в Слот-машине: ' + str(database[user_id]['slot_lost']) + ' очков')


# Вывод справочной информации
@bot.message_handler(func=lambda message: message.text == 'Справка' and message.content_type == 'text')
def helpMenu(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
    b_about = telebot.types.KeyboardButton(text='О программе')
    b_law = telebot.types.KeyboardButton(text='Законодательство РФ об азартных играх')
    b_back = telebot.types.KeyboardButton(text='Вернуться в главное меню')
    keyboard.row(b_about, b_law)
    keyboard.row(b_back)
    bot.send_message(message.chat.id, text='Выберите раздел', reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'О программе' and message.content_type == 'text')
def printAbout(message):
    from about import reply
    bot.send_message(message.chat.id, text=reply)


@bot.message_handler(func=lambda message: message.text == 'Законодательство РФ об азартных играх'
                                          and message.content_type == 'text')
def printLaw(message):
    from law import reply
    bot.send_message(message.chat.id, text=reply)


# Запрос удаления текущего пользователя
@bot.message_handler(func=lambda message: message.text == 'Сброс данных' and message.content_type == 'text')
def resetBot(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    b_yes = telebot.types.KeyboardButton(text='Да, удалить мой профиль')
    b_no = telebot.types.KeyboardButton(text='Нет, я передумал')
    keyboard.row(b_yes, b_no)
    bot.send_message(message.chat.id, text='Внимание! Данное действие удалит Ваш профиль и все связанные '
                                           'с ним данные! Вы уверены, что хотите продолжить?', reply_markup=keyboard)


# Удаление пользователя
@bot.message_handler(func=lambda message: message.text == 'Да, удалить мой профиль' and message.content_type == 'text')
def resetConfirm(message):
    bot.send_message(message.chat.id, text='Принято, удаляю данные из базы...',
                     reply_markup=telebot.types.ReplyKeyboardRemove())
    database.pop(message.from_user.id)


# Отмена удаления
@bot.message_handler(func=lambda message: message.text == 'Нет, я передумал' and message.content_type == 'text')
def resetDeny(message):
    mainMenu(message)


@bot.message_handler(content_types=['text'])
def textHandler(message):
   user_id = message.from_user.id
   if user_id not in database.keys():
       return bot.send_message(message.chat.id,
                               text='Пожалуйста, зарегистрируйтесь с помощью команды /start')
   text = message.text.lower()

   if text == 'привет':
       bot.send_message(message.chat.id, text='Привет! :)')
   elif text == 'пока':
       bot.send_message(message.chat.id, text='До встречи!')
   else:
       bot.send_message(message.chat.id,
                        text='Простите, я Вас не понимаю. Попробуйте выбрать команду из меню.')
       mainMenu(message)


if __name__ == '__main__':
    bot.polling(none_stop=True)