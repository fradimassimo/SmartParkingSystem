from flask import Flask, render_template, request, jsonify
import json
import paho.mqtt.client as mqtt
import threading
import time 

app = Flask(__name__)

# MQTT setup
mqtt_broker = 'mosquitto'
mqtt_topic = 'closed_parking/data'
client = mqtt.Client()
client.connect(host=mqtt_broker, port=1883)

client.subscribe(mqtt_topic)

# Variabile globale per memorizzare i dati di parcheggio
current_parking_data = {}

# Callback per la connessione
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker successfully")
        client.subscribe(mqtt_topic)  # Sottoscrizione al topic
    else:
        print(f"Failed to connect to MQTT Broker, return code {rc}")

# Callback per ricevere i messaggi
def on_message(client, userdata, msg):
    global current_parking_data
    
    try:
        # Decodifica il messaggio JSON ricevuto
        data = json.loads(msg.payload)
        deviceid = data.get('deviceid')
        capacity = data.get('capacity')
        availability = data.get('availability')

        if deviceid:
            # Aggiorna i dati per la zona ricevuta
            current_parking_data[deviceid] = {
                'capacity': capacity,
                'availability': availability,
                'occupied': capacity - availability
            }
    except Exception as e:
        print(f"Errore nel ricevere i dati MQTT: {str(e)}")

# Funzione per eseguire il loop MQTT in un thread separato
def mqtt_loop():
    client.loop_forever()

# Avvia il loop MQTT in un thread separato
mqtt_thread = threading.Thread(target=mqtt_loop)
mqtt_thread.daemon = True  # Assicura che il thread termini quando il programma principale termina
mqtt_thread.start()

# Rotta per la home page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/downtown', methods=['GET', 'POST'])
def downtown():
    global current_parking_data
    
    # Se non ci sono dati disponibili, mostra un messaggio
    if not current_parking_data:
        return render_template('downtown.html', message="Dati non ancora disponibili.")

    # Ottieni le prime 3 zone di parcheggio (dati disponibili)
    parking_zones = list(current_parking_data.keys())[:3]

    if request.method == 'POST':
        selected_zone = request.form.get('parkingZone')  # Ottieni la zona selezionata
        
        # Assicurati che la zona selezionata esista nei dati
        data = current_parking_data.get(selected_zone, None)
        
        if data:
            # Estrai i dati relativi alla zona selezionata
            capacity = data['capacity']
            availability = data['availability']
            occupied = data['occupied']
            
            # Passa i dati al template
            return render_template('downtown.html', parking_zones=parking_zones, 
                                   Park=selected_zone, Capacity=capacity, 
                                   Availability=availability, Occupied=occupied)
        else:
            return jsonify({"message": "No data available for selected zone"})

    # Se il metodo è GET
    return render_template('downtown.html', parking_zones=parking_zones)

# Rotte per altre pagine (esempio)
@app.route('/west')
def west():
    return render_template('west.html')

@app.route('/east')
def east():
    return render_template('east.html')

@app.route('/south')
def south():
    return render_template('south.html')

@app.route('/north')
def north():
    return render_template('north.html')

# Rotta che restituisce un dato JSON (esempio)
@app.route('/data')
def get_data():
    data = {
        'name': 'Flask App',
        'version': '1.0',
        'description': 'Un esempio di applicazione web con Flask'
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
