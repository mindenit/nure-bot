import sqlite3

def check_chat_id_exists(chat_id):
    # Підключитися до бази даних SQLite
    conn = sqlite3.connect('my_database.db')  # Замініть 'your_database.db' на шлях до вашої бази даних
    cursor = conn.cursor()

    # Виконати запит до бази даних, щоб перевірити наявність записів за chat_id
    cursor.execute("SELECT COUNT(*) FROM users WHERE chat_id = ?", (chat_id,))
    count = cursor.fetchone()
    conn.commit()
    conn.close()
    return count;

def update(Cist_name, Cist_id, Chat_type, First_name, Last_name, Username, Chat_id):
    conn = sqlite3.connect('my_database.db')  # Замініть 'your_database.db' на шлях до вашої бази даних
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE users SET cist_name = ?, cist_id = ?, chat_type = ?, first_name = ?, last_name = ?, username = ? WHERE chat_id = ?;''',
        (Cist_name, Cist_id, Chat_type,  First_name, Last_name, Username, Chat_id))
    conn.commit()
    conn.close()


def insert(Chat_id, Cist_name, Cist_id, Chat_type, First_name, Last_name, Username):
    conn = sqlite3.connect('my_database.db')  # Замініть 'your_database.db' на шлях до вашої бази даних
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO users (chat_id, cist_name, cist_id, chat_type, first_name, last_name, username)
          VALUES (?, ?, ?, ?, ?, ?, ?);''',
              (Chat_id, Cist_name, Cist_id, Chat_type, First_name, Last_name, Username))
    # Commit the changes
    conn.commit()
    # Close the database connection
    conn.close()

def init():
    conn = sqlite3.connect('my_database.db')
    c = conn.cursor()
    # Create the table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS users (
         chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
         cist_name TEXT,
         cist_id INTEGER,
         chat_type TEXT,
         first_name TEXT,
         last_name TEXT,
         username TEXT
       );''')
    conn.commit()
    conn.close()


def search(Chat_id):
    conn = sqlite3.connect('my_database.db')
    c = conn.cursor()
    c.execute('''SELECT cist_id FROM users WHERE chat_id = ?;''', (Chat_id,))
    Cist_id = c.fetchone()[0]
    conn.commit()
    conn.close()
    return Cist_id