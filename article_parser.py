import json
from connection import read_json, web_requests_get, write_json
from newspaper import Article
from bs4 import BeautifulSoup
import nltk

from sentiment_analysis import FinBert
nltk.download('punkt')


def yhoo_check(url):
    header = {
        'User-Agent': json.load(open('data/working/user_data.json'))['User-Agent']}
    page = web_requests_get(url, header)
    soup = BeautifulSoup(page.content, "html.parser")
    continue_reading_element = soup.find_all(
        'div', class_="caas-readmore caas-readmore-collapse")
    if continue_reading_element:
        a_tag = continue_reading_element[0].find('a')
        if a_tag:
            return a_tag['href']

    return url


def parse_article(url: str, tickers: list):
    parsed_article = {}
    new_url = url
    if "https://finance.yahoo.com" in url:
        new_url = yhoo_check(url)
    try:
        article = Article(new_url)
        article.download()
        article.parse()
        txt = article.text
        title = article.title
        parsed_article[new_url] = {"text": txt, "title": title}
        article.nlp()
        keywords = article.keywords
        summary = article.summary
        return {"title": title, "keywords": keywords, "summary": summary, "ticker": tickers}
    except Exception as e:
        print(e)
        return False


def update_visited(url: str, ticker: list):
    visited_articles = read_json("data/working/visited.json")
    if url in visited_articles.keys():
        if ticker not in visited_articles[url]:
            visited_articles[url].append(ticker)
    else:
        visited_articles[url] = ticker
    write_json("data/working/visited.json", visited_articles)


if __name__ == "__main__":
    visited_articles = read_json("data/working/visited.json")
    found_articles = read_json("data/working/history.json")
    model = FinBert()
    for key, value in found_articles.items():
        if not value['processed']:
            url = value['url']
            article_content = parse_article(url, value['tickers'])
            s_scores = model.findPercentageBySentence(value["summary"])
            article_content['s_scores'] = s_scores
            visited_articles[url] = article_content
            write_json("data/working/visited.json", visited_articles)

            found_articles[url]["processed"] = True
            write_json("data/working/history.json", found_articles)
            print(f"updated url{url}:\n\ts_score:{s_scores}\n")

    # url = "https://www.ft.com/content/a2670593-7e99-428e-886b-20af1d2187e2?ftcamp=traffic/partner/feed_headline/us_yahoo/auddev"
    # x = parse_article(url)
    # update_visited(url: str, ticker: list)
