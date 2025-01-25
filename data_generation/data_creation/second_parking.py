"""
File that manages the closed parking lots generation in order to create the base for our predictions.
Created from first_parking.py
"""

import json
import random
from datetime import timedelta



def read_parking_lots_from_json(input_file: str):
    """
    Reads parking lot data from a JSON file and returns a dictionary of parking lots.

    Args:
        input_file (str): The path to the JSON file containing parking lot data.

    Returns:
        dict: A dictionary where keys are parking lot names and values are their locations.
    """
    with open(input_file, "r") as file:
        parking_lots = json.load(file)

    return parking_lots



# generate parking data for all spots at a given time interval, give as input a vector of parkings in the same location
def generate_parking_data(closed_parking_lots, interval_minutes, time_window):
    """
        Takes as input an array of locations and generates occupancy data for each of them.
        time_window(tuple): a tuple of times (start_time, end_time)
    """
    start_time, end_time = time_window
    current_time = start_time
    data = []

    while current_time <= end_time:
        for parking_lot in closed_parking_lots:
            capacity = parking_lot["capacity"]
            park_flag = capacity - random.randint(0, capacity)
            # if the sensor malfunctions, then the spot is marked automatically as occupied

            record = {
                "deviceid": parking_lot["name"],
                "capacity": parking_lot["capacity"],
                "metadata_time": current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "location": parking_lot["location"],
                "availability": park_flag,
                "counter": random.randint(1, 1000),
                "active": 1
            }
            data.append(record)
        current_time += timedelta(minutes=interval_minutes)

    return data


# Main function to generate and save parking data to JSON file
def create_parking_dataset(input_file, output_file, interval_minutes: int, time_window: tuple):
    structures = read_parking_lots_from_json(input_file)
    all_parkings = []

    for struct in structures:
        all_parkings.append(struct)

    all_data = []
    for parking_set in all_parkings:
        all_data.extend(generate_parking_data(parking_set, interval_minutes, time_window))

    with open(output_file, 'w') as file:
        json.dump(all_data, file, indent=4)