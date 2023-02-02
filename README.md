# stock_news

This repo is designed to aggregate active ticker and leverage the website [finviz](www.finviz.com)to aggregate news associated with that company

## How do the modules interact with each-other

### connection.py
Multiple helper function to connect, track and log 

### Company.py
This is a collection of functions to get tickers to be used in the news aggregation.  We can collect the top 300 most popular stocks for a particular day, the S&P500 and the NASDQ.

### New_agg.py
Primarily used to get news article links from from finviz.  The links are placed into a dictionary where the tickers referencing that article are tracked

### article_parser.py
Used to parser the articles found in finviz.  They are primarily Yahoo Finance pieces which adds complexity as the articles are usually references to other articles.  There is a button which links to the other article or expands the current article.  I have created a check for that and use Newspaper3k to parse the actual article.  

### sentiment_analysis.py
Once the article is parsed and saved then the analysis can begin with "ProsusAI/finbert" to determine the sentiment of those articles.

I encounted difficulty when trying to install pytorch and found that I needed to depreciate my version of python to 3.7.  This link was very helpful in troubleshooting this [https://stackoverflow.com/questions/62898911/how-to-downgrade-python-version-from-3-8-to-3-7-mac]



