import torch, os, requests
from parking_detection.models.rcnn import RCNN
from parking_detection.utils import transforms
# from parking_detection.utils import visualize as vis 
import torchvision
from pymongo import MongoClient
import time
from datetime import datetime

def get_model():
    model = RCNN()
    weights_path = 'weights.pt'

    try:
        model.load_state_dict(torch.load(weights_path, map_location='cpu', weights_only=True))
        return model

    except Exception as e:
        print(f"Error loading model weights: {e}")
        return None

def standardize_bboxes(segmentation, image_width, image_height):
    bboxes = []
    for bbox in segmentation:
        standardized_bbox = [(x / image_width, y / image_height) for x, y in zip(bbox[0][0::2], bbox[0][1::2])]
        bboxes.append(standardized_bbox)

    # Convert to torch tensor
    bboxes_tensor = torch.tensor(bboxes, dtype=torch.float32)

    return bboxes_tensor

def detect_parking_image(image_path, model, parking_id):
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
                    "occupied": occupancy[0],
                    "vacant": occupancy[1]
                }
                parking_counts.append(parking_dict)

    return parking_counts


def get_bounding_boxes(parking_id):
    """Fetch bounding boxes (annotations) from MongoDB using parking_id."""
    try:
        # Connect to MongoDB (Docker container uses "mongodb" as the hostname)
        client = MongoClient("mongodb://admin:root@mongodb:27017/")
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

    
def main():
    folder_path = "/app/images"
    model = get_model()

    for folder_name in os.listdir(folder_path):
        # check every folder (should be in the name parkingXXX, with XXX being the parking id)
        if folder_name.startswith("parking") and folder_name[7:].isdigit():
            parking_id = int(folder_name[7:]) 
            new_folder_path = os.path.join(folder_path, folder_name)

            print(f"Processing folder: {folder_name} (Parking ID: {parking_id})")
            parking_data = detect_parking_folder(new_folder_path, parking_id, model)
            print("Processed parking data:")
            for entry in parking_data:
                print(entry)

    

# Entry point
if __name__ == "__main__":
    main()