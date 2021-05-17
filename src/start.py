import telebot
import os
from dotenv import load_dotenv
from .functions import get_top

load_dotenv()

TOKEN = os.getenv('TOKEN')

bot = telebot.TeleBot(TOKEN)


# nltk.download('averaged_perceptron_tagger')
# nltk.download('punkt')


@bot.message_handler(commands=['start'])
def start_cmd(message):
    text = "Добро пожаловать!\n" \
           "Для получения информации укажите ссылку."

    bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=['text'])
def get_link(message):
    link = message.text
    if "what_are_your_moves_tomorrow" in link:
         text = get_top(link)
    else:
        text = "неподходящая ссылка"
    bot.send_message(message.chat.id, text)


bot.polling()
