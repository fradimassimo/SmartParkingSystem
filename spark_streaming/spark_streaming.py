""""
How it works:
Generation of data simulating Spots sensors inside {Park_001, ..., Park_015}.
Local aggregation, based on coordinates (sensors having same coordinates come from same Park_0**).
Pub of MQTT messages on topic closed_parking/data in order to consume data in real time on dashboard.
Saving every 15 minutes in a postgres DB the last snapshot to accumulate data for more accurate predictions.

Spark Streaming could have managed a flux of true realtime data
I.e. reding a file with a relative path from a remote location,
such as HFS or S3 and performs data aggregation and processing in an efficient and highly scalable way.


[STARTING THE NET]
docker-compose down --remove-orphans
docker-compose up --build
NB, do not run from python file (as long as you just want to test it locally)
"""


from pyspark.sql import SparkSession
import paho.mqtt.client as mqtt
import json
from datetime import datetime, timezone
import time
import logging
import random

from utils import aggregator

#spark = SparkSession.builder.appName("SparkStreamingApp").getOrCreate()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT Broker successfully")
    else:
        logger.error(f"Failed to connect to MQTT Broker, return code {rc}")

def on_publish(client, userdata, mid):
    logger.info(f"Message {mid} has been published.")

def on_log(client, userdata, level, buf):
    logger.info(f"Log: {buf}")

def load_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"File '{file_path}' not found!")
        return []
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON file '{file_path}'! Ensure it is correctly formatted.")
        return []

def process_and_publish_data(tempo, lots, structure):
    try:
        """
        schema = ...
        df = spark.read.schema(schema).json("/app/live_data.json") 
        df.createOrReplaceTempView("closed_lots_data")
        processed_data = ...
        """

        current_time = tempo
        record = []
        for spot in lots:
            park_flag = random.choice([0, 1])
            # if the sensor malfunctions, then the spot is marked automatically as occupied
            battery_percent = 100 if random.random() > 0.005 else 0
            if battery_percent == 0:
                park_flag = 0

            single_record = {
                "device_id": spot["deviceid"],
                "metadata_time": current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "location": spot["location"],
                "payload_fields_park_flag": park_flag,
                "payload_fields_battery_percent": battery_percent,
                "payload_fields_low_voltage": "False",
                "counter": random.randint(1, 1000),
                "active": 1
            }
            record.append(single_record)
        aggregated = aggregator(structure, record)

        for lot in aggregated:
            try:
                client.publish("closed_parking/data", json.dumps(lot))
                logger.info(f"Published: {lot}")
            except Exception as error:
                logger.error(f"Error publishing to MQTT broker: {error}")
    except Exception as e:
        logger.error(f"Error processing data: {e}")

if __name__ == "__main__":
    mqtt_broker = "mosquitto" #mosquitto

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_log = on_log

    retry = 0
    retry_timeout = 10
    while retry < 10:
        try:
            client.connect(mqtt_broker, 1883, 60)
            client.loop_start()
            break
        except ConnectionRefusedError as error:
            retry += 1
            print(f"Connection refused, retrying, attempt: {retry}")
            time.sleep(retry_timeout)
            continue

    sensors = load_json_file('/app/1766_sensors_data.json')
    str = load_json_file('/app/corrected_closed_parking_structures.json')
    if not sensors or not str:
        logger.error("Critical files are missing or invalid. Exiting.")
        exit(1)

    while True:
        t = datetime.now(timezone.utc)
        process_and_publish_data(t, sensors, str)
        logger.info("Sleeping for 20 seconds")
        time.sleep(20)