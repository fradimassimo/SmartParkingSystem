import json
from datetime import datetime, timedelta
import pandas as pd
import pickle
import utils
import paho.mqtt.client as mqtt

# MQTT Broker Configuration
BROKER_ADDRESS = "mosquitto"  # Replace with your broker's IP or hostname
REQUEST_TOPIC = "forecast/request"
RESPONSE_TOPIC = "forecast/response"

# Define the MQTT client
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    # Subscribe to the request topic
    client.subscribe(REQUEST_TOPIC)

def on_message(client, userdata, msg):
    try:
        print(f"Received message on {msg.topic}: {msg.payload}")
        
        # Parse the incoming message
        payload = json.loads(msg.payload.decode())
        zone = payload.get("zone")
        parking_type = payload.get("parking_type")

        forecast_df = get_predictions(zone, parking_type)
        forecast_json = forecast_df.to_json(orient="records", date_format="iso")

        client.publish(RESPONSE_TOPIC, forecast_json)
        print("Forecast sent successfully.")
    
    except Exception as e:
        print(f"Error handling message: {e}")


def get_predictions(zone, parking_type, daily = False, start_time = None, festive_dates = None):
    """returns forecast for the next week given a zone, type of parking and a start_time (optional, current time is deafult). """ 
    VALID_ZONES = ["NORD", "SUD", "CENTRO", "EST", "OVEST"]
    VALID_TYPES = ["street", "garage"]
    
    if zone not in VALID_ZONES:
        raise ValueError(f"Invalid zone: {zone}. Valid zones are {VALID_ZONES}.")
    
    if parking_type not in VALID_TYPES:
        raise ValueError(f"Invalid parking type: {parking_type}. Valid types are {VALID_TYPES}.")
    
    if start_time is None:
        start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if daily:
            start_time += timedelta(days=1)
    
    try:
        with open("data_processor/sarima_model.pkl", "rb") as f:
            loaded_model = pickle.load(f)
    except Exception as e:
        print(f"Error loading model, be sure to train it first: {e}")

    n_pred = 24 if daily else 168

    new_records = []
    for i in range(n_pred):
        new_records.append({
            "timestamp": start_time + timedelta(hours=i)
        })

    if festive_dates is None:
        festive_dates = utils.get_festive_dates()


    df_aggregated = pd.DataFrame(new_records)
    df_aggregated['timestamp'] = pd.to_datetime(df_aggregated['timestamp'])

    df_aggregated['hour'] = df_aggregated['timestamp'].dt.hour
    df_aggregated['day_of_week'] = df_aggregated['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday
    df_aggregated['is_festive'] = df_aggregated['day_of_week'].apply(lambda x: 1 if x == 6 else 0)  # Sunday is festive
    df_aggregated['is_festive'] = df_aggregated['timestamp'].dt.date.isin(pd.to_datetime(festive_dates).date) | df_aggregated['is_festive']
    df_aggregated['zone'] = zone
    df_aggregated['parking_type'] = parking_type

    # Create dummy for zones and parking types
    for valid_zone in VALID_ZONES:
        df_aggregated[f'zone_{valid_zone}'] = (df_aggregated['zone'] == valid_zone).astype(int)

    for valid_type in VALID_TYPES:
        df_aggregated[f'parking_{valid_type}'] = (df_aggregated['parking_type'] == valid_type).astype(int)

    df_aggregated.drop(columns=['zone', 'timestamp', 'parking_type'], inplace=True)

    df_aggregated = df_aggregated.astype(int)
    df_aggregated = df_aggregated.apply(pd.to_numeric, errors='coerce').fillna(df_aggregated.mean())

    # Forecast using the loaded SARIMA model
    forecast = loaded_model.forecast(steps=n_pred, exog=df_aggregated)

    if daily:
        mean_occupancy = forecast.mean()
        return mean_occupancy
    else:
        forecast_df = pd.DataFrame({
            "timestamp": pd.date_range(start=start_time, periods=168, freq="h"),
            "forecasted_occupancy": forecast
        })

        return forecast_df  # pandas dataframe with forecasted occupancy for the next week


"""
def main():
    ma = get_prediction_for_week(zone = "NORD", parking_type = "street")
    print(ma.head())
    print(ma.tail())
"""

if __name__ == "__main__":
    # Connect the client
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_ADDRESS, 1883, 60)

    client.loop_forever()