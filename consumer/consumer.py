"""
Connection to Postgres, subscription to an MQTT topic, and saving one message every 15 minutes.
"""

import paho.mqtt.client as mqtt
import psycopg2
import json
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_CONFIG = {
    "dbname": "smart-parking",
    "user": "admin",
    "password": "root",
    "host": "postgres",
    "port": "5432"
}
last_save_time = datetime.min


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT broker.")
    else:
        logger.error(f"Failed to connect to MQTT broker, return code {rc}")


def on_message(client, userdata, msg):
    """On message, check if 15 minutes have passed since the last save, then save the data."""

    global last_save_time

    try:
        logger.info(f"Message received on topic {msg.topic}")
        data_list = json.loads(msg.payload)

        if not isinstance(data_list, list):
            logger.error("Received data is not a list.")
            return

        current_time = datetime.now()
        # Check if 15 minutes have passed since the last save
        if (current_time - last_save_time) < timedelta(minutes=15):
            logger.info("Skipping message as 15 minutes haven't passed yet.")
            return

        #  if htey have passed, save the data
        db_conn = userdata["db_conn"]
        insert_query = """
            INSERT INTO occupancy_data (parking_id, timestamp, occupancy, vacancy)
            VALUES (%s, %s, %s, %s)
        """

        with db_conn.cursor() as cur:
            for data in data_list:
                cur.execute(insert_query, (
                    data["parking_id"],
                    data["metadata_time"],
                    data["occupancy"],
                    data["vacancy"]
                ))

        last_save_time = current_time
        logger.info(f"Inserted data into DB: {data_list}")

    except Exception as e:
        logger.error(f"Error processing message: {e}")


def postgres_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        logger.info("Connected to Postgres DB.")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error connecting to Postgres DB: {e}")
        return None


if __name__ == "__main__":

    mqtt_broker = "mosquitto"
    mqtt_topic = "closed_parking/data"
    db_conn = postgres_connection()
    if db_conn is None:
        logger.error("Exiting because Postgres DB connection failed.")
        exit(1)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.user_data_set({"db_conn": db_conn})

    try:
        client.connect(mqtt_broker, 1883, 60)
        # Subscribe to closed_parking/data topic
        client.subscribe(mqtt_topic)
        logger.info(f"Subscribed to topic: {mqtt_topic}")
        client.loop_forever()
    except Exception as e:
        logger.error(f"Error in MQTT connection or loop: {e}")