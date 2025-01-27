import json
import torch
from PIL import Image
import os

def extract_and_standardize_bboxes(annotation_file, image_file):
    # Load the annotations
    with open(annotation_file, 'r') as f:
        annotations = json.load(f)
        
    # Get image dimensions
    image = Image.open(image_file)
    image_width, image_height = image.size

    # Find the image ID
    image_filename = os.path.basename(image_file)
    image_id = None
    for img in annotations['images']:
        if img['file_name'] == image_filename:
            image_id = img['id']
            break

    if image_id is None:
        raise ValueError(f"Image {image_filename} not found in annotations.")

    # Extract and standardize bounding boxes
    bboxes = []
    for ann in annotations['annotations']:
        if ann['image_id'] == image_id:
            segmentation = ann['segmentation'][0]  # Assuming polygon format
            standardized_bbox = [(x / image_width, y / image_height) for x, y in zip(segmentation[0::2], segmentation[1::2])]
            bboxes.append(standardized_bbox)

    # Convert to torch tensor
    bboxes_tensor = torch.tensor(bboxes, dtype=torch.float32)
    
    return bboxes_tensor

