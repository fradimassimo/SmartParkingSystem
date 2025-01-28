import random
from datetime import datetime, timedelta
import psycopg2

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


# load it into PostgreSQL
# PostgreSQL connection (reuse the same connection from above)
conn = psycopg2.connect(
    dbname="smart-parking",
    user="admin",
    password="root",
    host="postgres",
    port="5432"
)
cur = conn.cursor()


# generate fake occupancy data
start_time = datetime(2025, 1, 30, 23, 45)
end_time = datetime(2025, 1, 2, 0, 0)
time_interval = timedelta(minutes=15)

# Exclude these parking IDs (they are generated from actual data)
excluded_ids = {1, 3, 7, 8}
parking_ids = [i for i in range(1, 121) if i not in excluded_ids]
garage_ids = [f"C{i:03d}" for i in range(1,16)]
parking_ids = parking_ids + garage_ids

occupancy_data = generate_fake_parking_data(start_time, end_time, time_interval, parking_ids)


# Insert occupancy data
try:
    for record in occupancy_data:
        cur.execute(
            """
            INSERT INTO occupancy_data (parking_id, timestamp, occupancy, vacancy)
            VALUES (%s, %s, %s, %s)
            """,
            (
                record["parking_id"],
                record["timestamp"],
                record["occupancy"],
                record["vacancy"]
            )
        )
    
    print("Occupancy data successfully inserted!")
    
except Exception as e:
    print(f"An error occurred while inserting occupancy data: {e}")

conn.commit()
cur.close()
conn.close()




