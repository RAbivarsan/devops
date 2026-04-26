from flask import Flask, render_template, jsonify
import pandas as pd
import random
from datetime import datetime
from statsmodels.tsa.arima.model import ARIMA

app = Flask(__name__)

def update_data():
    data = pd.read_csv('data.csv')

    now = datetime.now()
    last_speed = data['wind_speed'].iloc[-1]

    new_speed = last_speed + random.uniform(-3, 3)
    new_speed = max(5, min(45, new_speed))

    new_row = pd.DataFrame(
        [[now.strftime("%Y-%m-%d %H:%M:%S"), round(new_speed, 2)]],
        columns=['timestamp', 'wind_speed']
    )

    data = pd.concat([data, new_row], ignore_index=True)
    data.to_csv('data.csv', index=False)


@app.route('/')
def dashboard():
    return render_template('index.html')


# 🔥 NEW API ROUTE
@app.route('/api/data')
def get_data():
    update_data()

    data = pd.read_csv('data.csv')
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    present_speed = round(data.iloc[-1]['wind_speed'], 2)

    # Prediction
    series = data['wind_speed']
    if len(series) > 10:
        model = ARIMA(series, order=(1,1,0))
        model_fit = model.fit()
        future_speed = round(float(model_fit.forecast(steps=1).iloc[0]), 2)
    else:
        future_speed = present_speed + random.uniform(-2, 2)

    return jsonify({
        "time": datetime.now().strftime("%H:%M:%S"),
        "speed": present_speed,
        "direction": random.randint(0, 360),
        "future": future_speed
    })


if __name__ == '__main__':
    app.run(debug=True)