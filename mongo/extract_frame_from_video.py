import cv2

def get_first_frame(video_path, output_image_path):
    """Extract the first frame from a video and save it as an image."""

    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        print("Error: Could not open video.")
    else:
        success, frame = video.read()
        
        if success:
            cv2.imwrite(output_image_path, frame)
            print(f"First frame saved as {output_image_path}")
        else:
            print("Error: Could not read the first frame.")

    video.release()