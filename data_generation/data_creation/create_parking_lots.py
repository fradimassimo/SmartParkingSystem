import json
import random

def create_parking_lot_locations(bounds, num_locations, output_file):
    """ 
        bounds should be a tuple of tuples ((lat_min, lat_max), (lon_min, lon_max)) or a vector of tuples.
        num_locations (int) is the number of parking lot structures to generate.
        output_file (str) is the path to the JSON file where the data will be stored.
    """

    # we generate a set of coordinates within the boundaries of a rectangle
    coordinates = generate_coordinates_within_bounds(bounds, num_locations)

    # create a parking lot for each location
    parking_lots = []
    for i, coord in enumerate(coordinates, start=1):
        parking_lot = {
            "name": f"Park_{i:03d}",
            "location": {
                "latitude": coord[0],
                "longitude": coord[1]
            }
        }
        parking_lots.append(parking_lot)

    # export
    with open(output_file, "w") as file:
        json.dump(parking_lots, file, indent=4)

    print(f"Generated {num_locations} parking lot locations and saved to {output_file}.")


def create_street_parking(bounds, num_locations):
    """ 
        Used to generate street parking locations.
        bounds should be a tuple of tuples ((lat_min, lat_max), (lon_min, lon_max)) or a vector of tuples.
        num_locations (int) is the number of parking locations (i.e. group of parking spots) to generate.
        returns a vector of dictionaries as output.
    """

    # we generate a set of coordinates within the boundaries of a rectangle
    coordinates = generate_coordinates_within_bounds(bounds, num_locations)

    # create a parking lot for each location
    parking_lots = []
    for i, coord in enumerate(coordinates):
        parking_lot = {
            "id": i + 1,
            "name": f"Street_{i:03d}",
            "location": {
                "latitude": coord[0],
                "longitude": coord[1]
            },
            "opening_hours": f"{random.choice([0,7,8])}:00-{random.choice([18,20,21,22,24])}:00",
            "price_per_hour": random.choice([0, 0.8, 1.0, 1.5, 2.0, 2.5])
        }
        parking_lots.append(parking_lot)

    return parking_lots

def generate_coordinates_within_bounds(bounds, num_coordinates):
    """ bounds should be a tuple of tuples ((lat_min, lat_max), (lon_min, lon_max)) or a vector of tuples, 
    num_coordinates is an integer"""

    coordinates = []
    for _ in range(num_coordinates):
        lat = random.uniform(bounds[0][0], bounds[0][1])
        lon = random.uniform(bounds[1][0], bounds[1][1])
        coordinates.append((round(lat, 6), round(lon, 6)))
    return coordinates