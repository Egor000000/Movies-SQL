import config 
import telebot 
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton 
 
from random import randint 
import sqlite3  
import matplotlib 
 
matplotlib.use('Agg') 
import matplotlib.pyplot as plt 
bot = telebot.TeleBot(config.API_TOKEN) 
 
def senf_info(bot, message, row): 
         
        info = f""" 
📍Title of movie:   {row[2]} 
📍Year:                   {row[3]} 
📍Genres:              {row[4]} 
📍Rating IMDB:      {row[5]} 
 
 
🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻 
{row[6]} 
""" 
        bot.send_photo(message.chat.id,row[1]) 
        bot.send_message(message.chat.id, info, reply_markup=add_to_favorite(row[0])) 
 
 
def add_to_favorite(id): 
        markup = InlineKeyboardMarkup() 
        markup.row_width = 1 
        markup.add(InlineKeyboardButton("Добавить фильм в избранное 🌟", callback_data=f'favorite_{id}')) 
        return markup 
 
 
def main_markup(): 
  markup = ReplyKeyboardMarkup() 
  markup.add(KeyboardButton('/random'))
  markup.add(KeyboardButton('/help'))
  return markup            
 
 
@bot.callback_query_handler(func=lambda call: True) 
def callback_query(call): 
    if call.data.startswith("favorite"): 
        id = call.data[call.data.find("_")+1:] 
 
 
@bot.message_handler(commands=['start']) 
def send_welcome(message): 
    bot.send_message(message.chat.id, """Привет! Добро пожаловать в лучший чат-бот для просмотра фильмов 🎥 !
Здесь вы можете найти 1000 фильмов 🔥 
Нажмите / random, чтобы получить случайный фильм
Или напишите название фильма, и я постараюсь его найти! 🎬""", reply_markup=main_markup()) 
 
@bot.message_handler(commands=['help']) 
def send_welcome(message): 
    bot.send_message(message.chat.id, """Чтобы посмотреть график количества выпусков фильмов, нужно ввести команду / Plt и две даты(года)""")

@bot.message_handler(commands=['random']) 
def random_movie(message): 
    con = sqlite3.connect("movie_database.db") 
    with con: 
        cur = con.cursor() 
        cur.execute(f"SELECT * FROM movies ORDER BY RANDOM() LIMIT 1") 
        row = cur.fetchall()[0] 
        cur.close() 
    senf_info(bot, message, row) 
 
     
 
 
@bot.message_handler(commands=['Plt']) 
def graphic_handler(message): 
    dates = message.text.split()[1:] 
    list_x, list_y = get_data(dates[0], dates[1]) 
    graf(list_x, list_y) 
    bot.send_photo(message.chat.id, open('plot.png', 'rb')) 
 
 
def graf(list_x, list_y): 
    plt.figure(figsize=(8, 6)) 
    plt.plot(list_x, list_y, marker='o', color='g', linestyle='--') 
    plt.grid(False) 
    plt.savefig('plot.png') 
 
 
def get_data(date_start, date_end): 
    con = sqlite3.connect("movie_database.db") 
    with con: 
        cur = con.cursor() 
        cur.execute('SELECT year, COUNT(*) FROM movies  WHERE year BETWEEN ? AND ? GROUP BY year', (date_start, date_end)) 
        res = cur.fetchall() 
        years = [x[0] for x in res] 
        counts = [x[1] for x in res] 
        return years,counts 
     
 
@bot.message_handler(func=lambda message: True) 
def echo_message(message): 
 
    con = sqlite3.connect("movie_database.db") 
    with con: 
        cur = con.cursor() 
        cur.execute(f"select * from movies where LOWER(title) = '{message.text.lower()}'") 
        row = cur.fetchall() 
        if row: 
            row = row[0] 
            bot.send_message(message.chat.id,"Of course! I know this movie😌") 
            senf_info(bot, message, row) 
        else: 
            bot.send_message(message.chat.id,"I don't know this movie ") 
 
        cur.close() 
 
 
bot.infinity_polling()
