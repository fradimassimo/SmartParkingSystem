import json

def merging(structure, aggregated_by_coords):
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
                    "vacancy": lot["availability"],
                    "occupancy": lot["capacity"]-lot["availability"],
                }
                result.append(record)
                match_found = True
                break
        if not match_found:
            print(f"No matching location found for: {lot_location}")

    return result


def read_parking_lots_from_json(input_file: str):
    with open(input_file, "r") as file:
        parking_lots = json.load(file)

    return parking_lots


def correct(input_file, input_file2, output_file):

    structures = read_parking_lots_from_json(input_file)
    aggregated = read_parking_lots_from_json(input_file2)
    all_data = merging(structures, aggregated)

    with open(output_file, 'w') as file:
        json.dump(all_data, file, indent=4)

input_file = r"C:\Users\franc\Documents\smart_parking_system\spark_streaming\corrected_closed_parking_structures.json"
input_file2 = r"C:\Users\franc\Documents\smart_parking_system\data_generation\data\closed_lots_aggregated_data.json"
output_file = r"C:\Users\franc\Documents\smart_parking_system\spark_streaming\corrected_base_data.json"
correct(input_file, input_file2, output_file)

