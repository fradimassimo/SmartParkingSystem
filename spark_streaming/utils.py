import json
import random
from collections import defaultdict
from sqlalchemy import create_engine
import pandas as pd
import sys

def aggregate_by_ids(record):
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
        ids = (spot["parking_id"])
        park_flag = spot["payload_fields_park_flag"]


        if park_flag == 1:  # Occupied
            parking_areas[ids]["occupied"] += 1
        else:  # Free
            parking_areas[ids]["free"] += 1

    result = []
    for id, counts in parking_areas.items():
        result.append({

            "parking_id": id,
            "occupied": counts["occupied"],
            "free": counts["free"],
            "metadata_time": metadata
        })

    return result


def merging(structure, aggregated_by_ids):
    """
       Merging aggregated by coordinates data with closed_parking structure.

       Args:
           structure (list): 15 closed parking lots data.
           aggregated_by_ids (list): aggregated by coordinates data.

       Returns:
           list: list of dictionaries, each representing a closed parking lot.
       """
    result = []

    for lot in aggregated_by_ids:
        lot_id = (lot["parking_id"])
        match_found = False
        for good_lot in structure:
            good_lot_id = (good_lot["parking_id"])
            if good_lot_id == lot_id:
                record = {
                    "parking_id": good_lot["parking_id"],
                    "name": good_lot["name"],
                    "metadata_time": lot["metadata_time"],
                    "location": good_lot["location"],
                    "vacancy": lot["free"],
                    "occupancy": lot["occupied"],
                }
                result.append(record)
                match_found = True
                break
        if not match_found:
            print(f"No matching id found for: {lot_id}")

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
    first_aggregation = aggregate_by_ids(data)
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

        data_as_dict = []

        # iterate on the dataframe and create a dictionary for each row
        for _, row in df.iterrows():
            row_dict = row.to_dict() 
            data_as_dict.append(row_dict)

        print("Data fetched successfully.")

        return data_as_dict
    except Exception as e:
        print(f"Error retrieving parking data: {e}", file=sys.stderr)

