""""
Connection to postgres, subscription on a topic MQTT every 15 minutes and insert in postgres table
"""

import paho.mqtt.client as mqtt
import psycopg2
import json
import logging
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_CONFIG = {
    "dbname": "smart-parking",
    "user": "admin",
    "password": "root",
    "host": "postgres",
    "port": "5432"
}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT broker.")
    else:
        logger.error(f"Failed to connect to MQTT broker, return code {rc}")

def on_log(client, userdata, level, buf):
    logger.info(f"Log: {buf}")

def on_sub(client, userdata, mid):
    logger.info(f"Message {mid} has been published.")


def on_message(client, userdata, msg):
    try:
        logger.info(f"Message received on topic {msg.topic}")
        data_list = json.loads(msg.payload)

        if not isinstance(data_list, list):
            logger.error("Received data is not a list.")
            return

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


def sub_and_insert_data(client, db_conn):
    client.subscribe(mqtt_topic)
    client.user_data_set({"db_conn": db_conn})
    logger.info(f"Subscribed to topic: {mqtt_topic}")


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
    client.on_log = on_log

    try:
        client.connect("mosquitto", 1883, 60)
        client.loop_start()
    except Exception as e:
        logger.error(f"Error in MQTT connection or loop: {e}")

    while True:
        sub_and_insert_data(client, db_conn)
        logger.info("Listening for messages")
        logger.info("Sleeping for 15 minutes before the next cycle.")
        time.sleep(900)  # Sleep for 15 minutes (900 seconds)

