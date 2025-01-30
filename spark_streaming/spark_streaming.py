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
from utils import aggregator, get_garage_structure

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


#generated sensors
def generate_parking_structure(parking_id, latitude, longitude, num_parkings: int):
    """
        Used to generate all the spots inside a certain location
    """

    parking_spots = []
    for i in range(num_parkings):
        parking_spot = {
            "device_id": f"spot_{i + 1:04d}",
            "parking_id": parking_id,
            "location": {
                "latitude": latitude,
                "longitude": longitude
            }
       }
        parking_spots.append(parking_spot)
    return parking_spots


# generate parking data for all spots at a given time interval, give as input a vector of parkings in the same location
def create_parking_dataset(structures: list):

    all_parkings = []
    for struct in structures:
        all_parkings.append(generate_parking_structure(struct["parking_id"], 
                    struct["latitude"], struct["longitude"], random.randint(50,200)))

    return all_parkings


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

        for garage in lots:
            for spot in garage:
                park_flag = random.choice([0, 1])
                # if the sensor malfunctions, then the spot is marked automatically as occupied
                battery_percent = 100 if random.random() > 0.005 else 0
                if battery_percent == 0:
                    park_flag = 0

                single_record = {
                    "device_id": spot["device_id"],
                    "parking_id": spot["parking_id"],
                    "metadata_time": current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "location": {
                        "latitude": spot["location"]["latitude"],
                        "longitude": spot["location"]["longitude"]
                    },
                    "payload_fields_park_flag": park_flag,
                    "payload_fields_battery_percent": battery_percent,
                    "payload_fields_low_voltage": "False",
                    "counter": random.randint(1, 1000),
                    "active": 1
                }
                record.append(single_record)
        aggregated = aggregator(structure, record)

        #for lot in aggregated:
        try:
            client.publish("closed_parking/data", json.dumps(aggregated))
            logger.info(f"Published: {aggregated}")
        except Exception as error:
            logger.error(f"Error publishing to MQTT broker: {error}")
    except Exception as e:
        logger.error(f"Error processing data: {e}")

if __name__ == "__main__":
    mqtt_broker = "mosquitto"

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

    structure = get_garage_structure()
    sensors =  create_parking_dataset(structure)
    
    if not sensors or not str:
        logger.error("Critical files are missing or invalid. Exiting.")
        exit(1)

    while True:
        t = datetime.now(timezone.utc)
        process_and_publish_data(t, sensors, structure)
        logger.info("Sleeping for 5 seconds")
        time.sleep(5)