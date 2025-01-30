import os
from datetime import datetime, timedelta

folder_path = "../images_prov/parking8"
current_time = datetime(2025, 1, 30, 23, 45)

time_interval = timedelta(minutes=15)
image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"}


image_files = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in image_extensions]
image_files.sort()

# Rename images
for image_file in image_files:
    # Create the new filename in the format YYYY-MM-DD_hh_mm_ss
    new_name = current_time.strftime("%Y-%m-%d_%H_%M_%S") + os.path.splitext(image_file)[1]

    old_path = os.path.join(folder_path, image_file)
    new_path = os.path.join(folder_path, new_name)

    os.rename(old_path, new_path)

    current_time -= time_interval

print("Renaming complete")