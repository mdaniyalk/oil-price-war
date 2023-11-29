import yfinance as yf
import openai
from tqdm import tqdm
from datetime import datetime
from newsapi import NewsApiClient



def convert_datetime_format(input_datetime_str):
    # Parse the input datetime string
    input_format = "%Y-%m-%dT%H:%M:%SZ"
    dt_object = datetime.strptime(input_datetime_str, input_format)

    # Convert to the desired format
    output_format = "%Y-%m-%d"
    output_datetime_str = dt_object.strftime(output_format)

    return output_datetime_str


def get_historical_price(period=None, interval=None, start=None, end=None):
    """
    Parameters:
        period : str
            Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            Either Use period parameter or use start and end
        interval : str
            Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            Intraday data cannot extend last 60 days
        start: str
            Download start date string (YYYY-MM-DD) or _datetime, inclusive.
            Default is 99 years ago
            E.g. for start="2020-01-01", the first data point will be on "2020-01-01"
        end: str
            Download end date string (YYYY-MM-DD) or _datetime, exclusive.
            Default is now
            E.g. for end="2023-01-01", the last data point will be on "2022-12-31"
    """
    crude = yf.Ticker("CL=F")
    data = crude.history(period=period, 
                         interval=interval, 
                         start=start, 
                         end=end)
    dates = data.index.astype(str).to_numpy()
    close_price = data['Close'].to_numpy()

    historical_data = []
    for i in range(len(dates)):
        _dates = dates[i]
        _price = close_price[i]
        _data = {'timestamp': _dates, 
                 'close_price': _price}
        historical_data.append(_data)
    return historical_data


def get_last_minutes_price():
    history = get_historical_price(period="1d", interval="1m")
    last_datetime = history[-1]['timestamp']
    last_price = history[-1]['close_price']
    last_minute_price = {'timestamp': last_datetime, 'close_price': last_price}
    return last_minute_price



def get_historical_news(query, sources, domains, start, end, language):
    """
    Parameters:
        query : str
            Keywords or a phrase to search for in the article title and body.  See the official News API
            `documentation <https://newsapi.org/docs/endpoints/everything>`_ for search syntax and examples.
        sources : str
            A comma-seperated string of identifiers for the news sources or blogs you want headlines from.
            Use :meth:`NewsApiClient.get_sources` to locate these programmatically, or look at the
            `sources index <https://newsapi.org/sources>`_.
        domains : str
            A comma-seperated string of domains (eg bbc.co.uk, techcrunch.com, engadget.com)
            to restrict the search to.
        start: str
            A date and optional time for the oldest article allowed.
            If a str, the format must conform to ISO-8601 specifically as one of either
            ``%Y-%m-%d`` (e.g. *2019-09-07*) or ``%Y-%m-%dT%H:%M:%S`` (e.g. *2019-09-07T13:04:15*).
            An int or float is assumed to represent a Unix timestamp.  All datetime inputs are assumed to be UTC.
        end: str
            A date and optional time for the newest article allowed.
            If a str, the format must conform to ISO-8601 specifically as one of either
            ``%Y-%m-%d`` (e.g. *2019-09-07*) or ``%Y-%m-%dT%H:%M:%S`` (e.g. *2019-09-07T13:04:15*).
            An int or float is assumed to represent a Unix timestamp.  All datetime inputs are assumed to be UTC.
        language: str
            The 2-letter ISO-639-1 code of the language you want to get headlines for.
            See :data:`newsapi.const.languages` for the set of allowed values.
    """
    api_key = '0e41d6f152534278bc39b3d29f063454'
    newsapi = NewsApiClient(api_key=api_key)
    result_title = []
    result_description = []
    result_date_published = []


    for i in range(100):
        try:
            all_articles = newsapi.get_everything(q=query,
                                                sources=sources,
                                                domains=domains,
                                                from_param=start,
                                                to=end,
                                                language=language,
                                                sort_by='relevancy',
                                                page=i+1)
        except:
            break 

        else:
            _title = [article['title'] for article in all_articles['articles']]
            _description = [article['description'] for article in all_articles['articles']]
            _date_published = [convert_datetime_format(str(article['publishedAt'])) for article in all_articles['articles']]
            result_title += _title
            result_description += _description
            result_date_published += _date_published
            print(len(all_articles))
    
    # sentiment = []

    # for i in tqdm(range(len(result_title))):
    #     title = result_title[i]
    #     description = result_description[i]
    #     combined_article = f"Title: {title}\nDescription: {description}"
    #     try:
    #         _sentiment = int(get_sentiment(combined_article))
    #     except:
    #         _sentiment = -1
    #     sentiment.append(_sentiment)

    
    news = {'title': result_title, 
            'description': result_description,
            'date_published' : result_date_published,
            # 'sentiment': sentiment
            }

    news_data = []
    for i in range(len(result_title)):
        _title = result_title[i]
        _description = result_description[i]
        _date_published = result_date_published[i]
        _data = {'title': _title, 
                 'description': _description,
                 'date_published' : _date_published,
                 # 'sentiment': sentiment
                }
        news_data.append(_data)

    return news_data


def answers_format():
    return "{'impact' : 'fill this'}"

def generate_response(news, api_key):
    prompt = f"""given this news article\n{news}\n
    based on this news, can you give your opinion how important the news and its impact to the oil prices. give scale 1-10
    Give your answers similar to this format
    {answers_format()}
    """
    openai.api_key = api_key[0]
    openai.api_base = api_key[1]
    openai.api_type = 'azure'
    openai.api_version = '2023-08-01-preview'

    response = openai.Completion.create(
        engine="gpt-pwc",
        prompt=prompt,
        max_tokens=400,
        n=1,
        stop=None,
        temperature=0.15
    )

    response_str = response.choices[0].text.strip()


    return response_str

def get_sentiment(article):
    openai_key = ''
    openai_api_base = 'https://pwc-azure.openai.azure.com/'
    result = generate_response(article, [openai_key, openai_api_base])
    return ast.literal_eval(result)['impact']
    

    




