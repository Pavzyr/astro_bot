from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext


def admin_pannel(query, context: CallbackContext, msg_ex=False):
    keyboard = [
        [InlineKeyboardButton("Добавить прогноз", callback_data="add_progn")],
        [InlineKeyboardButton("Изменить инфо", callback_data="add_info")],
        [
            InlineKeyboardButton(
                "Назад в меню администратора", callback_data="admin_pannel"
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if msg_ex:
        query.edit_message_text("Меню администратора", reply_markup=reply_markup)
    else:
        query.message.reply_text("Меню администратора", reply_markup=reply_markup)


def add_progn(query, context: CallbackContext, update):
    query.edit_message_text("Введите дату")


def add_info(query, context: CallbackContext, update):
    query.edit_message_text("Введите инфо")
