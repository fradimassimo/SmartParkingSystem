from pymongo import MongoClient
import json
from data_generation.data_creation import create_parking_lots as cp

client = MongoClient("mongodb://mongodb:27017/")
db = client.parking_management

annotations_collection = db.annotations
parkings_collection = db.parkings

with open("/app/mongo/_annotations.coco.json", "r") as f:
    coco_data = json.load(f)

# create random parkings within boundaries
lat_min, lat_max = 46.0400, 46.1234
lon_min, lon_max = 11.0700, 11.1405
bounds = ((lat_min, lat_max), (lon_min, lon_max))
num_parkings = 120
parking_data = cp.create_street_parking(bounds, num_parkings)

parkings_collection.create_index("name", unique=True)

# Check if parkings already exist
if parkings_collection.count_documents({}) == 0:
    try:
        # insert the parkings into MongoDB
        parkings_collection.insert_many(parking_data)
        print("Parking data inserted successfully!")

    except Exception as e:
        print(f"An error occurred while inserting parkings' data: {e}")

# import annotations for each parking (note that original file has 418k entries, 
# we will only extract a selected few as most are redundant), code is NOT generalised
try:
    for annotation in coco_data["annotations"]:
        if annotation["image_id"] >= num_parkings:
            break
        annotation_doc = {
            "annotation_id": annotation["id"],
            "parking_id": annotation["image_id"] + 1,
            "bbox": annotation["bbox"],
            "segmentation": annotation.get("segmentation"),
            "area": annotation["area"]
        }
        # insert each annotation in MongoDB
        annotations_collection.create_index("annotation_id", unique=True)
        annotations_collection.insert_one(annotation_doc)

    print("Annotation Data inserted successfully!")

except Exception as e:
    print(f"An error occurred while inserting annotations' data: {e}")