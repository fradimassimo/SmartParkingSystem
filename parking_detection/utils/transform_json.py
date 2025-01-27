import json, torch
from PIL import Image

def ultralytics_to_tensor(json_path):
    """
    Converts a JSON file containing points into a PyTorch tensor.
    
    Args:
        json_path (str): Path to the JSON file.
    
    Returns:
        torch.Tensor: A tensor of shape (N, 4, 2), where N is the number of bounding boxes.
    """
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Extract points and convert to tensor
    tensor_data = []
    for entry in data:
        points = entry['points']  # Assumes 'points' contains the bounding box
        tensor_data.append(points)
    
    return torch.tensor(tensor_data, dtype=torch.float32)


def normalize_tensor_with_image(tensor, image_path):
    """
    Normalizes tensor values between 0 and 1 based on image dimensions.
    
    Args:
        tensor (torch.Tensor): A tensor of shape (N, 4, 2) containing bounding box coordinates.
        image_path (str): Path to the image file.
    
    Returns:
        torch.Tensor: A normalized tensor.
    """
    # Load the image to get its dimensions
    with Image.open(image_path) as img:
        image_width, image_height = img.size
    
    # Normalize the tensor
    tensor[:, :, 0] /= image_width  # Normalize x-coordinates
    tensor[:, :, 1] /= image_height  # Normalize y-coordinates
    return tensor