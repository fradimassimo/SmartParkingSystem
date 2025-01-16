import json
import random
from datetime import datetime, timedelta
import utils

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


# generate parking structure
def generate_parking_structure(parking_structure: dict, num_parkings: int):
    """
        Used to generate all the spots inside a certain location
    """

    parking_spots = []
    for i in range(num_parkings):
        parking_spot = {
            "device_id": f"spot_{i+1:04d}",
            "latitude": parking_structure["location"]["latitude"],
            "longitude": parking_structure["location"]["longitude"]
        }
        parking_spots.append(parking_spot)
    return parking_spots

# generate parking data for all spots at a given time interval, give as input a vector of parkings in the same location
def generate_parking_data(parking_spots, interval_minutes, time_window):
    """
        Takes as input an array of locations and generates occupancy data for each of them.
        time_window(tuple): a tuple of times (start_time, end_time)
    """
    start_time, end_time = time_window
    current_time = start_time
    data = []

    while current_time <= end_time:
        for spot in parking_spots:
            park_flag = random.choice([0, 1])
            # if the sensor malfunctions, then the spot is marked automatically as occupied
            battery_percent = 100 if random.random() > 0.005 else 0
            if battery_percent == 0:
                park_flag = 0

            record = {
                "deviceid": spot["device_id"],
                "metadata_time": current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "location": {
                    "latitude": spot["latitude"],
                    "longitude": spot["longitude"]
                },
                "payload_fields_park_flag": park_flag,
                "payload_fields_battery_percent": battery_percent,
                "payload_fields_low_voltage": "False",
                "counter": random.randint(1,1000),
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
        all_parkings.append(generate_parking_structure(struct, random.randint(50,600)))
        
    all_data = []
    for parking_set in all_parkings:
        all_data.extend(generate_parking_data(parking_set, interval_minutes, time_window))


    with open(output_file, 'w') as file:
        json.dump(all_data, file, indent=4)
