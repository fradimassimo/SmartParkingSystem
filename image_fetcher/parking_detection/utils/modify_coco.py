import os
import json
from datetime import datetime

def read_image_names_from_directories(base_path):
    parking_images = {}
    parking_directories = ['parking1', 'parking2', 'parking3']

    for parking in parking_directories:
        dir_path = os.path.join(base_path, parking)
        if os.path.isdir(dir_path):
            parking_images[parking] = os.listdir(dir_path)
        else:
            print(f"Directory {dir_path} does not exist.")
    
    return parking_images

def update_coco_json_with_parking_field(coco_json_path, parking_images):
    with open(coco_json_path, 'r') as f:
        coco_data = json.load(f)

    for image_info in coco_data['images']:
        image_name = image_info['file_name']
        for parking, images in parking_images.items():
            if image_name in images:
                image_info['parking'] = parking
                break
    
    with open(coco_json_path, 'w') as f:
        json.dump(coco_data, f)

    print(f"Updated {coco_json_path} with parking information.")

def count_parking_occurrences(coco_json_path):
    with open(coco_json_path, 'r') as f:
        coco_data = json.load(f)

    parking_counts = {
        'parking1': 0,
        'parking2': 0,
        'parking3': 0
    }

    for image_info in coco_data['images']:
        if 'parking' in image_info:
            parking = image_info['parking']
            if parking in parking_counts:
                parking_counts[parking] += 1

    return parking_counts


def read_image_names_from_directories(base_path):
    parking_images = {}
    parking_directories = ['parking1', 'parking2', 'parking3']

    for parking in parking_directories:
        dir_path = os.path.join(base_path, parking)
        if os.path.isdir(dir_path):
            parking_images[parking] = os.listdir(dir_path)
        else:
            print(f"Directory {dir_path} does not exist.")
    
    return parking_images

def extract_date_from_filename(filename):
    # Extract the date and time from the filename (format: YYYY-MM-DD_HH_MM_SS)
    date_str = filename.split('_jpg')[0]
    try:
        date_captured = datetime.strptime(date_str, '%Y-%m-%d_%H_%M_%S').isoformat()
    except ValueError as e:
        print(f"Error parsing date from filename {filename}: {e}")
        date_captured = None
    return date_captured

def update_coco_json_with_date_captured(coco_json_path, parking_images):
    with open(coco_json_path, 'r') as f:
        coco_data = json.load(f)

    for image_info in coco_data['images']:
        image_name = image_info['file_name']
        for parking, images in parking_images.items():
            if image_name in images:
                date_captured = extract_date_from_filename(image_name)
                if date_captured:
                    image_info['date_captured'] = date_captured
                break
    
    with open(coco_json_path, 'w') as f:
        json.dump(coco_data, f)

    print(f"Updated {coco_json_path} with date_captured information.")

