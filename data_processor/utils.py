from forecast_sarima import get_predictions
import psycopg2

def get_festive_dates():
    return ["2025-01-01", "2025-01-06", "2025-04-20", "2025-04-21", "2025-05-01", "2025-04-25",
                    "2025-08-15","2025-12-08","2025-12-25","2025-12-26"]

def get_zone(lat, lon):
    zones = {
        "NORD": {"latitude": [46.100001, 46.1234], "longitude": [11.070001, 11.14]},
        "SUD": {"latitude": [46.04, 46.06], "longitude": [11.0070001, 11.14]},
        "EST": {"latitude": [46.060001, 46.10], "longitude": [11.110001, 11.14]},
        "OVEST": {"latitude": [46.060001, 46.10], "longitude": [11.070001, 11.10]},
        "CENTRO": {"latitude": [46.060001, 46.10], "longitude": [11.100001, 11.11]},
    }

    for zone, coords in zones.items():
        lat_min, lat_max = coords["latitude"]
        lon_min, lon_max = coords["longitude"]
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return zone
        
def get_zone_coordinates(zone):
    zones = {
        "NORD": {"latitude": [46.100001, 46.1234], "longitude": [11.070001, 11.14]},
        "SUD": {"latitude": [46.04, 46.06], "longitude": [11.0070001, 11.14]},
        "EST": {"latitude": [46.060001, 46.10], "longitude": [11.110001, 11.14]},
        "OVEST": {"latitude": [46.060001, 46.10], "longitude": [11.070001, 11.10]},
        "CENTRO": {"latitude": [46.060001, 46.10], "longitude": [11.100001, 11.11]},
    }

    if zone in zones:
        return zones[zone]
    else:
        raise ValueError(f"Invalid zone: {zone}. Valid zones are: {', '.join(zones.keys())}")
        
def calculate_new_price(expected_occupancy):
    if 0 <= expected_occupancy <= 0.20:
        return 0.8
    elif 0.20 < expected_occupancy <= 0.40:
        return 1.2
    elif 0.40 < expected_occupancy <= 0.60:
        return 1.5
    elif 0.60 < expected_occupancy <= 0.80:
        return 2.0
    else:
        return 2.2

def update_prices():
    """Adjust parking prices dynamically based on forecasted occupancy."""
    VALID_ZONES = ["NORD", "SUD", "CENTRO", "EST", "OVEST"]
    VALID_TYPES = ["street", "garage"]
    
    pg_conn = psycopg2.connect(
        dbname="smart-parking",
        user="admin",
        password="root",
        host="postgres",
        port="5432"
    )
    pg_cur = pg_conn.cursor()

    for zone in VALID_ZONES:
        for parking_type in VALID_TYPES:
            # get forecast for tomorrow
            mean_occupancy = get_predictions(zone, parking_type, daily=True)
            if mean_occupancy is None:
                print(f"Could not compute mean occupancy for zone {zone} and type {parking_type}.")
                continue

            # determine new prices
            price = calculate_new_price(mean_occupancy)

            # update postgres
            try:
                zone_coords = get_zone_coordinates(zone)

                # if the parking is free it stays free
                query = """
                    UPDATE parkings
                    SET price_per_hour = %s
                    WHERE latitude BETWEEN %s AND %s
                    AND longitude BETWEEN %s AND %s
                    AND parking_type = %s
                    AND price_per_hour > 0
                """

                params = (price,
                    zone_coords["latitude"][0], zone_coords["latitude"][1],
                    zone_coords["longitude"][0], zone_coords["longitude"][1],
                    parking_type,)
                pg_cur.execute(query, params)
                pg_conn.commit()

                print(f"Updated prices for {zone} {parking_type} parkings to {price:.2f}.")

            except Exception as e:
                print(f"Error updating prices for {zone} {parking_type}: {e}")

    pg_cur.close()
    pg_conn.close()

import psycopg2
from datetime import datetime, timedelta

def delete_old_entries(days: int):
    """Deletes entries from the occupancy_data table older than the specified number of days."""
    
    pg_conn = psycopg2.connect(
        dbname="smart-parking",
        user="admin",
        password="root",
        host="postgres",
        port="5432"
    )
    pg_cur = pg_conn.cursor()

    try:
        threshold_date = datetime.now() - timedelta(days=days)

        delete_query = """
            DELETE FROM occupancy_data
            WHERE timestamp < %s;
        """

        pg_cur.execute(delete_query, (threshold_date,))
        pg_conn.commit()
        print(f"Successfully deleted entries older than {days} days.")

    except Exception as e:
        print(f"Error deleting old entries: {e}")

    finally:
        pg_cur.close()
        pg_conn.close()
