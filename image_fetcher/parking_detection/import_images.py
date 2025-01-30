from roboflow import Roboflow
rf = Roboflow(api_key="ukQ4cG4ARhtXKcDFzcZx")
project = rf.workspace("restofpklot").project("restpklots")
version = project.version(1)
dataset = version.download("coco")

import utils.modify_coco as mc

base_path = 'path/to/images'
coco_json_path = 'path/to/json'

# Modify the coco.json file to include parking_ids for each image.
parking_images = mc.read_image_names_from_directories(base_path)
mc.update_coco_json_with_parking_field(coco_json_path, parking_images)

parking_counts = mc.count_parking_occurrences(coco_json_path)
print(parking_counts)

parking_images = mc.read_image_names_from_directories(base_path)
mc.update_coco_json_with_date_captured(coco_json_path, parking_images)