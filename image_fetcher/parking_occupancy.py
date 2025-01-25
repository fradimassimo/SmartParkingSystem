import torch, os, requests
from parking_detection.models.rcnn import RCNN
from parking_detection.utils import transforms
# from parking_detection.utils import visualize as vis 
import torchvision
from pymongo import MongoClient
import datetime

def get_model():
    model = RCNN()
    weights_path = 'weights.pt'

    try:
        model.load_state_dict(torch.load(weights_path, map_location='cpu', weights_only=True))
        return model

    except Exception as e:
        print(f"Error loading model weights: {e}")
        return None
    
    

def detect_parking_image(image_path, model, parking_id):
    image = torchvision.io.read_image(image_path)

    # here goes the import
    rois = get_bounding_boxes(parking_id)

    image = transforms.preprocess(image)

    with torch.no_grad():
        class_logits = model(image, rois)
        class_scores = class_logits.softmax(1)[:, 1]

    occupied_count = (class_scores > 0.5).sum().item()
    vacant_count = (class_scores <= 0.5).sum().item()

    return [occupied_count, vacant_count]

def detect_parking_folder(folder_path, parking_id, model):
    parking_counts = []
    print(f"Files in folder {folder_path}: {os.listdir(folder_path)}")
    for root, _, files in os.walk(folder_path):
        for i, file in enumerate(files):
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
    """Get the timestamp (date created) of an image."""
    try:
        # Get the modification time of the file
        timestamp = os.path.getmtime(image_path)
        # Convert to a readable format (e.g., ISO 8601)
        readable_timestamp = datetime.utcfromtimestamp(timestamp).isoformat()
        return readable_timestamp
    except Exception as e:
        print(f"Error fetching timestamp for {image_path}: {e}")
        return None
    
def main():
    # Define paths and parameters
    folder_path = "/app/images"  # Docker-mounted volume path for images
    parking_id = 8  # Example parking ID
    model = get_model()  # Load the model

    # Process images in the folder
    parking_data = detect_parking_folder(folder_path, parking_id, model)

    # Print or handle the processed data
    print("Processed parking data:")
    for entry in parking_data:
        print(entry)

# Entry point
if __name__ == "__main__":
    main()