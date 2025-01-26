import os
from datetime import datetime, timedelta

# Path to the folder containing images
folder_path = "../images_prov/parking8"

# Start date and time
current_time = datetime(2025, 1, 30, 23, 45)

# Time interval (15 minutes)
time_interval = timedelta(minutes=15)

# Supported image extensions
image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"}

# Get all image files in the folder
image_files = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in image_extensions]

# Sort files to ensure consistent renaming order
image_files.sort()

# Rename images
for image_file in image_files:
    # Create the new filename in the format YYYY-MM-DD_hh_mm_ss
    new_name = current_time.strftime("%Y-%m-%d_%H_%M_%S") + os.path.splitext(image_file)[1]

    # Full paths
    old_path = os.path.join(folder_path, image_file)
    new_path = os.path.join(folder_path, new_name)

    # Rename the file
    os.rename(old_path, new_path)

    # Decrement the timestamp
    current_time -= time_interval

print("Renaming complete!")