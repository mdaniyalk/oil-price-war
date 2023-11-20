from flask import Flask, render_template, jsonify
from random import randint
from threading import Thread
import time
from datetime import datetime, timedelta

app = Flask(__name__)

# Initial data for line graphs
graph1_data = [randint(0, 10) for _ in range(10)]
graph2_data = [randint(0, 10) for _ in range(1440)]  # 1440 data points for 24 hours

# Initial data for text field
text_data = "Initial Text"

# Function to update data every 1 second
def update_data():
    global graph1_data, graph2_data, text_data
    while True:
        # Simulate updating data for "Actual Price" every 1 minute
        graph1_data = graph1_data[1:] + [randint(0, 10)]

        # Simulate updating data for "Forecasted Price" every 24 hours
        graph2_data = graph2_data[1:] + [randint(0, 10)]
        text_data = f"Updated Text: {randint(0, 100)}"

        time.sleep(60)  # Sleep for 1 minute

# Start the data update thread
update_thread = Thread(target=update_data)
update_thread.daemon = True
update_thread.start()

# Route for the main dashboard
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint for getting updated data
@app.route('/get_data')
def get_data():
    return jsonify({
        'graph1': graph1_data,
        'graph2': graph2_data,
        'text': text_data
    })

if __name__ == '__main__':
    app.run(debug=True)
