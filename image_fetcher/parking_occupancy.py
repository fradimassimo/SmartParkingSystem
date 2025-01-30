import torch, os
from parking_detection.models.rcnn import RCNN
from parking_detection.utils import transforms
# from parking_detection.utils import visualize as vis 
import torchvision
from pymongo import MongoClient
import time
from datetime import datetime
import psycopg2
import requests
from sqlalchemy import create_engine
import pandas as pd
import os
import shutil

def get_model():
    """Loads the model weights"""

    model = RCNN()
    weights_path = 'weights.pt'
    
    if not os.path.exists(weights_path):
        r = requests.get('https://pub-e8bbdcbe8f6243b2a9933704a9b1d8bc.r2.dev/parking%2FRCNN_128_square_gopro.pt')  
    with open(weights_path, 'wb') as f:
        f.write(r.content)

    try:
        model.load_state_dict(torch.load(weights_path, map_location='cpu', weights_only=True))
        return model

    except Exception as e:
        print(f"Error loading model weights: {e}")
        return None

def standardize_bboxes(segmentation, image_width, image_height):
    """Standardize bounding boxes to the range [0, 1], the range that the CNN requires."""
    bboxes = []
    for bbox in segmentation:
        standardized_bbox = [(x / image_width, y / image_height) for x, y in zip(bbox[0][0::2], bbox[0][1::2])]
        bboxes.append(standardized_bbox)

    # Convert to torch tensor
    bboxes_tensor = torch.tensor(bboxes, dtype=torch.float32)

    return bboxes_tensor

def detect_parking_image(image_path, model, parking_id):
    """ Detect parking occupancy in a single image and return the results as a list. """
    image = torchvision.io.read_image(image_path)

    # here goes the import
    rois = get_bounding_boxes(parking_id)

    image_height, image_width = image.shape[1], image.shape[2]
    rois = standardize_bboxes(rois, image_width, image_height)

    image = transforms.preprocess(image)

    with torch.no_grad():
        class_logits = model(image, rois)
        class_scores = class_logits.softmax(1)[:, 1]

    occupied_count = (class_scores > 0.5).sum().item()
    vacant_count = (class_scores <= 0.5).sum().item()

    return [occupied_count, vacant_count]

def detect_parking_folder(folder_path, parking_id, model):
    """ Detect parking occupancy in a folder of images and return the results as a list of dictionaries. """
    parking_counts = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')):
                image_path = os.path.join(root, file)
                occupancy = detect_parking_image(image_path, model, parking_id)

                timestamp = get_image_timestamp(image_path)

                # create a dictionary for each image
                parking_dict = {
                    "parking_id": parking_id,
                    "timestamp": timestamp,
                    "occupancy": occupancy[0],
                    "vacancy": occupancy[1]
                }
                parking_counts.append(parking_dict)

    return parking_counts


def get_bounding_boxes(parking_id):
    """Fetch bounding boxes (annotations) from MongoDB using parking_id."""
    try:
        # Connect to MongoDB (Docker container uses "mongodb" as the hostname)
        client = MongoClient("mongodb://mongodb:27017/")
        db = client.parking_management  # Database name
        annotations_collection = db.annotations  # Collection name

        # Query MongoDB for annotations with the given parking_id
        annotations = list(annotations_collection.find({"parking_id": parking_id}, {"segmentation": 1, "_id": 0}))

        # Extract bounding boxes (list of bboxes)
        bounding_boxes = [annotation["segmentation"] for annotation in annotations]

        return bounding_boxes

    except Exception as e:
        print(f"Error fetching bounding boxes: {e}")
        return []
    


def get_image_timestamp(image_path):

    try:
        # Extract the file name without extension
        file_name = os.path.basename(image_path)
        name_without_extension = os.path.splitext(file_name)[0]

        try:
            timestamp = datetime.strptime(name_without_extension[:19], "%Y-%m-%d_%H_%M_%S")
            return timestamp.isoformat()  # Return in ISO 8601 format
        
        except ValueError:
            # If the name does not match the timestamp pattern, use the file's metadata
            pass

        date_creation = time.ctime(os.path.getmtime(image_path))
        date_creation = datetime.strptime(date_creation, "%a %b %d %H:%M:%S %Y")
        date_creation = date_creation.strftime("%Y-%m-%dT%H:%M:%SZ")

    except Exception as e:
        print(f"Error fetching timestamp for {image_path}: {e}")
        return None

    return date_creation


def insert_data_to_db(parking_data):
    """Insert parking data on PostreSQL using SQLAlchemy."""
    
    engine = create_engine("postgresql://admin:root@postgres:5432/smart-parking")

    try:
        df = pd.DataFrame(parking_data)
        df.to_sql('occupancy_data', con=engine, if_exists='append', index=False, method='multi')
    
    except Exception as e:
        print(f"An error occurred while inserting occupancy data: {e}")
    
    finally:
        engine.dispose() 

def delete_processed_images(folder_path):
    """Delete all files in the specified folder while keeping the directory structure"""

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


def main():
    folder_path = "/app/images"
    model = get_model()
    processed_folders = []

    try:
        for folder_name in os.listdir(folder_path):
            if folder_name.startswith("parking") and folder_name[7:].isdigit():
                parking_id = int(folder_name[7:]) 
                new_folder_path = os.path.join(folder_path, folder_name)
                processed_folders.append(new_folder_path)

                print(f"Processing folder: {folder_name} (Parking ID: {parking_id})")
                parking_data = detect_parking_folder(new_folder_path, parking_id, model)
                print("Processed parking data, Inserting into DB")
                insert_data_to_db(parking_data)
                print("Data inserted successfully.")

        """
        for folder in processed_folders:
            print(f"Cleaning up: {folder}")
            delete_processed_images(folder)
            print(f"Successfully deleted images in {folder}")
        """

    except Exception as e:
        print(f"Operation failed: {e}")
        print("No images were deleted due to processing errors")
        raise 

if __name__ == "__main__":
    main()
