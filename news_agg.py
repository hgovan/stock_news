# https://github.com/mariostoev/finviz
import json
import random
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from connection import error_logger, progress_tracker, read_json, web_requests_get, write_json


def main():
    pass
    # https://finviz.com/api/statement.ashx?t=BAC&s=IA
    # https://quantisnow.com/ticker/BAC
    # https://www.stocktitan.net/news/AAPL/


def stock_titan_news():
    url = "https://www.stocktitan.net/news/AAPL/"
    # To view how many articles per page there are<div class="news">
    # Individual article <article data-id="451591" data-ts="1670349600">
    # Tags: <div class="tags">
    # Title:<div class="title">
    # url: <div class="title"><a href="https://www.stocktitan.net/news/AAPL/apple-announces-biggest-upgrade-to-app-store-pricing-adding-700-new-9tq263bqx0x6.html">
    # AI_vote:<div class="rhea-vote is-5"><div class="title"><span>RHEA-AI</span></div><div class="indicator"><i class="icon-rhea-ai-very-positive"></i></div><div class="text">very positive</div>
    # Date: <div class="date">12/06/22 1:00 PM</div>
    # To view how many pages there are <div class="pagination">
    # URL -> Article content: <article>
    # URL -> Article content: <span id="mmgallerylink-link"><a rel="nofollow noopener" href="https://www.businesswire.com/news/home/20221027006041/en/">


def newsfilter():
    url = "https://api.newsfilter.io/public/actions"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
               "content-type": "application/json"}
    payload = {
        "type": "filterArticles",
        "isPublic": True,
        "queryString": "symbols:BAC AND (source.id:prNewswire)",
        "from": 0,
        "size": 50
    }
    r = requests.post(url, headers=headers, json=payload)
    return r


def finviz_news_getter(ticker: str) -> dict:
    """
    This function is to aggreagte the news for the ticker provided

    Agrs:
    ticker: str -> the ticker
    Return:
    dict -> The {date_time,description,link} for articles for that stock 

    """
    url = f'https://finviz.com/quote.ashx?t={ticker}'
    header = {
        'User-Agent': json.load(open('data/working/user_data.json'))['User-Agent']}
    news_tables = {}
    page = web_requests_get(url, header)
    if page:
        soup = BeautifulSoup(page.content, "html.parser")
        news_table = soup.find('table', id="news-table")
        articles = news_table.find_all('tr')
        library = read_json("data/working/history.json")
        date = ''
        for article in articles:
            template = {'date_time': '', 'description': '',
                        'ticker': [], "processed": False}
            content = article.text
            if "Loading…" not in content:
                time_text_index = content.find(":")
                if time_text_index > 8:
                    date = content[:time_text_index-3]
                if article.find('a')['href'] in library and ticker not in library[article.find('a')['href']]['ticker']:
                    library[article.find('a')['href']]['ticker'].append(ticker)
                else:
                    template['date_time'] = finviz_time_formater(
                        date, content[time_text_index-2:time_text_index+5])
                    template['description'] = content[time_text_index+5:]
                    template['ticker'].append(ticker)
                    library[article.find('a')['href']] = template
        write_json(f'data/working/history.json', library)
        return news_tables


def finviz_time_formater(date: str, time: str):
    """
    combinds date and time strings into one datetime object
    """
    in_time = datetime.strptime(time, "%I:%M%p")
    out_time = datetime.strftime(in_time, "%H:%M")
    datetime_str = f'{date} {out_time}'
    return datetime.strptime(datetime_str, '%b-%d-%y %H:%M').strftime('%b-%d-%y %H:%M')


if __name__ == "__main__":
    my_file = open("data/working/company_list.txt", "r")
    company_list_data = my_file.read()
    tickers = company_list_data.split("\n")
    for index, ii in enumerate(tickers):
        try:
            finviz_news_getter(ii)
        except Exception as e:
            error_logger(e)
        progress_tracker(index, len(tickers))
        time.sleep(round(random.uniform(1, 2), 1))
