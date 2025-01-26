import json
import random
from collections import defaultdict


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
                    "deviceid": good_lot["name"],
                    "capacity": good_lot["capacity"],
                    "metadata_time": lot["metadata_time"],
                    "location": lot["location"],
                    "availability": good_lot["capacity"] - lot["occupied"],
                    "counter": random.randint(1, 1000),
                    "active": 1
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

