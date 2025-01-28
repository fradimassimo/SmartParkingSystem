import random
import psycopg2
import logging



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_coordinates_within_bounds(bounds, num_coordinates):
    """ bounds should be a tuple of tuples ((lat_min, lat_max), (lon_min, lon_max)) or a vector of tuples,
    num_coordinates is an integer"""

    coordinates = []
    for _ in range(num_coordinates):
        lat = random.uniform(bounds[0][0], bounds[0][1])
        lon = random.uniform(bounds[1][0], bounds[1][1])
        coordinates.append((round(lat, 6), round(lon, 6)))
    return coordinates

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

def insert_parking_data(parking_data):
    insert_query = """
    INSERT INTO parkings (parking_id, name, latitude, longitude, paying_hours, price_per_hour, parking_type)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    conn = psycopg2.connect(
        dbname="smart-parking",
        user="admin",
        password="root",
        host="postgres",
        port="5432"
    )
    cur = conn.cursor()

    for data in parking_data:
        try:
            with conn.cursor() as cur:
                cur.execute(insert_query, (
                    data["parking_id"],
                    data["name"],
                    data["location"]["latitude"],
                    data["location"]["longitude"],
                    data["paying_hours"],
                    data["price_per_hour"],
                    "garage"
                ))
                logger.info(f"Parking data inserted: {data}")
        except psycopg2.Error as e:
            logger.error(f"Error inserting into Postgres DB: {e}")
    conn.commit()
    cur.close()
    conn.close()



def main():
    lat_min, lat_max = 46.0400, 46.1234
    lon_min, lon_max = 11.0700, 11.1400
    bounds = ((lat_min, lat_max), (lon_min, lon_max))
    num_locations = 15
    closed_lots = create_closed_parking(bounds, num_locations)
    insert_parking_data(closed_lots)


if __name__ == "__main__":
    main()
