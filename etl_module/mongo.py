from pymongo import MongoClient
from datetime import datetime, timedelta
from .crawl import *
import certifi

def initialize_history_price():
    client = MongoClient('mongodb+srv://mdaniyalk:1234@cluster-rekdat.7teizco.mongodb.net/rekdat', tlsCAFile=certifi.where())
    
    db = client['rekdat']
    collection = db['history_price']

    data = get_historical_price(period='max', interval="1m")

    for entry in data:
        timestamp = entry['timestamp']

        existing_entry = collection.find_one({'timestamp': timestamp})

        if existing_entry is None:
            collection.insert_one(entry)

    client.close()
    

def post_history_price():
    client = MongoClient('mongodb+srv://mdaniyalk:1234@cluster-rekdat.7teizco.mongodb.net/rekdat', tlsCAFile=certifi.where())
    
    db = client['rekdat']
    collection = db['history_price']
    data = get_last_minutes_price()
    timestamp = data['timestamp']
    existing_entry = collection.find_one({'timestamp': timestamp})

    if existing_entry is None:
        collection.insert_one(data)
    client.close()
    return data['close_price']

def initialize_history_news():
    client = MongoClient('mongodb+srv://mdaniyalk:1234@cluster-rekdat.7teizco.mongodb.net/rekdat', tlsCAFile=certifi.where())
    
    db = client['rekdat']
    collection = db['history_news']
    
    data = get_historical_news(query='war', 
                               sources='bbc-news,the-verge, new-york-times', 
                               domains='bbc.co.uk,techcrunch.com,nytimes.com', 
                               start='2023-10-29', 
                               end='2023-11-29', 
                               language='en')
    print(len(data))
    for entry in data:
        title = entry['title']

        existing_entry = collection.find_one({'title': title})

        if existing_entry is None:
            collection.insert_one(entry)

    client.close()
    

def post_history_news():
    client = MongoClient('mongodb+srv://mdaniyalk:1234@cluster-rekdat.7teizco.mongodb.net/rekdat', tlsCAFile=certifi.where())
    
    db = client['rekdat']
    collection = db['history_news']
    current_datetime = datetime.now()
    
    previous_day_datetime = current_datetime - timedelta(days=1)

    data = get_historical_news(query='war', 
                               sources='bbc-news,the-verge, new-york-times', 
                               domains='bbc.co.uk,techcrunch.com,nytimes.com', 
                               start=previous_day_datetime.strftime("%Y-%m-%d"), 
                               end=current_datetime.strftime("%Y-%m-%d"), 
                               language='en')
    
    headlines = ''

    for entry in data:
        title = entry['title']

        existing_entry = collection.find_one({'title': title})

        if existing_entry is None:
            collection.insert_one(entry)
        headlines += f"{title}\n"

    client.close()

    
    return headlines






