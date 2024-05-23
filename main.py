import calendar
import os
import sqlite3
import logging
import time
import requests

from datetime import datetime
from dotenv import load_dotenv
from yoomoney import Client, Quickpay

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    MessageHandler,
    Filters
)


def start(update: Update, context: CallbackContext, msg_ex=False):
    if msg_ex:
        profile_list = registration_check(update.from_user)
    else:
        profile_list = registration_check(update.effective_user)

    if profile_list[0] in ('user', 'admin'):
        keyboard = [
            [InlineKeyboardButton("🆓 Бектест", callback_data='backtest')],
            [InlineKeyboardButton("🔎 Прогноз", callback_data='today')],
            [InlineKeyboardButton("🆔 Профиль", callback_data='profile')],
            [InlineKeyboardButton("❓ INFO", callback_data='info')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if msg_ex:
            update.edit_message_text('Меню бота', reply_markup=reply_markup)
        else:
            update.message.reply_text('Меню бота', reply_markup=reply_markup)
    else:
        keyboard = [
            [InlineKeyboardButton("❓ INFO", callback_data='info')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        register(context, update)
        update.message.reply_text('Привет! Предлагаю ознакомиться c функционалом бота.', reply_markup=reply_markup)


def commands(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    command = query.data
    if command == "backtest_info":
        backtest_info(query)
    elif command == "prognosis_info":
        prognosis_info(query)
    elif command == "individual_info":
        individual_info(query)
    elif command == "backtest":
        query.edit_message_text("Выберире дату:", reply_markup=create_calendar())
    elif command == "buy":
        buy(query, update)
    elif command == "today":
        today(query, update)
    elif command == "menu":
        start(query, context, True)
    elif command == "profile":
        profile(query, update)
    elif command == "info":
        info(query)
    elif command == "pay_check":
        pay_check(query, update)
    elif command.startswith("pay_request-"):
        value = command.split('-')[1]
        profile_list = registration_check(update.effective_user)
        payment_code = f"bill||{datetime.now().strftime('%d.%m.%Y-%H:%M')}||{value}||{profile_list[2]}"
        payment_url = pay_url_generate(value, payment_code, profile_list[3])
        pay_button(query, payment_code, payment_url)
    elif command.startswith("bill"):
        conn = sqlite3.connect('astro_db.db')
        c = conn.cursor()
        c.execute(
            'SELECT href, value FROM payments WHERE payment_code=?;',
            (command,)
        )
        payment_url = c.fetchone()
        value = payment_url[1]
        payment_url = payment_url[0]
        conn.close()
        pay_check_target(query, update, command, value, payment_url)
    elif command.startswith("calendar-day-"):
        backtest_after_date_recieve(query, update, command)
    elif command.startswith("change-month-"):
        page_of_calendar(command, query)
    elif command.startswith("delete_payment-"):
        label = command.replace('delete_payment-', '')
        delete_payment(query, label)


def menu(update, msg):
    keyboard = [
        [InlineKeyboardButton("↩️ Назад в меню", callback_data='menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.edit_message_text(msg, reply_markup=reply_markup, parse_mode='HTML')


def registration_check(user):
    conn = sqlite3.connect('astro_db.db')
    c = conn.cursor()
    c.execute('SELECT role, balance, expired, user_id FROM users WHERE user_id=?;', (user.id,))
    role = c.fetchone()
    if role is not None:
        return [role[0], role[1], role[2], role[3]]
    else:
        return ['unauthorized']


def create_calendar(year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month
    keyboard = []
    row = [
        InlineKeyboardButton(
            f"{calendar.month_name[month]} {year}",
            callback_data="ignore"
            ),
        ]
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
                row.append(InlineKeyboardButton(
                    str(day),
                    callback_data=f"calendar-day-{year}-{month}-{day}"
                    ))
        keyboard.append(row)
    row = []
    previous_month = month - 1 if month > 1 else 12
    previous_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    row.append(InlineKeyboardButton(
        "<- Пред. месяц",
        callback_data=f"change-month-{previous_year}-{previous_month}"
        ))
    row.append(InlineKeyboardButton(
        "След. месяц ->",
        callback_data=f"change-month-{next_year}-{next_month}"
        ))
    keyboard.append(row)
    row = []
    row.append(InlineKeyboardButton(
        "↩️ Назад в меню", callback_data='menu'
        ))
    keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)


def page_of_calendar(command, query):
    parts = command.split('-')
    _, year, month = parts[1], parts[2], parts[3]
    query.edit_message_text(
        "Выберите дату:",
        reply_markup=create_calendar(int(year), int(month))
        )


def profile(query, update):
    profile_list = registration_check(update.effective_user)
    if profile_list[0] == 'user':
        keyboard = [
            [InlineKeyboardButton("💳 Оплатить подписку", callback_data='buy')],
            [InlineKeyboardButton("🆓 Бектест", callback_data='backtest')],
            [InlineKeyboardButton("🔎 Проверить оплату", callback_data='pay_check')],
            [InlineKeyboardButton("↩️ Назад в меню", callback_data='menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            f'👤 Ваш ID - {profile_list[3]} (пользователь) \n💰 Баланс - {profile_list[1]} ₽.\nОплатите подписку для актуального прогноза, или станьте премиум пользователем для индивидуального астропрогноза.',
            reply_markup=reply_markup
            )
    elif profile_list[0] == 'admin':
        keyboard = [
            [InlineKeyboardButton("💳 Оплатить подписку", callback_data='buy')],
            [InlineKeyboardButton("🆓 Бектест", callback_data='backtest')],
            [InlineKeyboardButton("🔎 Проверить оплату", callback_data='pay_check')],
            [InlineKeyboardButton("↩️ Назад в меню", callback_data='menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            f'👤 Ваш ID - {profile_list[3]} (Администратор) \n💰 Баланс - {profile_list[1]} ₽.',
            reply_markup=reply_markup
            )
    else:
        keyboard = [
            [InlineKeyboardButton("↩️ Назад в меню", callback_data='menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            'Возникла ошибка с вашим профилем, обратитесь к администратору!',
            reply_markup=reply_markup
            )


def register(context, update):
    user = update.effective_user
    conn = sqlite3.connect('astro_db.db')
    c = conn.cursor()
    try:
        c.execute(
            'INSERT INTO users (user_id, username, first_name, last_name, role, balance, expired) VALUES (?, ?, ?, ?, "user", ?, ?)',
                  (user.id, user.username, user.first_name, user.last_name, '0', '0'))
        conn.commit()
        logger.info(f"Пользователь {user.id} успешно зарегистрировался")
        send_messages(context, user_ids, f"Пользователь {user.id} {user.username} {user.first_name} {user.last_name} успешно зарегистрировался. (Сообщение только администраторам)")
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()


def buy(query, update):
    profile_list = registration_check(update.effective_user)
    conn = sqlite3.connect('astro_db.db')
    c = conn.cursor()
    c.execute(
        'SELECT payment_code, value FROM payments WHERE user_id=? AND payment_status="0";',
        (profile_list[3],)
    )
    rows = c.fetchall()
    if len(rows) < 3:
        keyboard = [
            [InlineKeyboardButton("Пополнить на 10 ₽", callback_data='pay_request-10')],
            [InlineKeyboardButton("Пополнить на 750 ₽", callback_data='pay_request-750')],
            [InlineKeyboardButton("Пополнить на 4500 ₽", callback_data='pay_request-4500')],
            [InlineKeyboardButton("↩️ Назад в меню", callback_data='menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            f'Выберите сумму для пополнения:',
            reply_markup=reply_markup
            )
    else:
        keyboard = [
            [InlineKeyboardButton("🔎 Проверить оплаты", callback_data='pay_check')],
            [InlineKeyboardButton("↩️ Назад в меню", callback_data='menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            f'У Вас слишком много активных ссылок на оплаты! Проверьте их и отмените ненужные:',
            reply_markup=reply_markup
            )


def backtest_after_date_recieve(query, update, command):
    da, _, year, month, day = command.split('-')[:5]
    date = datetime(int(year), int(month), int(day))
    if date.strftime('%d.%m.%Y') == datetime.now().strftime('%d.%m.%Y'):
        today(query, update)
    elif date.strftime('%d.%m.%Y') > datetime.now().strftime('%d.%m.%Y'):
        msg = 'Функция бектеста позволяет посмотреть только историю. '
        'Прогнозы доступны для индивидуальных подписчиков.'
        menu(query, msg)
    else:
        conn = sqlite3.connect('astro_db.db')
        c = conn.cursor()
        c.execute('SELECT text FROM data WHERE date=?;', (date.strftime('%d.%m.%Y'),))
        msg = c.fetchone()
        if msg is not None:
            msg = msg[0] 
        else:
            msg = 'На эту дату у нас нет прогноза.'
        conn.close()
        menu(query, msg)


def today(query, update):
    profile_list = registration_check(update.effective_user)
    if profile_list[0] == 'subscriber':
        conn = sqlite3.connect('astro_db.db')
        c = conn.cursor()
        c.execute('SELECT text FROM data WHERE date=?;',
                  (datetime.now().strftime('%d.%m.%Y'),))
        msg = c.fetchone()
        if msg is not None:
            msg = msg[0]
        else:
            msg = 'На этот день прогноз еще не добавлен'
        conn.close()
        menu(query, msg)
    else:
        keyboard = [
            [InlineKeyboardButton("💳 Перейти к оплате", callback_data='buy')],
            [InlineKeyboardButton("↩️ Назад в меню", callback_data='menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            'Для просмотра актуального прогноза необходима активная подписка!',
            reply_markup=reply_markup
            )


def info(query):
    conn = sqlite3.connect('astro_db.db')
    c = conn.cursor()
    c.execute('SELECT "page_text" FROM "info" WHERE page_name="info";')
    msg = c.fetchone()
    msg = msg[0]
    conn.close()
    keyboard = [
            [
                InlineKeyboardButton("Бектест", callback_data='backtest_info'),
                InlineKeyboardButton("Актуальный прогноз", callback_data='prognosis_info')
            ],
            [InlineKeyboardButton("Индивидуальный прогноз", callback_data='individual_info')],
            [InlineKeyboardButton("↩️ В меню", callback_data='menu')],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(msg, reply_markup=reply_markup, parse_mode='HTML')


def backtest_info(query):
    conn = sqlite3.connect('astro_db.db')
    c = conn.cursor()
    c.execute('SELECT "page_text" FROM "info" WHERE page_name="backtest";')
    msg = c.fetchone()
    msg = msg[0]
    conn.close()
    msg_points = msg.split('.')
    msg_send = ''
    for msg in msg_points:
        msg_send += msg
        query.edit_message_text(msg_send, parse_mode='HTML')
        time.sleep(3)
    menu(query, msg_send)


def prognosis_info(query):
    conn = sqlite3.connect('astro_db.db')
    c = conn.cursor()
    c.execute('SELECT "page_text" FROM "info" WHERE page_name="prognosis";')
    msg = c.fetchone()
    msg = msg[0]
    conn.close()
    msg_points = msg.split('.')
    msg_send = ''
    for msg in msg_points:
        msg_send += msg
        query.edit_message_text(msg_send, parse_mode='HTML')
        time.sleep(3)
    menu(query, msg_send)


def individual_info(query):
    conn = sqlite3.connect('astro_db.db')
    c = conn.cursor()
    c.execute('SELECT "page_text" FROM "info" WHERE page_name="individual";')
    msg = c.fetchone()
    msg = msg[0]
    conn.close()
    msg_points = msg.split(' ')
    msg_send = ''
    for msg in msg_points:
        msg_send += msg + ' '
        query.edit_message_text(msg_send, parse_mode='HTML')
        time.sleep(0.1)
    menu(query, msg_send)


def pay_url_generate(value, payment_code, user_id):
    quickpay = Quickpay(
            receiver="4100118665757287",
            quickpay_form="shop",
            targets=f"Пополнение кошелька Астро Trade прогноз на {value} ₽",
            paymentType="SB",
            sum=value,
            label=payment_code,
            successURL="https://web.telegram.org/k/#@Astropredikt_bot"
            )
    conn = sqlite3.connect('astro_db.db')
    c = conn.cursor()
    c.execute(
        'INSERT INTO payments (user_id, payment_code, payment_status, value, href) VALUES (?, ?, ?, ?, ?)',
        (user_id, payment_code, '0', value, quickpay.redirected_url))
    conn.commit()
    conn.close()
    return quickpay.redirected_url


def pay_button(query, payment_code, payment_url):
    pay_list = payment_code.split('||')
    keyboard = [
            [InlineKeyboardButton("💸 Перейти на страницу оплаты", url=payment_url)],
            [InlineKeyboardButton("🔎 Проверить оплаты", callback_data='pay_check')],
            [InlineKeyboardButton("🆔 Профиль", callback_data='profile')]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        f'Ваша личная ссылка на оплату сгенерирована! Реквизиты платежа для проверки - "Счет от {pay_list[1]} на сумму {pay_list[2]} ₽"',
        reply_markup=reply_markup
        )


def pay_check(query, update):
    profile_list = registration_check(update.effective_user)
    conn = sqlite3.connect('astro_db.db')
    c = conn.cursor()
    c.execute(
        'SELECT payment_code, value, href FROM payments WHERE user_id=? AND payment_status="0";',
        (profile_list[3],)
    )
    rows = c.fetchall()
    if rows:
        payment_list = []
        for row in rows:
            payment_list.append(row)
        keyboard = [
                    [InlineKeyboardButton("🆔 Профиль", callback_data='profile')],
                    [InlineKeyboardButton("↩️ Назад в меню", callback_data='menu')],
                    ]
        for payment_item in payment_list:
            pay_list = payment_item[0].split('||')
            keyboard.insert(0, [InlineKeyboardButton(f'Счет от {pay_list[1]} на сумму {pay_list[2]} ₽', callback_data=payment_item[0])])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            f'Выберите нужную транзакцию:',
            reply_markup=reply_markup
            )
    else:
        keyboard = [
                    [InlineKeyboardButton("🆔 Профиль", callback_data='profile')],
                    [InlineKeyboardButton("↩️ Назад в меню", callback_data='menu')],
                    ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            f'У Вас нет текущих транзакций',
            reply_markup=reply_markup
            )


def pay_check_target(query, update, label, value, payment_url):
    profile_list = registration_check(update.effective_user)
    pay_list = label.split('||')
    conn = sqlite3.connect('astro_db.db')
    c = conn.cursor()
    UMONEY_TOKEN = os.getenv("UMONEY_TOKEN")
    client = Client(UMONEY_TOKEN)
    history = client.operation_history(label=label)
    if history.operations:
        if history.operations[0].status == 'success':
            c.execute('UPDATE payments SET payment_status="1" WHERE payment_code=?;', (label,))
            c.execute(
                'SELECT balance FROM users WHERE user_id=?;',
                (profile_list[3],)
            )
            old_value = c.fetchone()
            old_value = old_value[0]
            value = convert_to_int(value) + convert_to_int(old_value)
            c.execute('UPDATE users SET balance=? WHERE user_id=?;', (value, profile_list[3],))
            c.close()
            conn.commit()
            keyboard = [
                    [InlineKeyboardButton("🆔 Профиль", callback_data='profile')],
                    [InlineKeyboardButton("↩️ Назад в меню", callback_data='menu')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                f'✅ Ваша оплата прошла успешно! (Счет от {pay_list[1]} на сумму {pay_list[2]} ₽)',
                reply_markup=reply_markup
                )
        else:
            keyboard = [
            [InlineKeyboardButton("🆔 Профиль", callback_data='profile')],
            [InlineKeyboardButton("↩️ Назад в меню", callback_data='menu')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                f'Ошибка при оплате (Счет от {pay_list[1]} на сумму {pay_list[2]} ₽)',
                reply_markup=reply_markup
                )
    else:
        keyboard = [
        [InlineKeyboardButton("💸 Перейти на страницу оплаты", url=payment_url)],
        [InlineKeyboardButton("❌ Удалить реквизиты для оплаты", callback_data=f'delete_payment-{label}')],
        [InlineKeyboardButton("🆔 Профиль", callback_data='profile')],
        [InlineKeyboardButton("↩️ Назад в меню", callback_data='menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            f'Ваша оплата еще не прошла (Счет от {pay_list[1]} на сумму {pay_list[2]} ₽)',
            reply_markup=reply_markup
            )
    conn.close()


def delete_payment(query, label):
    conn = sqlite3.connect('astro_db.db')
    c = conn.cursor()
    c.execute(
        'DELETE FROM payments WHERE payment_code=?;',
        (label,)
    )
    conn.commit()
    conn.close()
    keyboard = [
        [InlineKeyboardButton("🆔 Профиль", callback_data='profile')],
        [InlineKeyboardButton("↩️ Назад в меню", callback_data='menu')],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        'Данные по оплате удалены.',
        reply_markup=reply_markup
        )


def convert_to_int(value):
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            print(f"Невозможно преобразовать '{value}' в int.")
            return None
    return value


def script(update, context):
    update.message.reply_text("Привет! Пожалуйста, введите скрипт для применения к базе данных:")
    context.user_data['waiting_for_script'] = True


def apply_script(update, context):
    if 'waiting_for_script' in context.user_data and context.user_data['waiting_for_script']:
        profile_list = registration_check(update.effective_user)
        if profile_list[0] == 'admin':
            script = update.message.text
            if script == 'Обновление':
                update.message.reply_text(f"Загрузил новое обновление - изменено инфо, исправлены переменные контекста, тест подписки внутри ЛК для админа")
            else:
                conn = sqlite3.connect('astro_db.db')
                c = conn.cursor()
                c.execute(script)
                conn.commit()
                conn.close()
                update.message.reply_text(f"Скрипт применен к базе данных:\n{script}")
        else:
            update.message.reply_text("Скрипт не выполнен, Вы не админ.")
        del context.user_data['waiting_for_script']
    else:
        update.message.reply_text("Для общения с ботом используйте только кнопки меню.")


def send_messages(context, user_ids, text):
    bot = context.bot
    for user_id in user_ids:
        try:
            bot.send_message(chat_id=user_id, text=text)
        except Exception as e:
            logger.info(f"Ошибка при отправлении письма {user_id}: {str(e)}")


def error(update, context):
    logger.error(f'Ошибка! - {context.error}. Qerry для прочтения - {update}')
    print(f'Ошибка! - {context.error}. Qerry для прочтения - {update}')


async def post_init(updater):
    await updater.bot.set_my_commands([
        BotCommand("/start", "Вызов меню"),
    ])


def main():
    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(commands))
    dp.add_handler(CommandHandler("script", script))
    dp.add_handler(MessageHandler(
        Filters.text & ~Filters.command,
        apply_script
        )
    )
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()
    updater.loop.create_task(post_init(updater))


if __name__ == '__main__':
    logging.basicConfig(
        filename='bot.log',
        filemode='a',  # 'a' - новые сообщения будут добавляться в файл
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    file_handler = logging.FileHandler('bot.log', 'a', 'utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(file_handler)
    logger = logging.getLogger(__name__)
    user_ids = [605381950, 2038870658]
    main()
