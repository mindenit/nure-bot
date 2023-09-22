from pprint import pprint
import random
import telebot
import sqlite3
from pytz import timezone
import datetime
import nure_tools
from Database import *
KYIV = timezone('Europe/Kyiv')
# Read the bot's token from the file "Token"
with open("Token", "r") as f:
    bot_token = f.read()
# Create a bot object with the bot token
bot = telebot.TeleBot(bot_token)

# Define a global variable to store the bot status
bot_status = False

@bot.message_handler(commands=['choose'])
def register(message):
  x = message.text.split()
  if (len(x) == 2):
    Cist_name = x[1]
    Chat_id = message.chat.id
    Chat_type = message.chat.type
    if (Chat_type == 'private'):
      First_name = message.from_user.first_name
      Last_name = message.from_user.last_name
      Username = message.chat.username
    else:
      First_name = message.chat.title
      Last_name = None
      Username = message.chat.username
      init()
    if (check_chat_id_exists(message.chat.id)):
      update(Cist_name, int(random.uniform(1, 100000)), Chat_type, First_name, Last_name, Username, Chat_id)
    else:
      insert(Chat_id, Cist_name, int(random.uniform(1, 100000)), Chat_type, First_name, Last_name, Username)
    bot.reply_to(message,f"Thank you {message.from_user.first_name} for registration")
  else:
    bot.reply_to(message, f"Sorry, not valid input. Please, try again")

@bot.message_handler(commands=['start'])
def start(message):
  # Set the bot status to True
  global bot_status
  bot_status = True

  # Send a welcome message to the user
  bot.reply_to(message, f"Hello, {message.from_user.first_name}. I am a Telegram bot that can tell you the current date, week. Type /day, /week to get started.")

# Define a function to handle the /end command
@bot.message_handler(commands=['end'])
def end(message):
  # Set the bot status to False
  global bot_status
  bot_status = False

  # Send a goodbye message to the user
  bot.reply_to(message, f"Goodbye, {message.from_user.first_name}. I hope you enjoyed using my bot. See you soon.")

# Define a function to handle the /day command
@bot.message_handler(commands=['day'])
def day(message):
  # Check if the bot status is True
  global bot_status
  if bot_status:
    # Get the current date in Kyiv time
    today = KYIV.localize(datetime.datetime.now())
    # Get the Unix timestamp of the day in Kyiv time
    groups = nure_tools.get_groups()
    today_timestamp = KYIV.localize(datetime.datetime(today.year, today.month, today.day)).timestamp()
    # Send the date and Unix timestamp as a reply to the user
    bot.reply_to(message, f"Today is {today.strftime('%Y-%m-%d')} (Unix timestamp: {today_timestamp}")

# Define a function to handle the /week command
@bot.message_handler(commands=['week'])
def week(message):
  # Check if the bot status is True
  global bot_status
  if bot_status:
    # Get the Monday of this week in Kyiv time
    current_day = KYIV.localize(datetime.datetime.now())
    monday = current_day - datetime.timedelta(days=current_day.weekday())
    # Get the week number
    week_num = monday.isocalendar()[1]

    # Create a string to store the week number and day names, dates, and Unix timestamps in Kyiv time
    week_str = f"Week {week_num}:\n"
    for i in range(7):
      # Get the day name and date in Kyiv time
      day_name = monday + datetime.timedelta(days=i)
      day_name = KYIV.localize(datetime.datetime(day_name.year, day_name.month, day_name.day))
      # Get the start and end timestamps of the day in Kyiv time
      start_timestamp = day_name.timestamp()
      end_timestamp = start_timestamp + 86399

      # Add the day name, date, and Unix timestamps to the week string
      day_str = f"{day_name.strftime('%A')}: {day_name.strftime('%Y-%m-%d')} (Start time: {start_timestamp}, End time: {end_timestamp})\n"
      week_str += day_str

    # Send the week string as a reply to the user
    bot.reply_to(message, week_str)

# Start the bot
bot.polling()

