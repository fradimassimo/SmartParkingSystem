""""
Let's assume first that 3 different 'closed' parking lots publish MQTT messages (P1, P2, P3) with the following format.

{
    "parking_id": "P1",
    "available_spots": 25
}
How should work:
Sensors connected to {P1, P2, P3}: Periodically publish MQTT messages on topic closed_parking/data.
Spark Streaming process data from topic closed_parking/data.
It generates alerts if parking availability is under a certain threshold and computes some metrics.
There is a dumb script to simulate random data.
[STARTING THE NET]
docker-compose down --remove-orphans
docker-compose up --build
NB) do not run from python file (as long as you just want to test it locally)
"""

from pyspark.sql import SparkSession
import paho.mqtt.client as mqtt
import json
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

def process_and_publish_data():

    with open('closed_lots.json', 'r', encoding='utf-8') as file:
        lots = json.load(file)

    for i in range(200):
        lot = random.choice(lots)
        parking_id = lot["ID"]
        capacity = lot["capacity"]
        availability = int(random.uniform(0,capacity))
        if (availability/capacity) * 100 < 5:
            alert = 1
        else:
            alert = 0

        try:

            message = {
                "parking_id": parking_id,
                "available_spots": availability,
                "alert": alert
            }

            client.publish("closed_parking/data", json.dumps(message))
            logger.info(f"Published: {message}")

        except ConnectionRefusedError:
            logger.error("MQTT broker connection was refused.")

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
        process_and_publish_data()
        logger.info("Sleeping for 20 seconds")
        time.sleep(20)