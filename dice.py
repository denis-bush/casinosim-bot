def startGame(message):
    chat_id = message.chat.id
    text = message.text
    
    msg = bot.send_message(chat_id, 'Принято, ' + text + '!')	
    isRunning=False
    bot.register_next_step_handler(msg, start_handler)