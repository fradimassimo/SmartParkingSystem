from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import paho.mqtt.client as mqtt
import time
import json
import threading

app = Flask(__name__)

# MQTT setup


mqtt_broker = "mosquitto"
mqtt_topic_zone = "zone/select"
mqtt_topic_alerts = "closed_parking/data" #(20 sec published)
#mqtt_forecast_request = "forecast/request"
mqtt_topic_forecast_response = "forecast/response"
#sulla base della request response manda json con previsioni dati street per quella zona
#prendi solo le prime 24
#ogni dict timestamp (keys sono timestamp e forecasted_occupancy)

client = mqtt.Client()
client.connect(mqtt_broker, 1883, 60)


####################################### closed_parkings #####################################################à
closed_data = []
selected_zone = None
def get_zone(lat, lon):
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

# Funzione per gestire i messaggi di parcheggi chiusi
def on_closed_message(client, userdata, msg):
    global closed_data
    closed_data = []
    try:
        closed_parkings = json.loads(msg.payload)
        print(f"Received alert payload: {closed_parkings}")
        if isinstance(closed_parkings, list):
            closed_data = closed_parkings
        else:
            print(f"Invalid format or not a list: {closed_parkings}")

    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON payload: {msg.payload}, error: {e}")


# Funzione per ottenere i dati filtrati in base alla zona richiesta
def get_data_for_zone(zone):
    """Restituisce i parcheggi relativi alla zona selezionata."""
    if zone:
        filtered_parkings = [
            parking for parking in closed_data
            if get_zone(parking["location"]["latitude"], parking["location"]["longitude"]) == zone
        ]
        return filtered_parkings
    else:
        print("Nessuna zona selezionata.")
        return []
        # Se non è stata selezionata alcuna zona, restituisci una lista vuota


# Subscrizione ai topic
client.message_callback_add(mqtt_topic_alerts, on_closed_message)  # Callback per i parcheggi chiusi
client.subscribe(mqtt_topic_alerts)  # Sottoscrive al topic 'closed_parking/data' per i parcheggi chiusi

##################################### closed_parkings ########################################################



###################################### forecast ###############################################################

forecast_data = []
def on_forecast_message(client, userdata, msg):
    global forecast_data
    forecast_data = []
    try:
        forecast_data = json.loads(msg.payload)
        print(f"Ricevute previsioni: {forecast_data}")
        if isinstance(forecast_data, list):
            return forecast_data
        else:
            print("Dati previsioni non nel formato previsto.")

    except json.JSONDecodeError as e:
        print(f"Errore nella ricezione delle previsioni: {e}")


def get_24h_forecast(forecast):
    first_24h = forecast[:24]  # Prende prime 24h di forecast data
    return first_24h


client.message_callback_add(mqtt_topic_forecast_response, on_forecast_message)
client.subscribe(mqtt_topic_forecast_response)

##################################### forecast ###########################################################à


def mqtt_loop():
    client.loop_forever()

mqtt_thread = threading.Thread(target=mqtt_loop)
mqtt_thread.start()



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/select_zone', methods=["POST"])
def select_zone():
    global selected_zone
    zone = request.form['zone']  # Recupera la zona selezionata dal modulo
    selected_zone = zone  # Aggiorna la zona selezionata
    client.publish(mqtt_topic_zone, zone)  # Pubblica la zona selezionata nel topic MQTT
    print(f"Zona selezionata: {selected_zone}")

    #Redirige l'utente alla pagina corrispondente della zona
    return redirect(url_for('zone_selected', zone=selected_zone))


@app.route('/zone_selected/<zone>')
def zone_selected(zone):
    filtered_data = get_data_for_zone(zone) # Ottieni i parcheggi filtrati per zona
    print(f"Filtered Parkings: {filtered_data}")
    filtered_forecast =  get_24h_forecast(forecast_data) # Ottieni le prime 24
    print(f"Filtered Forecast: {filtered_forecast}")
    return render_template('zone_selected.html',
                           zone=zone,
                           parkings=filtered_data,
                           forecasts=filtered_forecast)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
