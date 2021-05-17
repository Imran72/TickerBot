import praw
import requests
from bs4 import BeautifulSoup
import os
import nltk
from dotenv import load_dotenv
from nltk.tokenize import sent_tokenize, word_tokenize, RegexpTokenizer
import pandas as pd
import pymorphy2

from praw.models import MoreComments, Comment

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
USER_AGENT = os.getenv('USER_AGENT')

morph = pymorphy2.MorphAnalyzer()
tokenizer = RegexpTokenizer(r'\w+')


def get_comments(dataset):
    arr = []
    for comment in dataset:
        if isinstance(comment, MoreComments):
            continue
        else:
            arr.append(comment.body)
    return arr


# лемматизация входного слова
def lemmatize(word):
    p = morph.parse(word)[0]
    p = p.normal_form
    return p


# удаление стоп-слов
def get_without_stopwords(s):
    words = []
    for el in s:
        tokenized_words = tokenizer.tokenize(el)

        tags = nltk.pos_tag(tokenized_words)
        nouns = [word for word, pos in tags if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS')]
        for word in nouns:
            words.append(word)

    without_stop_words = [lemmatize(word) for word in words]
    return without_stop_words


# приведение к нижнему регистру
def to_lower(sen):
    return sen.lower()


# def get_link():
#     URL = 'https://www.reddit.com/r/wallstreetbets/?f=flair_name%3A%22Daily%20Discussion%22'
#     page = requests.get(URL)
#
#     soup = BeautifulSoup(page.content, 'html.parser')
#
#     results = soup.find_all('a', href=True)
#     results = [result['href'] for result in results if "what_are_your_moves_tomorrow" in result['href']]
#
#     return results


def get_data():
    dataset = pd.read_csv("data/tickers_nasdaq.csv")

    # оставляем только названия тикеров
    ticker_list = list(dataset.Symbol)

    for i in range(len(ticker_list)):
        ticker_list[i] = to_lower(ticker_list[i])

    ticker_dict = dict((el, 0) for el in ticker_list)

    return ticker_dict


def to_format(arr, link):
    data = link[85:85 + link[85:].find('/')]
    str = "Date: %s\n" % data
    index = 1
    for el in arr[::-1]:
        str += "%d. %s\n" % (index, el.upper())
        index += 1
    return str


def get_top(link):
    reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)
    submission = reddit.submission(url=link)

    comment_set = submission.comments.list()

    arr = get_comments(comment_set)
    brr = get_without_stopwords(arr)

    ticker_dict = get_data()

    for i in brr:
        if i in ticker_dict:
            ticker_dict[i] += 1

    sorted_keys = sorted(ticker_dict, key=ticker_dict.get)

    return to_format(sorted_keys[-10:], link)
