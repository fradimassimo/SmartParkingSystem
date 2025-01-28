import json
import random
from collections import defaultdict
from sqlalchemy import create_engine
import pandas as pd
import sys

def aggregate_by_coordinates(record):
    """
    Aggregating data from spots sensors into closed parking lots based on locations,
    showing amount of occupied and free spots per parking lot.

    Args:
        record (list): sensors data generated every 20 seconds.

    Returns:
        list: list of dictionaries, each representing a parking lot.
    """
    parking_areas = defaultdict(lambda: {"occupied": 0, "free": 0})
    metadata = record[0]["metadata_time"]
    for spot in record:
        coordinates = (spot["location"]["latitude"], spot["location"]["longitude"])
        park_flag = spot["payload_fields_park_flag"]


        if park_flag == 1:  # Occupied
            parking_areas[coordinates]["occupied"] += 1
        else:  # Free
            parking_areas[coordinates]["free"] += 1

    result = []
    for coords, counts in parking_areas.items():
        result.append({

            "location": {"latitude":coords[0],"longitude":coords[1]},
            "occupied": counts["occupied"],
            "free": counts["free"],
            "metadata_time": metadata
        })

    return result


def merging(structure, aggregated_by_coords):
    """
       Merging aggregated by coordinates data with closed_parking structure.

       Args:
           structure (list): 15 closed parking lots data.
           aggregated_by_coords (list): aggregated by coordinates data.

       Returns:
           list: list of dictionaries, each representing a closed parking lot.
       """
    result = []

    for lot in aggregated_by_coords:
        lot_location = (lot["location"]["latitude"], lot["location"]["longitude"])
        match_found = False
        for good_lot in structure:
            good_lot_location = (good_lot["location"]["latitude"], good_lot["location"]["longitude"])
            if good_lot_location == lot_location:
                record = {
                    "parking_id": good_lot["parking_id"],
                    "name": good_lot["name"],
                    "capacity": good_lot["capacity"],
                    "metadata_time": lot["metadata_time"],
                    "location": lot["location"],
                    "vacancy": lot["free"],
                    "occupancy": lot["occupied"],
                }
                result.append(record)
                match_found = True
                break
        if not match_found:
            print(f"No matching location found for: {lot_location}")

    return result

def aggregator(structure, data):
    """"
    Combining the previous functions in this file in order to achieve a good data aggregation.

     Args:
           structure (list): 15 closed parking lots data.
           data (list): data coming from single sensors into closed parking lots.

       Returns:
           list: list of dictionaries, each representing a closed parking lot.
    """
    first_aggregation = aggregate_by_coordinates(data)
    result = merging(structure, first_aggregation)
    return result


def get_garage_structure():
    DATABASE_URI = "postgresql://admin:root@postgres:5432/smart-parking"
    engine = create_engine(DATABASE_URI)

    try:
        # Retrieve data from PostgreSQL
        query = """
               SELECT * FROM parkings WHERE parking_type = 'garage'
           """
        print("Fetching data from the database...")

        df = pd.read_sql(query, engine)

        if df.empty:
            print("No data found.")
            return []

        print("Data fetched successfully.")

        # Convert the DataFrame to a list of dictionaries
        data_as_dict = df.to_dict(orient="records")
        data_as_dict["location"] = {
            "latitude": data_as_dict["latitude"],
            "longitude": data_as_dict["longitude"]
        }

        return data_as_dict

    except Exception as e:
        print(f"Error retrieving parking data: {e}", file=sys.stderr)
        return []