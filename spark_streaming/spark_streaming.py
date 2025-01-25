""""
How it works:
Spots sensors inside {Park_001, ..., Park_015}: Periodically publish MQTT messages on topic closed_parking/data.
Spark Streaming manage this flux of data from topic closed_parking/data.
It aggregates the spots per Park_0**
It generates alerts if parking availability is under a certain threshold.
It save data about spots every 15 minutes in postgres DB.

[STARTING THE NET]
docker-compose down --remove-orphans
docker-compose up --build
NB) do not run from python file (as long as you just want to test it locally)
"""
import signal

from fontTools.merge.util import current_time
from pyspark.sql import SparkSession
import paho.mqtt.client as mqtt
import json
from datetime import datetime, timezone
import time
import logging
import random

spark = SparkSession.builder.appName("SparkStreamingApp").getOrCreate()

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


def process_and_publish_data(t):

    try:
        # Open the JSON file and load data
        with open('1766_sensors_data.json', 'r', encoding='utf-8') as file:
            lots = json.load(file)
    except FileNotFoundError:
        logger.error("File '1766_sensors_data.json' not found!")
        return
    except json.JSONDecodeError:
        logger.error("Error decoding JSON file! Ensure it is correctly formatted.")
        return

    current_time = t

    for spot in lots:
        #aggiungi timestemp
        park_flag = random.choice([0, 1])
        # if the sensor malfunctions, then the spot is marked automatically as occupied
        battery_percent = 100 if random.random() > 0.005 else 0
        if battery_percent == 0:
            park_flag = 0

        record = {
            "device_id": spot["deviceid"],
            "metadata_time": current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "location": spot["location"],
            "payload_fields_park_flag": park_flag,
            "payload_fields_battery_percent": battery_percent,
            "payload_fields_low_voltage": "False",
            "counter": random.randint(1, 1000),
            "active": 1
        }

        try:
            client.publish("closed_parking/data", json.dumps(record))
            logger.info(f"Published: {record}")
        except Exception as error:
            logger.error(f"Error publishing to MQTT broker: {error}")


if __name__ == "__main__":
    mqtt_broker = "mosquitto"
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_log = on_log

    client.connect(mqtt_broker, 1883, 60)
    client.loop_start()

    while True:
        t = datetime.now(timezone.utc)
        process_and_publish_data(t)
        logger.info("Sleeping for 20 seconds")
        time.sleep(20)