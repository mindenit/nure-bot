import sqlite3
import telegram
from pprint import pprint


def check_chat_id_exists(chat_id):
    # Підключитися до бази даних SQLite
    conn = sqlite3.connect('my_database.db')  # Замініть 'your_database.db' на шлях до вашої бази даних
    cursor = conn.cursor()

    # Виконати запит до бази даних, щоб перевірити наявність записів за chat_id
    cursor.execute("SELECT COUNT(*) FROM users WHERE chat_id = ?", (chat_id, ))
    result = cursor.fetchone()[0]
    # conn.commit()
    conn.close()
    if result is not None:
        return True
    else:
        return False
def get_chat_ids():
    conn = sqlite3.connect('my_database.db')
    c = conn.cursor()
    c.execute('SELECT chat_id FROM users')
    chat_ids = []
    for row in c.fetchall():
        chat_ids.append(row[0])
    conn.close()
    return chat_ids
def check_cist_id(chat_id):
    # connect to the database
    conn = sqlite3.connect("my_database.db")
    # create a cursor object
    cur = conn.cursor()
    # execute a query to select the cist_id from the users table where chat_id matches
    cur.execute("SELECT cist_id FROM users WHERE chat_id = ?", (chat_id,))
    # fetch the result
    result = cur.fetchone()[0]
    # close the connection
    conn.close()
    # check if the result is not None and return True or False accordingly
    if result is not None:
        return True
    else:
        return False

def save_chat_id(message):
    # get the chat id from the message
    chat_id = message.chat.id
    conn = sqlite3.connect('my_database.db')
    c = conn.cursor()
    # check if the chat id already exists in the table
    c.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
    result = c.fetchone()
    if result is None:
        c.execute("INSERT INTO users (chat_id, chat_type, first_name, last_name, username) VALUES (?, ?, ?, ?, ?)",
                  (chat_id, message.chat.type, message.chat.first_name, message.chat.last_name,  message.chat.username))
        conn.commit()

def count_chats():
  """Counts the number of private and group chats in the sqlite3 database at the given path.

  Args:
    db_path: The path to the sqlite3 database.

  Returns:
    A tuple of two integers, where the first integer is the number of private chats and the second integer is the number of group chats.
  """

  # Connect to the database.
  conn = sqlite3.connect('my_database.db')
  c = conn.cursor()

  # Count the number of private chats.
  c.execute("SELECT COUNT(*) FROM users WHERE chat_type = 'private'")
  num_private_chats = c.fetchone()[0]

  # Count the number of group chats.
  c.execute("SELECT COUNT(*) FROM users WHERE chat_type = 'group'")
  num_group_chats = c.fetchone()[0]

  c.execute("SELECT COUNT(*) FROM users WHERE chat_type = 'supergroup'")
  num_group_chats += c.fetchone()[0]

  c.execute("SELECT COUNT(*) FROM users WHERE cist_id IS NULL")
  num_none_chats = c.fetchone()[0]

  # Close the database connection.
  c.close()
  conn.close()

  return num_private_chats, num_group_chats, num_none_chats
def update(Cist_name, Cist_id, Chat_type, First_name, Last_name, Username, Chat_id):
    conn = sqlite3.connect('my_database.db')  # Замініть 'your_database.db' на шлях до вашої бази даних
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE users SET cist_name = ?, cist_id = ?, chat_type = ?, first_name = ?, last_name = ?, username = ? WHERE chat_id = ?;''',
        (Cist_name, Cist_id, Chat_type,  First_name, Last_name, Username, Chat_id))
    conn.commit()
    conn.close()


def insert(Chat_id, Cist_name, Cist_id, Chat_type, First_name, Last_name, Username):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    # Check if the chat type is valid
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
         chat_id INTEGER,
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