import json
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
from connection import web_requests_get, web_requests_post, error_logger, progress_tracker

'''
Useful Edgar Links
https://www.sec.gov/os/accessing-edgar-data
https://www.sec.gov/edgar/sec-api-documentation
********** Companies ********** 
list of Companies and their CIK - https://www.sec.gov/Archives/edgar/cik-lookup-data.txt
list of Companies and their Tickers and their exchange - https://www.sec.gov/files/company_tickers_exchange.json

Individual company information
Companies fillings - https://data.sec.gov/submissions/CIK0000320193.json
https://query1.finance.yahoo.com/v7/finance/quote?symbols=BAC

stock price:
https://query1.finance.yahoo.com/v7/finance/spark?symbols=BAC&range=5d&interval=5m&indicators=close&includeTimestamps=false&includePrePost=false&corsDomain=finance.yahoo.com&.tsrc=finance
timestamp = time-18000
dt = datetime.datetime.fromtimestamp(timestamp)
print(dt.strftime("%A, %B %d, %Y %I:%M:%S %p"))

https://query1.finance.yahoo.com/v7/finance/spark?symbols=BAC&range=1d&interval=1m&indicators=close&includeTimestamps=true&includePrePost=false&corsDomain=finance.yahoo.com&.tsrc=finance


Fillings
Daily changes - https://www.sec.gov/Archives/edgar/daily-index/

'''
# ToDo: aggregate list of top companies
# Most popular (new/twitter), most vol, large price movements,largest by market cap

# ToDo: select a company based on ticker and Generate a profile for that company
# ToDo: Identifiable info (website, description, basic finances, stock price, fiscal year calendar (identify up coming events?))
# ToDo: Aggregate financial statements/filings
# ToDo: previous earnings call transcripts
# ToDo: Aggregate news finviz?

# ToDo: Generate a sentiment score for that company


def stock_price(ticker: str):
    """
    This function is to aggregate the news for the ticker provided
    """
    url = f'https://query1.finance.yahoo.com/v7/finance/spark?symbols={ticker}&range=5d&interval=1m&indicators=close&includeTimestamps=false&includePrePost=false&corsDomain=finance.yahoo.com&.tsrc=finance'
    header = {'User-Agent': json.load(open('vars.json'))['User-Agent']}
    quotes = {}
    page = web_requests_get(url, header)
    if page:
        data = page.json()
        quotes = data["spark"]["result"][0]["response"][0]['indicators']["quote"][0]["close"]
        times = data["spark"]["result"][0]["response"][0]['timestamp']
        price_date = {datetime.fromtimestamp(item[0]).strftime(
            '%b-%d-%y %H:%M'): item[1] for item in zip(times, quotes)}
        if file_check(ticker, "stock_quotes"):
            current_data = json_reader(f'{ticker}.json', "stock_quotes")
            # combine two dicts
            new_price_date = current_data.update(price_date)
            price_date = new_price_date
        json_writer(f'{ticker}.json', "stock_quotes", price_date)


def get_company_list():
    """
    This function uses yhoo finance to aggregate the top 300 most popular stocks for that day, based on vol.
    The list will be continually updated and be inclusive of any changes that happen, meaning tickers will not 
    be removed but only added to the company_list.txt with no duplicates.

    """
    popular_tickers = []
    my_file = open("company_list.txt", "r")
    company_list_data = my_file.read()
    popular_tickers = company_list_data.split("\n")
    for index in range(3):
        time.sleep(.5)
        vars = json.load(open('vars.json'))
        vars['yhoo_finance_query_payload']["offset"] = index*100
        url = 'https://query2.finance.yahoo.com/v1/finance/screener?crumb=HNeyfaCEzMS&lang=en-US&region=US&formatted=true&corsDomain=finance.yahoo.com'
        r = web_requests_post(
            url, {'User-Agent': vars['User-Agent'], 'Cookie': vars['cookie']}, vars['yhoo_finance_query_payload'])
        if r:
            data = json.loads(r.content.decode('utf-8')
                              )['finance']['result'][0]['quotes']
            for ii in data:
                if ii['symbol'] not in popular_tickers:
                    popular_tickers.append(ii['symbol'])
            # perform removal
            while ("" in popular_tickers):
                popular_tickers.remove("")
            with open('company_list.txt', 'w') as f:
                for line in popular_tickers:
                    f.write(f"{line}\n")
    return popular_tickers


def get_price_data():
    my_file = open("company_list.txt", "r")
    company_list_data = my_file.read()
    tickers = company_list_data.split("\n")
    for index, ii in enumerate(tickers):
        try:
            stock_price(ii)
        except Exception as e:
            error_logger(e)
        progress_tracker(index, len(tickers))
        time.sleep(round(random.uniform(4, 5), 1))


def get_nasdq():
    x = manage_requests("https://en.wikipedia.org/wiki/Nasdaq-100")
    soup = BeautifulSoup(x.content, "html.parser")
    table = soup.find('table', id="constituents")
    table_rows = table.find_all('tr')
    ll = []
    for raw_data in table_rows[1:]:
        row = [item.text.strip() for item in raw_data.find_all('td')]
        if len(row) != 4:
            print(f"Row failed:{row}")
        else:
            ll.append(row)
    companies = pd.DataFrame(
        ll, columns=[item.text.strip() for item in table_rows[0].find_all('th')])
    return companies.Ticker.to_list()


def get_sp500():
    x = manage_requests(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    soup = BeautifulSoup(x.content, "html.parser")
    table = soup.find('table', id="constituents")
    table_rows = table.find_all('tr')
    ll = []
    for raw_data in table_rows[1:]:
        row = [item.text.strip() for item in raw_data.find_all('td')]
        if len(row) != 9:
            while len(row) < 9:
                row.append('')
            ll.append(row)
        else:
            ll.append(row)
    companies = pd.DataFrame(
        ll, columns=[item.text.strip() for item in table_rows[0].find_all('th')])
    return companies.Symbol.to_list()


if __name__ == "__main__":
    get_price_data()
