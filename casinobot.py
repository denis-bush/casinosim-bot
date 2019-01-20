from random import randint
from time import sleep
from telebot import TeleBot, types

# Импорт токена из переменной окружения (неисп.)
# import os
# token = os.getenv("token")
from config import token
bot = TeleBot(token)

# Инициализируем базу данных в виде словаря
DATABASE = {}


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def startBot(message):
    if message.from_user.id not in DATABASE.keys():
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
    DATABASE[user_id] = {'name': username, 'balance': 1000, 'bet': 0, 'score': 0, 'dice_won': 0, 'dice_lost': 0,
                         'slot_won': 0, 'slot_lost': 0, 'game_id': 0}
    sleep(0.5)
    bot.send_message(message.chat.id, str(username) + ', Ваш стартовый баланс: ' +
                     str(DATABASE[user_id]['balance']) + ' очков')
    sleep(0.5)
    mainMenu(message)


# Клавиатура главного меню
def mainMenu(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    b_dice = types.KeyboardButton(text='🎲 Сыграть в "Кости"')
    b_slot = types.KeyboardButton(text='🎰 Сыграть в Слот-машину')
    b_stat = types.KeyboardButton(text='📊 Статистика профиля')
    b_help = types.KeyboardButton(text='❓ Справка')
    b_reset = types.KeyboardButton(text='❌ Сброс данных')
    keyboard.row(b_dice, b_slot)
    keyboard.row(b_stat)
    keyboard.row(b_help, b_reset)
    bot.send_message(message.chat.id, 'Чем могу помочь?', reply_markup=keyboard)


# Запуск игры в "Кости"
@bot.message_handler(func=lambda message: message.text == '🎲 Сыграть в "Кости"' and message.content_type == 'text')
def diceStart(message):
    DATABASE[message.from_user.id]['game_id'] = 1
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    b_start = types.KeyboardButton(text='Начать игру')
    b_back = types.KeyboardButton(text='🔙 Вернуться в главное меню')
    keyboard.row(b_start, b_back)
    bot.send_message(message.chat.id, text='Добро пожаловать в игру кости!', reply_markup=keyboard)


# Выбор ставки для игры
@bot.message_handler(func=lambda message: message.text == 'Начать игру' and message.content_type == 'text')
def askBet(message):
    bot.send_message(message.chat.id, text='Выберите свою ставку (макс. ставка - 50 очков)',
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, setBet)


# Проверка введённого значения и утверждение ставки для игры
def setBet(message):
    user_id = message.from_user.id
    bet = message.text
    if not str.isdigit(bet):
        bot.send_message(message.chat.id, text='Неккорректное значение, попробуйте ещё раз')
        askBet(message)
    elif int(bet) < 1 or int(bet) > 50:
        bot.send_message(message.chat.id, text='Неккорректное значение, попробуйте ещё раз')
        askBet(message)
    else:
        DATABASE[user_id]['bet'] = int(bet)
        if DATABASE[user_id]['game_id'] == 1:
            dicePlay(message)
        elif DATABASE[user_id]['game_id'] == 2:
            slotPlay(message)
        else:
            return


# "Ход" (бросок) в "Кости"
def dicePlay(message):
    die_faces = ['', '⚀', '⚁', '⚂', '⚃', '⚄', '⚅']
    # Подсчитываем результат броска
    die1 = randint(1, 6)
    die2 = randint(1, 6)
    die3 = randint(1, 6)
    die4 = randint(1, 6)
    diesum1 = die1 + die2
    diesum2 = die3 + die4
    user_id = message.from_user.id
    bet = DATABASE[user_id]['bet']
    curr_score = 0

    # Выводим результат броска
    bot.send_message(message.chat.id, text='Бросок... 🎲🎲', reply_markup=types.ReplyKeyboardRemove())
    sleep(1)
    bot.send_message(message.chat.id, text= str(DATABASE[user_id]['name']) + ': ' + die_faces[die1] + die_faces[die2]
                                            + '\n' + 'Бот: ' + die_faces[die3] + die_faces[die4])
    sleep(0.5)

    # Проверяем результат и зачисляем или снимаем очки
    if diesum1 > diesum2:
        DATABASE[user_id]['balance'] += bet
        DATABASE[user_id]['dice_won'] += bet
        curr_score += bet
        bot.send_message(message.chat.id, text='Поздравляю! 🎉 Вы выиграли ' + str(bet) + ' очков!')
        sleep(0.5)
        bot.send_message(message.chat.id, text='💰 Ваш баланс: ' + str(DATABASE[user_id]['balance']) + ' очков.')
    elif diesum1 < diesum2:
        DATABASE[user_id]['balance'] -= bet
        DATABASE[user_id]['dice_lost'] += bet
        curr_score -= bet
        bot.send_message(message.chat.id, text='Неудача. 😔 Вы проиграли ' + str(bet) + ' очков.')
        sleep(0.5)
        bot.send_message(message.chat.id, text='💰 Ваш баланс: ' + str(DATABASE[user_id]['balance']) + ' очков.')
    else:
        curr_score = 0
        bot.send_message(message.chat.id, text='Ничья.')
    DATABASE[user_id]['score'] += curr_score

    # Ожидаем следующего хода
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    b_again = types.KeyboardButton(text='Сыграть ещё раз')
    b_stop = types.KeyboardButton(text='Закончить игру')
    keyboard.row(b_again, b_stop)
    sleep(0.5)
    bot.send_message(message.chat.id, text='Сыграем ещё?', reply_markup=keyboard)


# Продолжение игры в "Кости"
@bot.message_handler(func=lambda message: message.text == 'Сыграть ещё раз' and message.content_type == 'text')
def playAgain(message):
    if DATABASE[message.from_user.id]['game_id'] == 1:
        dicePlay(message)
    elif DATABASE[message.from_user.id]['game_id'] == 2:
        slotPlay(message)


# Остановка текущей игры, проверка и вывод итогового результата
@bot.message_handler(func=lambda message: message.text == 'Закончить игру' and message.content_type == 'text')
def gameOver(message):
    user_id = message.from_user.id
    score = DATABASE[user_id]['score']
    if score >= 0:
        bot.send_message(message.chat.id, text='Вы выиграли ' + str(score) + ' очков')
    else:
        bot.send_message(message.chat.id, text='Вы проиграли ' + str(abs(score)) + ' очков')
    DATABASE[user_id]['score'] = 0
    mainMenu(message)


# Возврат в главное меню
@bot.message_handler(func=lambda message: message.text == '🔙 Вернуться в главное меню'
                                          and message.content_type == 'text')
def backToMenu(message):
    mainMenu(message)


# Запуск игры в слот-машину
@bot.message_handler(func=lambda message: message.text == '🎰 Сыграть в Слот-машину' and message.content_type == 'text')
def slotStart(message):
    DATABASE[message.from_user.id]['game_id'] = 2
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    b_start = types.KeyboardButton(text='Начать игру')
    b_back = types.KeyboardButton(text='🔙 Вернуться в главное меню')
    b_table = types.KeyboardButton(text='📋 Таблица выигрышей')
    keyboard.row(b_start, b_back)
    keyboard.row(b_table)
    bot.send_message(message.chat.id, text='Добро пожаловать в Слот-машину!', reply_markup=keyboard)


# Вывод таблицы выигрышей в Слот-машине
@bot.message_handler(func=lambda message: message.text == '📋 Таблица выигрышей' and message.content_type == 'text')
def slotTable(message):
    txtfile = open('paytable.txt', 'r')
    reply = txtfile.read()
    bot.send_message(message.chat.id, text=reply)
    txtfile.close()


# "Ход" (нажатие на рычаг) в Слот-машине
def slotPlay(message):
    user_id = message.from_user.id
    bet = DATABASE[user_id]['bet']
    curr_score = bet

    # Формируем игровую линию Слот-машины
    slot_cells = ['🍒', '🍋', '🍉', '🥝', '🔔', '💸']
    cell1 = randint(0, 5)
    cell2 = randint(0, 5)
    cell3 = randint(0, 5)
    slot_line = slot_cells[cell1] + slot_cells[cell2] + slot_cells[cell3]

    # Сверяем полученную линию с таблицей и вычисляем выигрыш
    if slot_line == '💸💸💸':
        curr_score *= 50
        bot.send_message(message.chat.id, text='Джекпот!!!')
    elif slot_line == '🔔🔔🔔':
        curr_score *= 20
    elif slot_line == '🥝🥝🥝':
        curr_score *= 15
    elif slot_line == '🍉🍉🍉':
        curr_score *= 10
    elif slot_line == '🍋🍋🍋':
        curr_score *= 5
    elif slot_line == '🍒🍒🍒':
        curr_score *= 3
    elif '🍒🍒' in slot_line:
        curr_score *= 2
    elif '🍒' in slot_line:
        curr_score *= 1
    else:
        curr_score *= 0

    # Зачисляем или снимаем полученные очки с вычетом изначальной ставки
    curr_score -= bet
    DATABASE[user_id]['balance'] += curr_score
    DATABASE[user_id]['score'] += curr_score

    # Проверяем и выводим результат
    bot.send_message(message.chat.id, text='Запускаю Слот-машину... 📍', reply_markup=types.ReplyKeyboardRemove())
    sleep(1)
    bot.send_message(message.chat.id, text=slot_line)
    sleep(0.5)
    if curr_score > 0:
        DATABASE[user_id]['slot_won'] += curr_score
        bot.send_message(message.chat.id, text='Поздравляю! 🎉 Вы выиграли ' + str(curr_score) + ' очков!')
        sleep(0.5)
        bot.send_message(message.chat.id, text='💰 Ваш баланс: ' + str(DATABASE[user_id]['balance']) + ' очков.')
    elif curr_score < 0:
        DATABASE[user_id]['slot_lost'] += abs(curr_score)
        bot.send_message(message.chat.id, text='Ставка потеряна. 😔 Вы проиграли ' + str(bet) + ' очков.')
        sleep(0.5)
        bot.send_message(message.chat.id, text='💰 Ваш баланс: ' + str(DATABASE[user_id]['balance']) + ' очков.')
    else:
        bot.send_message(message.chat.id, text='Ставка вернулась.')
        bot.send_message(message.chat.id, text='💰 Ваш баланс: ' + str(DATABASE[user_id]['balance']) + ' очков.')

    # Ожидаем следующего хода
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    b_again = types.KeyboardButton(text='Сыграть ещё раз')
    b_stop = types.KeyboardButton(text='Закончить игру')
    keyboard.row(b_again, b_stop)
    sleep(0.5)
    bot.send_message(message.chat.id, text='Сыграем ещё?', reply_markup=keyboard)


# Вывод статистики профиля
@bot.message_handler(func=lambda message: message.text == '📊 Статистика профиля' and message.content_type == 'text')
def printStats(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, text='👤 Имя игрока: ' + str(DATABASE[user_id]['name']) + '\n' +
                     '💰 Баланс: ' + str(DATABASE[user_id]['balance']) + ' очков' + '\n' +
                     '🎲 Выиграно в "Кости": ' + str(DATABASE[user_id]['dice_won']) + ' очков' + '\n' +
                     '🎲 Проиграно в "Кости": ' + str(DATABASE[user_id]['dice_lost']) + ' очков' + '\n' +
                     '🎰 Выиграно в Слот-машине: ' + str(DATABASE[user_id]['slot_won']) + ' очков' + '\n' +
                     '🎰 Проиграно в Слот-машине: ' + str(DATABASE[user_id]['slot_lost']) + ' очков')


# Вывод списка справочной информации
@bot.message_handler(func=lambda message: message.text == '❓ Справка' and message.content_type == 'text')
def helpMenu(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    b_about = types.KeyboardButton(text='📄 О программе')
    b_law = types.KeyboardButton(text='📕 Законодательство РФ об азартных играх')
    b_back = types.KeyboardButton(text='🔙 Вернуться в главное меню')
    keyboard.row(b_about, b_law)
    keyboard.row(b_back)
    bot.send_message(message.chat.id, text='Выберите раздел', reply_markup=keyboard)


# Печать документа "О программе"
@bot.message_handler(func=lambda message: message.text == '📄 О программе' and message.content_type == 'text')
def printAbout(message):
    txtfile = open('about.txt', 'r')
    reply = txtfile.read()
    bot.send_message(message.chat.id, text=reply)
    txtfile.close()


# Печать документа "Законодательство РФ об азартных играх"
@bot.message_handler(func=lambda message: message.text == '📕 Законодательство РФ об азартных играх'
                                          and message.content_type == 'text')
def printLaw(message):
    txtfile = open('law.txt', 'r')
    reply = txtfile.read()
    bot.send_message(message.chat.id, text=reply)
    txtfile.close()


# Запрос удаления текущего пользователя
@bot.message_handler(func=lambda message: message.text == '❌ Сброс данных' and message.content_type == 'text')
def resetBot(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    b_yes = types.KeyboardButton(text='Да, удалить мой профиль')
    b_no = types.KeyboardButton(text='Нет, я передумал')
    keyboard.row(b_yes, b_no)
    bot.send_message(message.chat.id, text='⚠ Внимание! Данное действие удалит Ваш профиль и все связанные '
                                           'с ним данные! Вы уверены, что хотите продолжить?', reply_markup=keyboard)


# Удаление пользователя
@bot.message_handler(func=lambda message: message.text == 'Да, удалить мой профиль' and message.content_type == 'text')
def resetConfirm(message):
    bot.send_message(message.chat.id, text='Принято, удаляю данные из базы...',
                     reply_markup=types.ReplyKeyboardRemove())
    DATABASE.pop(message.from_user.id)


# Отмена удаления
@bot.message_handler(func=lambda message: message.text == 'Нет, я передумал' and message.content_type == 'text')
def resetDeny(message):
    mainMenu(message)


# Обработчик прочих текстовых сообщений
@bot.message_handler(content_types=['text'])
def textHandler(message):
   user_id = message.from_user.id
   if user_id not in DATABASE.keys():
       return bot.send_message(message.chat.id,
                               text='Пожалуйста, зарегистрируйтесь с помощью команды /start')
   text = message.text.lower()

   if 'привет' in text:
       bot.send_message(message.chat.id, text='Привет! :)')
   elif 'пока' in text:
       bot.send_message(message.chat.id, text='До встречи!')
   else:
       bot.send_message(message.chat.id,
                        text='Простите, я Вас не понимаю. Попробуйте выбрать команду из меню.')
       mainMenu(message)


# Запуск и поддержка работы бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
