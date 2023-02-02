import time
from article_parser import parse_article
from connection import read_json, write_json
import nltk

from sentiment_analysis import FinBert
nltk.download('punkt')


def main():
    visited_articles = read_json("data/visited.json")
    found_articles = read_json("data/history.json")
    model = FinBert()
    print(f"Parsing articles...\n")
    for url, value in found_articles.items():
        if not value['processed']:
            article_content = parse_article(url, value['ticker'])
            if article_content:
                s_scores = model.findPercentageBySentence(
                    article_content["summary"])
                article_content['s_scores'] = s_scores
                visited_articles[url] = article_content
                write_json("data/working/visited.json", visited_articles)
                print(f"updated url: {url}:\ns_score:{s_scores}\n")
            else:
                print(f"failed to process: {url}:\n")

            found_articles[url]["processed"] = True
            write_json("data/working/history.json", found_articles)
            time.sleep(3)


if __name__ == "__main__":
    model = FinBert()
    print(model.findPercentageBySentence("This sucks"))
