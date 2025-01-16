import json
import utils

def create_parking_lot_locations(bounds, num_locations, output_file):
    """ 
        bounds should be a tuple of tuples ((lat_min, lat_max), (lon_min, lon_max)) or a vector of tuples.
        num_locations (int) is the number of parking lot locations to generate.
        output_file (str) is the path to the JSON file where the data will be stored.
    """

    # we generate a set of coordinates within the boundaries of a rectangle
    coordinates = utils.generate_coordinates_within_bounds(bounds, num_locations)

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
        print(parking_lot)

    # export
    with open(output_file, "w") as file:
        json.dump(parking_lots, file, indent=4)

    print(f"Generated {num_locations} parking lot locations and saved to {output_file}.")
