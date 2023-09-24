from pprint import pprint
import random
import telebot
import sqlite3
from pytz import timezone
import datetime
import nure_tools
from Database import *

KYIV = timezone('Europe/Kyiv')
DonateHTML = "\n" + "<a href=\"https://t.me/nure_dev\">Канал з інфою</a> | " + "<a href=\"https://send.monobank.ua/jar/5tHDuV8dfg\">Підтримати розробку</a> | " + "<a href=\"https://t.me/ketronix_dev\">Адмін</a> | " + "<a href=\"https://github.com/nure-dev/nure-cist-bot\">Код</a>" + "\n"
# Read the bot's token from the file "Token"
with open("Token", "r") as f:
    bot_token = f.read()
# Create a bot object with the bot token
bot = telebot.TeleBot(bot_token)

init()


@bot.message_handler(commands=['choose'])
def register(message):
    x = message.text.split()
    if (len(x) == 2):
        Cist_name = x[1]
        Cist_id = nure_tools.find_group(Cist_name)["id"]
        Chat_id = message.chat.id
        Chat_type = message.chat.type
        if (Chat_type == 'private'):
            First_name = message.chat.first_name
            Last_name = message.chat.last_name
            Username = message.chat.username
        else:
            First_name = message.chat.title
            Last_name = None
            Username = message.chat.username
        if (check_chat_id_exists(message.chat.id)):
            update(Cist_name, Cist_id, Chat_type, First_name, Last_name, Username, Chat_id)
        else:
            insert(Chat_id, Cist_name, Cist_id, Chat_type, First_name, Last_name, Username)
        bot.reply_to(message, f"Thank you {message.from_user.first_name} for registration")
    else:
        bot.reply_to(message, f"Sorry, not valid input. Please, try again")


# Define a function to handle the /day command
@bot.message_handler(commands=['day'])
def day(message):
    # Check if the bot status is True
    # Get the current date in Kyiv time
    today = datetime.datetime.now().astimezone(KYIV)
    today = datetime.datetime(today.year, today.month, today.day)
    today_str = today.strftime("%Y-%m-%d %H:%m")
    end_str = (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%m")
    Cist_id = search(message.chat.id)
    # Get the Unix timestamp of the day in Kyiv time
    Schedule = nure_tools.get_schedule('group',
                                       Cist_id,
                                       today_str,
                                       end_str
                                       )
    Schedule.sort(key=lambda lesson: lesson['start_time'])
    today_text = ''
    for event in Schedule:
        # pprint(event)
        Start_time = datetime.datetime.fromtimestamp(int(event["start_time"]))
        End_time = datetime.datetime.fromtimestamp(int(event["end_time"]))
        Brief = event["subject"]["brief"]
        Type = event["type"]
        if (len(event["teachers"]) < 1):
            Short_name = "Не визначено"
        else:
            Short_name = event["teachers"][0]["short_name"]
        today_text += f"{Start_time.strftime('%H:%M')} - {End_time.strftime('%H:%M')} | <b>{Brief} - {Type}</b> | {Short_name}\n"
    # Send the date and Unix timestamp as a reply to the user
    parse_mode = 'html'
    if (today_text == ''):
        today_text = 'Пар нема. Відпочивайте!\n'
    bot.reply_to(message, f"Розклад на {today.strftime('%Y-%m-%d')}\n{today_text} {DonateHTML} ", parse_mode=parse_mode,
                 disable_web_page_preview=True)


@bot.message_handler(commands=['next_day'])
def next_day(message):
    # Check if the bot status is True
    # Get the current date in Kyiv time
    today = datetime.datetime.now().astimezone(KYIV)
    tommorow = datetime.datetime(today.year, today.month, today.day) + datetime.timedelta(days=1)
    tommorow_str = tommorow.strftime("%Y-%m-%d %H:%m")
    end_str = (tommorow + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%m")
    Cist_id = search(message.chat.id)
    # Get the Unix timestamp of the day in Kyiv time
    Schedule = nure_tools.get_schedule('group',
                                       Cist_id,
                                       tommorow_str,
                                       end_str
                                       )
    Schedule.sort(key=lambda lesson: lesson['start_time'])
    tommorow_text = ''
    for event in Schedule:
        pprint(event)
        Start_time = datetime.datetime.fromtimestamp(int(event["start_time"]))
        End_time = datetime.datetime.fromtimestamp(int(event["end_time"]))
        Brief = event["subject"]["brief"]
        Type = event["type"]
        if (len(event["teachers"]) < 1):
            Short_name = "Не визначено"
        else:
            Short_name = event["teachers"][0]["short_name"]
        tommorow_text += f"{Start_time.strftime('%H:%M')} - {End_time.strftime('%H:%M')} | <b>{Brief} - {Type}</b> | {Short_name}\n"
    # Send the date and Unix timestamp as a reply to the user
    parse_mode = 'html'
    bot.reply_to(message, f"Розклад на {tommorow.strftime('%Y-%m-%d')}\n{tommorow_text} {DonateHTML} ",
                 parse_mode=parse_mode, disable_web_page_preview=True)


# Define a function to handle the /week command
@bot.message_handler(commands=['week'])
def week(message):
    # Check if the bot status is True
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
