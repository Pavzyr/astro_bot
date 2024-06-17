from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from collections import defaultdict

# Состояния диалога
WAITING_FOR_INPUT = range(1)

# Хранилище пользовательских данных
user_data_store = defaultdict(dict)

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("💎 Индивидуальный прогноз", callback_data='individual')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Выберите опцию:", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    # Переход к диалогу ожидания ввода
    if query.data == 'individual':
        query.edit_message_text(text="Пожалуйста, введите свое сообщение:")
        return WAITING_FOR_INPUT

def receive_input(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_input = update.message.text
    user_data_store[user_id]['individual_input'] = user_input

    update.message.reply_text(f"Ваш ввод сохранен: {user_input}")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Действие отменено.')
    return ConversationHandler.END

def main():
    updater = Updater("6982950113:AAFB3undU2ditRkLlk0EdRmKtvCDrjl-zz0", use_context=True)

    # Создание обработчиков
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button, pattern='^individual$')],
        states={
            WAITING_FOR_INPUT: [MessageHandler(Filters.text & ~Filters.command, receive_input)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()