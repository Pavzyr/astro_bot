import sqlite3

conn = sqlite3.connect('astro_db.db')
c = conn.cursor()

# Создание таблицы
# c.execute('''CREATE TABLE users
#              (id INTEGER PRIMARY KEY AUTOINCREMENT, 
#               user_id INTEGER UNIQUE, 
#               username TEXT, 
#               first_name TEXT, 
#               last_name TEXT, 
#               role TEXT, 
#               balance TEXT, 
#               expired TEXT)''')
# c.execute('''CREATE TABLE info
#              (id INTEGER PRIMARY KEY AUTOINCREMENT, 
#               page_name TEXT, 
#               page_text TEXT)''')
c.execute('''CREATE TABLE payments
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              user_id TEXT, 
              payment_code TEXT,
              payment_status TEXT,
              value TEXT,
              href TEXT)''')
conn.commit()
conn.close()