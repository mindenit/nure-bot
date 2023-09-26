from pprint import pprint
import telebot
import sqlite3
from pytz import timezone
import datetime
import nure_tools
import Database
from collections import OrderedDict
import locale

locale.setlocale(locale.LC_ALL, 'uk_UA.UTF-8')

KYIV = timezone('Europe/Kyiv')
DonateHTML = "\n" + "<a href=\"https://t.me/nure_dev\">Канал з інфою</a> | " + "<a href=\"https://send.monobank.ua/jar/5tHDuV8dfg\">Підтримати розробку</a> | " + "<a href=\"https://t.me/ketronix_dev\">Адмін</a> | " + "<a href=\"https://github.com/nure-dev/nure-cist-bot\">Код</a>" + "\n"
# Read the bot's token from the file "Token"
with open("Token", "r") as f:
    bot_token = f.read()
# Create a bot object with the bot token
bot = telebot.TeleBot(bot_token)

Database.init()
def greet_user(messages):
    for message in messages:
        if (message.new_chat_members != None):
            for new_member in message.new_chat_members:
                if (new_member.id == bot.get_me().id):
                    parse_mode = 'html'
                    bot.reply_to(message.chat.id, f"Цей бот має низку команд, за допомогою яких ви можете отримати розклад для себе, " +
                                            "і своєї групи. Нижче буде список цих команд, із коротким описом, і прикладом. \n \n" +
                                            "Список команд бота: \n \n" +
                                            "\t <code>/choose group</code> - зміна групи у чаті, замість group треба написати назву вашої групи. " +
                                            "Наприклад: <code>/choose КІУКІ-22-7</code>, <code>/choose кіукі-22-7</code> і тд.\nУвага! Назву групи бот розуміє лише " +
                                            "якщо та була введена українською, через те шо він звіряє назву із реєстром на сайті cist.nure.ua." +
                                            " Якщо у вас виникла помилка зміни групи, перевірте щоб назва була українською мовою, " +
                                            "і відповідала тій що на cist.nure.ua. \n" +
                                            "\t <code>/help</code> - вам відправиться це повідомлення. \n" +
                                            "\t <code>/info</code> - вам відправиться інформація про цей чат із бази даних, якщо запис існує. \n" +
                                            "\t <code>/day</code> -  вам відправиться розклад для вашої групи на поточний день. \n" +
                                            "\t <code>/week</code> - вам відправиться розклад для вашої групи на поточний тиждень. " +
                                            "У неділю ця команда вам відправить розклад вже на наступний тиждень. \n" +
                                            "\t <code>/next_day</code> - відправляє розклад на наступний день. \n" +
                                            "\t <code>/next_week</code> - відправить розклад на наступний тиждень. \n \n", parse_mode=parse_mode, disable_web_page_preview=True)
bot.set_update_listener(greet_user)

@bot.message_handler(commands=['help'])
def help(message):
    parse_mode = 'html'
    bot.send_message(message.chat.id,
                     f"Список команд бота: \n \n" +
                     "\t <code>/choose group</code> - зміна групи у чаті, замість group треба написати назву вашої групи. " +
                     "Наприклад: <code>/choose КІУКІ-22-7</code>, <code>/choose кіукі-22-7</code> і тд. Увага! Назву групи бот розуміє лише " +
                     "якщо та була введена українською, через те шо він звіряє назву із реєстром на сайті cist.nure.ua." +
                     " Якщо у вас виникла помилка зміни групи, перевірте щоб назва була українською мовою, " +
                     "і відповідала тій що на cist.nure.ua. \n" +
                     "\t <code>/help</code> - вам відправиться це повідомлення. \n" +
                     "\t <code>/info</code> - вам відправиться інформація про цей чат із бази даних, якщо запис існує. \n" +
                     "\t <code>/day</code> -  вам відправиться розклад для вашої групи на поточний день. \n" +
                     "\t <code>/week</code> - вам відправиться розклад для вашої групи на поточний тиждень. " +
                     "У неділю ця команда вам відправить розклад вже на наступний тиждень. \n" +
                     "\t <code>/next_day</code> - відправляє розклад на наступний день. \n" +
                     "\t <code>/next_week</code> - відправить розклад на наступний тиждень. \n \n", parse_mode=parse_mode,
                     disable_web_page_preview=True)

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
        if (Database.check_chat_id_exists(message.chat.id)):
            Database.update(Cist_name, Cist_id, Chat_type, First_name, Last_name, Username, Chat_id)
        else:
            Database.insert(Chat_id, Cist_name, Cist_id, Chat_type, First_name, Last_name, Username)
        bot.reply_to(message, f"Дякую {message.from_user.first_name} за реєстрацію")
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
    Cist_id = Database.search(message.chat.id)
    # Get the Unix timestamp of the day in Kyiv time
    Schedule = nure_tools.get_schedule('group',
                                       Cist_id,
                                       today_str,
                                       end_str
                                       )
    Schedule = list(OrderedDict(((schedule['number_pair'],
                                  schedule['teachers'][0]['id'] if schedule['teachers'] else 'no_teacher'),
                                 schedule) for schedule in Schedule).values())
    Schedule.sort(key=lambda lesson: lesson['start_time'])
    today_text = ''
    for event in Schedule:
        # pprint(event)
        Start_time = datetime.datetime.fromtimestamp(int(event["start_time"])).astimezone(KYIV)
        End_time = datetime.datetime.fromtimestamp(int(event["end_time"])).astimezone(KYIV)
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
    bot.reply_to(message, f"Розклад на {today.strftime('%d.%m.%Y')}\n{today_text} {DonateHTML} ", parse_mode=parse_mode,
                 disable_web_page_preview=True)


