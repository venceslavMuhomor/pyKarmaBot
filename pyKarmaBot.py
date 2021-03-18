import telebot
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN, parse_mode=None)
chat = os.getenv('CHAT')


@bot.message_handler(commands=['giveKarma'])
def give_karma(message):
    db = psycopg2.connect(
        database="karmaDB",
        user=os.getenv('dbUSER'),
        password=os.getenv('dbPASS'),
        host="127.0.0.1",
        port="5432"
    )
    cursor = db.cursor()
    cursor.execute('SELECT user_id FROM karma')
    users_list = [x[0] for x in cursor.fetchall()]
    user = message.from_user
    if user.id in users_list:
        bot.send_message(chat, 'Вы уже в круге кармы!')
    else:
        cursor.execute(f'''INSERT INTO karma VALUES({user.id}, 0 )''')
        bot.send_message(chat, 'Вы добавлены в круг кармы, поднимайте свою карму помогая другим')
        cursor.close()
        db.commit()
        db.close()


bot.infinity_polling()
