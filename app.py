from flask import Flask, render_template
import pandas as pd
import random
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA
import warnings

warnings.filterwarnings("ignore")

app = Flask(__name__)

# ------------------ UPDATE LIVE DATA ------------------
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


# ------------------ DASHBOARD ------------------
@app.route('/')
def dashboard():
    update_data()

    data = pd.read_csv('data.csv')
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    # -------- CURRENT --------
    present_speed = round(data.iloc[-1]['wind_speed'], 2)
    current_time = data.iloc[-1]['timestamp'].strftime("%H:%M:%S")

    # -------- FUTURE --------
    series = data['wind_speed']

    if len(series) < 10:
        future_speed = present_speed + random.uniform(-2, 2)
    else:
        model = ARIMA(series, order=(1,1,0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=1)
        future_speed = round(float(forecast.iloc[0]), 2)

    # smooth jump
    if abs(future_speed - present_speed) > 5:
        future_speed = present_speed + random.uniform(-2, 2)

    future_time = (datetime.now() + timedelta(minutes=5)).strftime("%H:%M:%S")

    # -------- HISTORICAL --------
    last_year = datetime.now().year - 1
    current_month = datetime.now().month

    historical = data[
        (data['timestamp'].dt.year == last_year) &
        (data['timestamp'].dt.month == current_month)
    ]

    # fallback if empty
    if historical.empty:
        dates = pd.date_range(start=f"{last_year}-{current_month}-01", periods=10)
        speeds = [random.randint(10, 30) for _ in range(10)]
        historical = pd.DataFrame({
            "timestamp": dates,
            "wind_speed": speeds
        })

    return render_template(
        'index.html',
        past_times=data['timestamp'].dt.strftime('%H:%M:%S').tolist(),
        past_speeds=data['wind_speed'].tolist(),
        present_speed=present_speed,
        future_speed=future_speed,
        current_time=current_time,
        future_time=future_time,
        hist_times=historical['timestamp'].dt.strftime('%d-%m').tolist(),
        hist_speeds=historical['wind_speed'].tolist()
    )


if __name__ == '__main__':
    app.run(debug=True)