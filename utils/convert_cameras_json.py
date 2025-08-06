#!/usr/bin/env python3
"""
Convert cameras.json format to transforms.json format expected by the 3DGS-to-PC pipeline.
"""

import json
import numpy as np
import os
import argparse

def convert_cameras_to_transforms(input_path, output_path):
    """
    Convert cameras.json to transforms.json format.
    
    Args:
        input_path: Path to the input cameras.json file
        output_path: Path to save the converted transforms.json file
    """
    
    # Load the cameras data
    with open(input_path, 'r') as f:
        cameras_data = json.load(f)
    
    if not cameras_data:
        raise ValueError("Empty cameras data")
    
    # Get common intrinsics from first camera
    first_cam = cameras_data[0]
    
    # Create the transforms structure
    transforms = {
        "fl_x": first_cam["fx"],
        "fl_y": first_cam["fy"], 
        "w": first_cam["width"],
        "h": first_cam["height"],
        "frames": []
    }
    
    for cam in cameras_data:
        # Convert rotation matrix (3x3) and position (3x1) to 4x4 transform matrix
        rotation = np.array(cam["rotation"])  # 3x3 rotation matrix
        position = np.array(cam["position"])  # 3x1 position vector
        
        # Create 4x4 transform matrix
        transform_matrix = np.eye(4)
        transform_matrix[:3, :3] = rotation
        transform_matrix[:3, 3] = position
        
        # Add frame entry
        frame = {
            "file_path": f"images/{cam['img_name']}.jpg",  # Assuming .jpg extension
            "transform_matrix": transform_matrix.tolist()
        }
        
        transforms["frames"].append(frame)
    
    # Save the converted data
    with open(output_path, 'w') as f:
        json.dump(transforms, f, indent=2)
    
    print(f"Converted {len(cameras_data)} cameras from {input_path} to {output_path}")
    print(f"Image resolution: {transforms['w']}x{transforms['h']}")
    print(f"Focal lengths: fx={transforms['fl_x']:.2f}, fy={transforms['fl_y']:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert cameras.json to transforms.json format.")
    parser.add_argument("--input_file", required=True, help="Path to input cameras.json")
    parser.add_argument("--output_file", required=True, help="Path to output transforms.json")
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    
    convert_cameras_to_transforms(input_file, output_file)
