from flask import Flask, render_template, jsonify
from random import randint
from threading import Thread
import time
from datetime import datetime, timedelta
import time
import pickle


from etl_module.crawl import *
from etl_module.mongo import *
from etl_module.predictive import *


app = Flask(__name__)


with open('predictive.pkl', 'rb') as file:
    model = pickle.load(file)
model._n_classes = 1 

raw_graph1_data = get_historical_price(period='1d', interval="1m")
graph1_data = [data['close_price'] for data in raw_graph1_data]
graph1_data = graph1_data[-60:]

graph2_data = predict_next_30_days(model).tolist()
print(graph2_data)

text_data = post_history_news()


def update_graph1_data():
    global graph1_data
    while True:
        time.sleep(60)
        graph1_data = graph1_data[1:] + [post_history_price()]
        

def update_graph2_data():
    global graph2_data, text_data
    while True:
        time.sleep(60 * 60 * 24)
        graph2_data = predict_next_30_days(model).tolist()
        text_data = post_history_news()
        

# Start threads for updating graph1_data and graph2_data
graph1_update_thread = Thread(target=update_graph1_data)
graph1_update_thread.daemon = True
graph1_update_thread.start()

graph2_update_thread = Thread(target=update_graph2_data)
graph2_update_thread.daemon = True
graph2_update_thread.start()



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_data')
def get_data():
    return jsonify({
        'graph1': graph1_data,
        'graph2': graph2_data,
        'text': text_data
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, Debug=True)
