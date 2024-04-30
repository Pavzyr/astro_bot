import sqlite3
import calendar
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext


def start(update: Update, context: CallbackContext, msg_ex=False):
    keyboard = [
        [InlineKeyboardButton("INFO", callback_data='info')],
        [InlineKeyboardButton("Регистрация", callback_data='register')],
        [InlineKeyboardButton("Бектест", callback_data='backtest')],
        [InlineKeyboardButton("Прогноз", callback_data='today')],
        [InlineKeyboardButton("Подписка", callback_data='buy')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if msg_ex:
        update.edit_message_text('Меню бота', reply_markup=reply_markup)
    else:
        update.message.reply_text('Меню бота', reply_markup=reply_markup)


def menu(update: Update, context: CallbackContext, msg):
    keyboard = [
        [InlineKeyboardButton("Назад в меню", callback_data='menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.edit_message_text(msg, reply_markup=reply_markup, parse_mode='HTML')


def registration_check(update) -> str:
    ''' Проверка роли пользователя в БД. '''
    user = update.effective_user
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT role FROM users WHERE user_id=?;', (user.id,))
    role = c.fetchone()
    if role is not None:
        return role[0] 
    else:
        return 'unauthorized'


def create_calendar(year=None, month=None):
    if year is None: 
        year = datetime.now().year
    if month is None: 
        month = datetime.now().month
    keyboard = []
    row = [InlineKeyboardButton(f"{calendar.month_name[month]} {year}", callback_data="ignore")]
    keyboard.append(row)
    row = []
    for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
        row.append(InlineKeyboardButton(day, callback_data="ignore"))
    keyboard.append(row)
    month_calendar = calendar.monthcalendar(year, month)
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(" ", callback_data="ignore"))
            else:
                row.append(InlineKeyboardButton(str(day), callback_data=f"calendar-day-{year}-{month}-{day}"))
        keyboard.append(row)
    row = []
    previous_month = month - 1 if month > 1 else 12
    previous_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    row.append(InlineKeyboardButton("<- Пред. месяц", callback_data=f"change-month-{previous_year}-{previous_month}"))
    row.append(InlineKeyboardButton("След. месяц ->", callback_data=f"change-month-{next_year}-{next_month}"))
    keyboard.append(row)
    row = []
    row.append(InlineKeyboardButton("Назад в меню", callback_data='menu'))
    keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    command = query.data
    if command == "register":
        register(query, context, update)
    elif command == "backtest":
        backtest(query, context, update)
    elif command == "buy":
        buy(query, context)
    elif command == "today":
        today(query, context, update)
    elif command == "menu":
        start(query, context, True)
    elif command == "info":
        info(query, context)
    elif command.startswith("calendar-day-"):
        da, _, year, month, day = command.split('-')[:5]
        date = datetime(int(year), int(month), int(day))
        if date.strftime('%d.%m.%Y') == datetime.now().strftime('%d.%m.%Y'):
            today(query, context, update)
        else:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute('SELECT text FROM data WHERE date=?;', (date.strftime('%d.%m.%Y'),))
            msg = c.fetchone()
            if msg is not None:
                msg = msg[0] 
            else:
                msg = 'На эту дату у нас нет прогноза.'
            conn.close()
            menu(query, context, msg)
    elif command.startswith("change-month-"):
        parts = command.split('-')
        _, year, month = parts[1], parts[2], parts[3]
        query.edit_message_text("Please choose a date:", reply_markup=create_calendar(int(year), int(month)))


def register(query, context: CallbackContext, update):
    user = update.effective_user
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (user_id, username, first_name, last_name, role) VALUES (?, ?, ?, ?, "user")',
                  (user.id, user.username, user.first_name, user.last_name))
        conn.commit()
        keyboard = [
            [InlineKeyboardButton("Бектест", callback_data='backtest')],
            [InlineKeyboardButton("Назад в меню", callback_data='menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text('Вы успешно зарегистрированы!', reply_markup=reply_markup)
    except sqlite3.IntegrityError:
        menu(query, context, f'{user.first_name} {user.last_name} Вы уже зарегистрированы.')
    finally:
        conn.close()


def buy(query: Update, context: CallbackContext):
    menu(query, context, 'Здесь будет оплата')


def backtest(query, context: CallbackContext, update):
    role = registration_check(update)
    if role == 'user':
        query.edit_message_text("Выберире дату:",
                                reply_markup=create_calendar())
    else:
        keyboard = [
            [InlineKeyboardButton("Регистрация", callback_data='register')],
            [InlineKeyboardButton("Назад в меню", callback_data='menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text('Для бектеста необходима регистрация. Она полностью бесплатна и происходит всего за один клик!', reply_markup=reply_markup)


def today(query: Update, context: CallbackContext, update):
    role = registration_check(update)
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT text FROM data WHERE date=?;', (datetime.now().strftime('%d.%m.%Y'),))
    msg = c.fetchone()
    msg = msg[0]
    conn.close()
    if role == 'subscriber':
        menu(query, context, msg)
    else:
        keyboard = [
            [InlineKeyboardButton("Перейти к оплате", callback_data='buy')],
            [InlineKeyboardButton("Назад в меню", callback_data='menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text('Для просмотра актуального прогноза необходима активная подписка!', reply_markup=reply_markup)


def info(query: Update, context: CallbackContext):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT "text" FROM "data" WHERE id=2;')
    msg = c.fetchone()
    msg = msg[0]
    conn.close()
    keyboard = [
            [InlineKeyboardButton("Один", callback_data='1'), InlineKeyboardButton("Два", callback_data='1'), InlineKeyboardButton("Три", callback_data='1')],
            [InlineKeyboardButton("Назад в меню", callback_data='menu')],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(msg, reply_markup=reply_markup, parse_mode='HTML')
    
    


def main():
    updater = Updater("6873708372:AAF1HxDdrK_cGIke7FuFDit91nMlG3eWQ5c", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()