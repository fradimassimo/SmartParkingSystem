import boto3
import os

# initializing the client on S3
s3_client = boto3.client("s3")

BUCKET_NAME = "smart-parking-images"
FOLDER_NAME = "parkings/"

def upload_to_s3(file_path, bucket_name, folder_name):
    file_name = os.path.basename(file_path)
    s3_key = f"{folder_name}{file_name}"

    try:
        s3_client.upload_file(file_path, bucket_name, s3_key)
        print(f"Uploaded {file_name} to {bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Error uploading {file_name}: {e}")
