import random
from datetime import datetime, timedelta
import psycopg2
from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, MetaData
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import pandas as pd

def generate_coordinates_within_bounds(bounds, num_coordinates):
    """ bounds should be a tuple of tuples ((lat_min, lat_max), (lon_min, lon_max)) or a vector of tuples,
    num_coordinates is an integer"""

    coordinates = []
    for _ in range(num_coordinates):
        lat = random.uniform(bounds[0][0], bounds[0][1])
        lon = random.uniform(bounds[1][0], bounds[1][1])
        coordinates.append((round(lat, 6), round(lon, 6)))
    return coordinates

def generate_fake_parking_data(start_time, end_time, time_interval, parking_ids):
    data = []

    for parking_id in parking_ids:
        current_time = start_time
        total_slots = random.randint(15, 110)

        while current_time >= end_time:
            occupancy = random.randint(0, total_slots)
            vacancy = total_slots - occupancy

            record = {
                "parking_id": parking_id,
                "timestamp": current_time.isoformat(),
                "occupancy": occupancy,
                "vacancy": vacancy
            }
            data.append(record)

            current_time -= time_interval

    return data


def create_closed_parking(bounds, num_locations):
    """
        Used to generate street parking locations.
        bounds should be a tuple of tuples ((lat_min, lat_max), (lon_min, lon_max)) or a vector of tuples.
        num_locations (int) is the number of parking locations (i.e. group of parking spots) to generate.
        returns a dictionary as output.
    """

    # we generate a set of coordinates within the boundaries of a rectangle
    coordinates = generate_coordinates_within_bounds(bounds, num_locations)

    # create a parking lot for each location
    parking_lots = []
    for i, coord in enumerate(coordinates, start=1):
        parking_lot = {
            "parking_id": f"C{i:03d}",
            "name": f"Garage_{i:03d}",
            "location": {
                "latitude": coord[0],
                "longitude": coord[1]
            },
            "paying_hours": "00:00-24:00",
            "price_per_hour": random.choice([0.8, 1.0, 1.5, 2.0, 2.5])
        }
        parking_lots.append(parking_lot)
        # print(parking_lot)

    return parking_lots


DATABASE_URL = "postgresql://admin:root@postgres:5432/smart-parking"
engine = create_engine(DATABASE_URL)

metadata = MetaData()
occupancy_data_table = Table(
    "occupancy_data", metadata,
    Column("parking_id", String, primary_key=True),
    Column("timestamp", DateTime, primary_key=True),
    Column("occupancy", Integer),
    Column("vacancy", Integer),
)

Session = sessionmaker(bind=engine)
session = Session()

start_time = datetime(2025, 1, 30, 23, 45)
end_time = datetime(2025, 1, 2, 0, 0)
time_interval = timedelta(minutes=15)

excluded_ids = {1, 3, 7, 8}
parking_ids = [i for i in range(1, 121) if i not in excluded_ids]
garage_ids = [f"C{i:03d}" for i in range(1, 16)]
parking_ids += garage_ids

occupancy_data = generate_fake_parking_data(start_time, end_time, time_interval, parking_ids)

df = pd.DataFrame(occupancy_data)

try:
    session.bulk_insert_mappings(occupancy_data_table, df.to_dict(orient="records"))
    session.commit()
    print("Occupancy data successfully inserted!")

except Exception as e:
    session.rollback()
    print(f"An error occurred while inserting occupancy data: {e}")

finally:
    session.close()
