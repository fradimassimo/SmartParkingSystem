import json
import queue
import threading
from datetime import datetime
import paho.mqtt.client as mqtt
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


mqtt_broker = "mosquitto"
mqtt_topic_zone = "zone/select"
mqtt_topic_closed = "closed_parking/data"
mqtt_topic_forecast_response = "forecast/response"


client = mqtt.Client()
client.connect(mqtt_broker, 1883, 60)


closed_data_queue = queue.Queue()
forecast_data_queue = queue.Queue()



def get_zone(lat, lon):
    """
    Retrieves zone based on latitude and longitude.
    """
    zones = {
        "NORD": {"latitude": [46.100001, 46.12], "longitude": [11.070001, 11.14]},
        "SUD": {"latitude": [46.04, 46.06], "longitude": [11.0070001, 11.14]},
        "EST": {"latitude": [46.060001, 46.10], "longitude": [11.110001, 11.14]},
        "OVEST": {"latitude": [46.060001, 46.10], "longitude": [11.070001, 11.10]},
        "CENTRO": {"latitude": [46.060001, 46.10], "longitude": [11.100001, 11.11]},
    }

    for zone, coords in zones.items():
        lat_min, lat_max = coords["latitude"]
        lon_min, lon_max = coords["longitude"]
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return zone

def on_closed_message(client, userdata, msg):
    """
    Retrieves closed_parking data once a message is received on topic closed_parking/data
    """
    try:
        closed_parkings = json.loads(msg.payload)
        if isinstance(closed_parkings, list):
            closed_data_queue.put(closed_parkings)
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON payload: {msg.payload}, error: {e}")

def on_forecast_message(client, userdata, msg):
    """
    Retrieves forecast data once a message is received on topic forecast/response
    """
    try:
        forecast_data = json.loads(msg.payload)
        if isinstance(forecast_data, list) and forecast_data:
            forecast_data_queue.put(forecast_data)
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON payload: {msg.payload}, error: {e}")

client.message_callback_add(mqtt_topic_closed, on_closed_message)
client.subscribe(mqtt_topic_closed)
client.message_callback_add(mqtt_topic_forecast_response, on_forecast_message)
client.subscribe(mqtt_topic_forecast_response)

def mqtt_loop():
    client.loop_forever()

mqtt_thread = threading.Thread(target=mqtt_loop)
mqtt_thread.daemon = True
mqtt_thread.start()

@app.route('/')
def index():
    """
    Renders the home page
    """
    return render_template('index.html')


@app.route('/select_zone', methods=["POST"])
def select_zone():
    """
    Takes {zone} (user choice on GUI),
    redirects user to zone_selected.html and publish {zone} on zone/select topic
    """
    zone = request.form['zone']
    client.publish(mqtt_topic_zone, zone)
    return redirect(url_for('zone_selected', zone=zone))

@app.route('/zone_selected/<zone>')
def zone_selected(zone):
    """
    Takes {zone} (user choice on GUI),
    fetch data from forecast/response topic and closed_parking/data
    to show filtered per zone parking data to the user on zone_selected.html
    """
    try:
        closed_data = closed_data_queue.get_nowait() if not closed_data_queue.empty() else []
        forecast_data = forecast_data_queue.get_nowait() if not forecast_data_queue.empty() else []

    except queue.Empty:
        closed_data = []
        forecast_data = []


    filtered_data = [parking for parking in closed_data if get_zone(parking["location"]["latitude"], parking["location"]["longitude"]) == zone]


    for entry in forecast_data:
        timestamp = entry['timestamp']
        dt = datetime.fromisoformat(timestamp)
        entry['timestamp'] = dt.strftime('%H:%M')
        entry['forecasted_occupancy'] = entry['forecasted_occupancy'] * 100
    filtered_forecast = forecast_data


    return render_template('zone_selected.html',
                           zone=zone,
                           parkings=filtered_data,
                           filtered_forecast=filtered_forecast)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)