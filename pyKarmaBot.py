import telebot
import os
from dotenv import load_dotenv
import psycopg2
import re
from telebot import types

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN, parse_mode=None)


@bot.message_handler(regexp=r'^@([\w\d]+)\s+\/giveKarma')
def give_karma(message):
    db = psycopg2.connect(
        database="karmaDB",
        user=os.getenv('dbUSER'),
        password=os.getenv('dbPASS'),
        host="127.0.0.1",
        port="5432"
    )
    cursor = db.cursor()
    cursor.execute('SELECT user_id FROM "KARMA"')
    users_list = [x[0] for x in cursor.fetchall()]
    user = message.from_user
    if user.id in users_list:
        bot.send_message(message.chat.id, 'Вы уже в круге кармы!')
    else:
        cursor.execute(f'''INSERT INTO "KARMA" VALUES({user.id}, LOWER('{user.username}'), 0)''')
        bot.send_message(message.chat.id, 'Вы добавлены в круг кармы, поднимайте свою карму помогая другим')
        cursor.close()
        db.commit()
        db.close()


@bot.message_handler(regexp=r'^@([\w\d]+)\s+\/addKarma\s+@([\w\d]+)$')
def add_karma(message):
    karma_owner = (re.findall(r'^@([\w\d]+)\s+\/addKarma\s+@([\w\d]+)$', message.text)[0])[1]
    db = psycopg2.connect(
        database="karmaDB",
        user=os.getenv('dbUSER'),
        password=os.getenv('dbPASS'),
        host="127.0.0.1",
        port="5432"
    )
    cursor = db.cursor()
    try:
        if message.from_user.username != karma_owner:
            cursor.execute(f'''
                            UPDATE "KARMA" SET karma_points = karma_points + 10 WHERE username = LOWER('{karma_owner}');
                            SELECT karma_points from "KARMA" WHERE username = LOWER('{karma_owner}')
                            ''')
            mes = cursor.fetchone()[0]
            bot.send_message(message.chat.id, f'@{karma_owner} получает +10 к карме. Общая карма {mes}')
            cursor.close()
            db.commit()
            db.close()
        else:
            bot.send_message(message.chat.id, 'накрутка своей кармы запрещена')
    except TypeError:
        bot.send_message(message.chat.id, 'чел не найден')


@bot.message_handler(commands=['eybratbergelchi'])
def buttons_return(message):
    db = psycopg2.connect(
        database="karmaDB",
        user=os.getenv('dbUSER'),
        password=os.getenv('dbPASS'),
        host="127.0.0.1",
        port="5432"
    )
    cursor = db.cursor()
    cursor.execute('SELECT user_id FROM "KARMA"')
    users_list = [x[0] for x in cursor.fetchall()]
    user = message.from_user.id
    buttons = types.InlineKeyboardMarkup()
    give_karma_button = types.InlineKeyboardButton('рег в карму', switch_inline_query_current_chat='/giveKarma')
    add_karma_button = types.InlineKeyboardButton('плюс карма', switch_inline_query_current_chat='/addKarma @')
    if user in users_list:
        buttons.add(add_karma_button)
    else:
        buttons.add(give_karma_button)
    bot.send_message(message.chat.id, "ЧО хотел?", reply_markup=buttons)


bot.infinity_polling()