@bot.message_handler(commands=['next_day'])
def next_day(message):
    # Check if the bot status is True
    # Get the current date in Kyiv time
    today = datetime.datetime.now().astimezone(KYIV)
    tommorow = datetime.datetime(today.year, today.month, today.day) + datetime.timedelta(days=1)
    tommorow_str = tommorow.strftime("%Y-%m-%d %H:%m")
    end_str = (tommorow + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%m")
    Cist_id = Database.search(message.chat.id)
    # Get the Unix timestamp of the day in Kyiv time
    Schedule = nure_tools.get_schedule('group',
                                       Cist_id,
                                       tommorow_str,
                                       end_str
                                       )
    Schedule = list(OrderedDict(((schedule['number_pair'],
                                  schedule['teachers'][0]['id'] if schedule['teachers'] else 'no_teacher'),
                                 schedule) for schedule in Schedule).values())
    Schedule.sort(key=lambda lesson: lesson['start_time'])
    tommorow_text = ''
    for event in Schedule:
        pprint(event)
        Start_time = datetime.datetime.fromtimestamp(int(event["start_time"])).astimezone(KYIV)
        End_time = datetime.datetime.fromtimestamp(int(event["end_time"])).astimezone(KYIV)
        Brief = event["subject"]["brief"]
        Type = event["type"]
        if (len(event["teachers"]) < 1):
            Short_name = "Не визначено"
        else:
            Short_name = event["teachers"][0]["short_name"]
        tommorow_text += f"{Start_time.strftime('%H:%M')} - {End_time.strftime('%H:%M')} | <b>{Brief} - {Type}</b> | {Short_name}\n"
    # Send the date and Unix timestamp as a reply to the user
    parse_mode = 'html'
    if (tommorow_text == ''):
        today_text = 'Пар нема. Відпочивайте!\n'
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
    Cist_id = Database.search(message.chat.id)
    # Create a string to store the week number and day names, dates, and Unix timestamps in Kyiv time
    week_str = f"Розклад {monday.strftime('%d.%m')} - {(monday + datetime.timedelta(days=6)).strftime('%d.%m')} ({week_num}) :\n\n"
    for i in range(6):
        # Get the day name and date in Kyiv time
        day_name = monday + datetime.timedelta(days=i)
        day_name = KYIV.localize(datetime.datetime(day_name.year, day_name.month, day_name.day))
        # Add the name of the day in Ukrainian using %A format code
        day_name_uk = day_name.strftime("%A")
        # Capitalize the name of the day using capitalize method
        day_name_uk = day_name_uk.capitalize()
        # Format the date as DD.MM.YYYY using %d, %m, and %Y format codes
        date_format = day_name.strftime("%d.%m.%Y")
        # Add the day name, date, and Unix timestamps to the week string
        day_str = day_name.strftime("%Y-%m-%d %H:%m")
        end_str = (day_name + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%m")
        Schedule = nure_tools.get_schedule('group',
                                           Cist_id,
                                           day_str,
                                           end_str
                                           )
        Schedule = list(OrderedDict(((schedule['number_pair'],
                                      schedule['teachers'][0]['id'] if schedule['teachers'] else 'no_teacher'),
                                      schedule) for schedule in Schedule).values())
        Schedule.sort(key=lambda lesson: lesson['start_time'])
        # Add the date and the name of the day in Ukrainian with a capital letter and the first format
        day_text = f'{date_format} ({day_name_uk})\n'
        for event in Schedule:
            pprint(event)
            Start_time = datetime.datetime.fromtimestamp(int(event["start_time"])).astimezone(KYIV)
            End_time = datetime.datetime.fromtimestamp(int(event["end_time"])).astimezone(KYIV)
            Brief = event["subject"]["brief"]
            Type = event["type"]
            if (len(event["teachers"]) < 1):
                Short_name = "Не визначено"
            else:
                Short_name = event["teachers"][0]["short_name"]
            day_text += f"{Start_time.strftime('%H:%M')} - {End_time.strftime('%H:%M')} | <b>{Brief} - {Type}</b> | {Short_name}\n"
        if (day_text == f'{date_format} ({day_name_uk})\n'):
            day_text = day_text + 'Пар нема. Відпочивайте!\n'
        day_text += "\n"
        week_str = week_str + day_text
    week_str = week_str + DonateHTML
    parse_mode = 'html'
    # Send the week string as a reply to the user
    bot.reply_to(message, week_str, parse_mode=parse_mode, disable_web_page_preview=True)

@bot.message_handler(commands=['next_week'])
def Next_week(message):
    # Check if the bot status is True
    # Get the Monday of next week in Kyiv time
    next_monday = KYIV.localize(datetime.datetime.now()) + datetime.timedelta(days=7)
    # Get the week number
    week_num = next_monday.isocalendar()[1]
    Cist_id = Database.search(message.chat.id)
    # Create a string to store the week number and day names, dates, and Unix timestamps in Kyiv time
    week_str = f"Розклад {next_monday.strftime('%d.%m')} - {(next_monday + datetime.timedelta(days=6)).strftime('%d.%m')} ({week_num}) :\n\n"
    for i in range(6):
        # Get the day name and date in Kyiv time
        day_name = next_monday + datetime.timedelta(days=i)
        day_name = KYIV.localize(datetime.datetime(day_name.year, day_name.month, day_name.day))
        # Add the name of the day in Ukrainian using %A format code
        day_name_uk = day_name.strftime("%A")
        # Capitalize the name of the day using capitalize method
        day_name_uk = day_name_uk.capitalize()
        # Format the date as DD.MM.YYYY using %d, %m, and %Y format codes
        date_format = day_name.strftime("%d.%m.%Y")
        # Add the day name, date, and Unix timestamps to the week string
        day_str = day_name.strftime("%Y-%m-%d %H:%m")
        end_str = (day_name + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%m")
        Schedule = nure_tools.get_schedule('group',
                                           Cist_id,
                                           day_str,
                                           end_str
                                           )
        Schedule = list(OrderedDict(((schedule['number_pair'],
                                      schedule['teachers'][0]['id'] if schedule['teachers'] else 'no_teacher'),
                                     schedule) for schedule in Schedule).values())
        Schedule.sort(key=lambda lesson: lesson['start_time'])
        # Add the date and the name of the day in Ukrainian with a capital letter and the first format
        day_text = f'{date_format} ({day_name_uk})\n'
        for event in Schedule:
            pprint(event)
            Start_time = datetime.datetime.fromtimestamp(int(event["start_time"])).astimezone(KYIV)
            End_time = datetime.datetime.fromtimestamp(int(event["end_time"])).astimezone(KYIV)
            Brief = event["subject"]["brief"]
            Type = event["type"]
            if (len(event["teachers"]) < 1):
                Short_name = "Не визначено"
            else:
                Short_name = event["teachers"][0]["short_name"]
            day_text += f"{Start_time.strftime('%H:%M')} - {End_time.strftime('%H:%M')} | <b>{Brief} - {Type}</b> | {Short_name}\n"
        if (day_text == f'{date_format} ({day_name_uk})\n'):
            day_text = day_text + 'Пар нема. Відпочивайте!\n'
        day_text += "\n"
        week_str = week_str + day_text
    week_str = week_str + DonateHTML
    parse_mode = 'html'
    # Send the week string as a reply to the user
    bot.reply_to(message, week_str, parse_mode=parse_mode, disable_web_page_preview=True)
# Start the bot
bot.polling()
