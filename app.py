from flask import Flask, render_template, jsonify
import pandas as pd
import random
from datetime import datetime
import os
from statsmodels.tsa.arima.model import ARIMA

app = Flask(__name__)

DATA_FILE = 'data.csv'

# Ensure data file exists
def initialize_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame({
            "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            "wind_speed": [10]
        })
        df.to_csv(DATA_FILE, index=False)

def update_data():
    data = pd.read_csv(DATA_FILE)

    now = datetime.now()
    last_speed = data['wind_speed'].iloc[-1]

    new_speed = last_speed + random.uniform(-3, 3)
    new_speed = max(5, min(45, new_speed))

    new_row = pd.DataFrame(
        [[now.strftime("%Y-%m-%d %H:%M:%S"), round(new_speed, 2)]],
        columns=['timestamp', 'wind_speed']
    )

    data = pd.concat([data, new_row], ignore_index=True)
    data.to_csv(DATA_FILE, index=False)


@app.route('/')
def dashboard():
    return render_template('index.html')


@app.route('/api/data')
def get_data():
    initialize_data()
    update_data()

    data = pd.read_csv(DATA_FILE)
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    present_speed = round(data.iloc[-1]['wind_speed'], 2)

    series = data['wind_speed']

    if len(series) > 10:
        model = ARIMA(series, order=(1, 1, 0))
        model_fit = model.fit()
        future_speed = round(float(model_fit.forecast(steps=1).iloc[0]), 2)
    else:
        future_speed = round(present_speed + random.uniform(-2, 2), 2)

    return jsonify({
        "time": datetime.now().strftime("%H:%M:%S"),
        "speed": present_speed,
        "direction": random.randint(0, 360),
        "future": future_speed
    })


# 🚨 Important for Railway (Gunicorn uses this)
if __name__ != "__main__":
    initialize_data()

# Local run only
if __name__ == '__main__':
    app.run(debug=True)