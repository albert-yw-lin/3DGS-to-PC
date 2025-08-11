#!/usr/bin/env python3
"""
Convert nuScenes-style extrinsics and intrinsics data to transforms.json format expected by the 3DGS-to-PC pipeline.

This script is specifically designed for nuScenes data format:

Extrinsics format:
- Files named {timestep}_{camera}.txt (e.g., 000_0.txt, 010_5.txt) containing 4x4 transformation matrices
- Timestep: 3-digit number (000, 001, ..., 010)
- Camera: single digit (0, 1, 2, 3, 4, 5)

Intrinsics format:
- Files named {camera}.txt (e.g., 0.txt, 1.txt, ..., 5.txt) 
- Each file contains: fx, fy, cx, cy (followed by zeros)

Images format:
- Files named {timestep}_{camera}.jpg matching the extrinsics naming
"""

import json
import numpy as np
import os
import argparse
import glob
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(filename)s:%(lineno)d - %(message)s',
    handlers=[
        logging.StreamHandler()  # Console output
    ]
)

logger = logging.getLogger(__name__)

def load_extrinsics_from_directory(extrinsics_dir):
    """Load all extrinsics files from a directory."""
    extrinsics = {}
    
    logger.info(f"Scanning extrinsics directory: {extrinsics_dir}")
    
    # List all .txt files in directory
    files = [f for f in os.listdir(extrinsics_dir) if f.endswith('.txt')]
    
    if not files:
        logger.error(f"No nuScenes extrinsics files found in {extrinsics_dir}")
        return extrinsics
    
    logger.info(f"Found {len(files)} potential extrinsics files")
    
    valid_files = 0
    for filename in files:
        # Parse nuScenes extrinsics filename: {timestep}_{camera_name}.txt
        filepath = os.path.join(extrinsics_dir, filename)
        matrix = np.loadtxt(filepath)
        
        if matrix.shape == (4, 4):
            # Store with string key format: "timestep_camera"
            extrinsics[filename[:-4]] = matrix # Remove .txt extension
            logger.info(f"Loaded extrinsics for {filename[:-4]}")
            valid_files += 1
        else:
            raise ValueError(f"Invalid extrinsics matrix shape in {filepath}, expected 4x4, got {matrix.shape}")
    
    logger.info(f"Successfully loaded {valid_files}/{len(files)} extrinsics files")
    return extrinsics

def load_intrinsics(intrinsics_path, camera_id="0", width=1600, height=900):
    """Load camera intrinsics for nuScenes format."""
    intrinsics_file = os.path.join(intrinsics_path, f"{camera_id}.txt")

    if not os.path.exists(intrinsics_file):
        logger.error(f"Intrinsics file not found: {intrinsics_file}")
        return None

    data = np.loadtxt(intrinsics_file)
    # nuScenes format: fx, fy, cx, cy followed by zeros
    if len(data) >= 4:
        fx, fy, cx, cy = data[0], data[1], data[2], data[3]
        logger.info(f"Loaded intrinsics from {os.path.basename(intrinsics_file)}: fx={fx:.2f}, fy={fy:.2f}, cx={cx:.2f}, cy={cy:.2f}")
        intrinsics = {
            'fx': fx, 'fy': fy, 'cx': cx, 'cy': cy,
            'width': width, 'height': height
        }
    else:
        raise ValueError(f"Insufficient intrinsics data in {intrinsics_file}, expected at least 4 values, got {len(data)}")

    return intrinsics

# def convert_to_nerf_format(transform_matrix):
#     """
#     Convert camera pose to NeRF format (similar to convert_sfm_pose_to_nerf in transform_dataloader.py).
#     This applies the coordinate system conversion commonly used in NeRF.
#     """
#     # Convert world-to-camera to camera-to-world
#     c2w = np.linalg.inv(transform_matrix)
    
#     # Apply coordinate system flip (NeRF convention)
#     flip_mat = np.array([
#         [1, 0, 0, 0],
#         [0, -1, 0, 0],
#         [0, 0, -1, 0],
#         [0, 0, 0, 1]
#     ])
    
#     return np.matmul(c2w, flip_mat)

def convert_nuscenes_to_transforms(extrinsics_path, intrinsics_path, output_path, 
                                  images_dir=None, image_ext='.jpg', 
                                  width=1600, height=900, camera_id="0",
                                  apply_nerf_transform=True, multi_camera=False):
    """
    Convert nuScenes extrinsics and intrinsics to transforms.json format.
    
    Args:
        extrinsics_path: Path to extrinsics directory containing {timestep}_{camera}.txt files
        intrinsics_path: Path to intrinsics directory containing {camera}.txt files
        output_path: Path to save the transforms.json file
        images_dir: Directory containing images (if different from "images/")
        image_ext: Image file extension (default: .jpg)
        width: Image width (default: 1600 for nuScenes)
        height: Image height (default: 900 for nuScenes)
        camera_id: Camera ID to use for intrinsics (default: "0") - only used if multi_camera=False
        apply_nerf_transform: Whether to apply NeRF coordinate system transformation
        multi_camera: If True, include all cameras with per-frame intrinsics; if False, single camera
    """
    
    # Load nuScenes extrinsics
    logger.info(f"Loading nuScenes extrinsics from: {extrinsics_path}")
    extrinsics = load_extrinsics_from_directory(extrinsics_path)
    
    if not extrinsics:
        logger.error("No extrinsics data loaded!")
        return False
    
    if multi_camera:
        # Load intrinsics for all cameras (0-5)
        logger.info(f"Multi-camera mode: Loading intrinsics for all cameras from: {intrinsics_path}")
        all_intrinsics = {}
        
        # Find all camera IDs from extrinsics
        camera_ids = set()
        for camera_name in extrinsics.keys():
            # Extract camera ID from filename like "000_0"
            parts = camera_name.split('_')
            if len(parts) == 2:
                camera_ids.add(parts[1])
        
        logger.info(f"Detected cameras: {sorted(camera_ids)}")
        
        # Load intrinsics for each camera
        for cam_id in sorted(camera_ids):
            logger.info(f"Loading intrinsics for camera {cam_id}")
            intrinsics = load_intrinsics(intrinsics_path, cam_id, width, height)
            all_intrinsics[cam_id] = intrinsics
        
        # Create transforms structure (no global intrinsics for multi-camera)
        transforms = {
            "frames": []
        }
        
        logger.info(f"Successfully loaded intrinsics for {len(camera_ids)} cameras")
        
    else:
        # Single camera mode - load intrinsics for specified camera
        raise NotImplementedError("Single camera mode is not implemented yet. Please set --multi_camera to True.")
    
    # Load first camera pose for alignment (same as nuScenes dataloader)
    camera_front_start = None
    if os.path.exists(extrinsics_path):
        # Find the first frame with camera 0 (front camera)
        first_frame_candidates = [name for name in sorted(extrinsics.keys()) if name.endswith('_0')]
        if first_frame_candidates:
            first_camera_name = first_frame_candidates[0]
            try:
                camera_front_start = extrinsics[first_camera_name].copy()
                logger.info(f"Applying camera alignment using first front camera pose: {first_camera_name}")
            except KeyError:
                logger.warning(f"Warning: Could not load first camera pose {first_camera_name}, skipping alignment")
        else:
            logger.warning("Warning: No front camera (camera 0) found, skipping alignment")

    # Process each camera frame
    for camera_name in sorted(extrinsics.keys()):
        transform_matrix = extrinsics[camera_name].copy()

        # Apply alignment if requested (same as nuScenes dataloader)
        if camera_front_start is not None:
            # Transform pose using inverse of first camera pose
            transform_matrix = np.matmul(np.linalg.inv(camera_front_start), transform_matrix)
        
        # Apply NeRF coordinate transformation if requested
        # if apply_nerf_transform:
        #     transform_matrix = convert_to_nerf_format(transform_matrix)
        
        # Determine image path
        if images_dir:
            image_path = f"{images_dir}/{camera_name}{image_ext}"
        else:
            image_path = f"images/{camera_name}{image_ext}"
        
        # Create frame entry
        frame = {
            "file_path": image_path,
            "transform_matrix": transform_matrix.tolist()
        }
        
        # Add per-frame intrinsics if multi-camera mode
        if multi_camera:
            # Extract camera ID from camera_name (e.g., "000_0" -> "0")
            parts = camera_name.split('_')
            assert len(parts) == 2, f"Unexpected camera name format: {camera_name}"
            cam_id = parts[1]
            assert cam_id in all_intrinsics
            cam_intrinsics = all_intrinsics[cam_id]
            frame["fl_x"] = cam_intrinsics['fx']
            frame["fl_y"] = cam_intrinsics['fy']
            frame["cx"] = cam_intrinsics['cx']
            frame["cy"] = cam_intrinsics['cy']
            frame["w"] = cam_intrinsics['width']
            frame["h"] = cam_intrinsics['height']
        
        transforms["frames"].append(frame)
    
    # Save the converted data
    logger.info(f"Saving transforms to: {output_path}")
    with open(output_path, 'w') as f:
        json.dump(transforms, f, indent=2)
    
    logger.info(f"✓ Successfully converted {len(extrinsics)} camera frames to {output_path}")
    
    if multi_camera:
        logger.info(f"Multi-camera mode: {len(camera_ids)} cameras with per-frame intrinsics")
        for cam_id in sorted(camera_ids):
            cam_intrinsics = all_intrinsics[cam_id]
            logger.info(f"  Camera {cam_id}: {cam_intrinsics['width']}x{cam_intrinsics['height']}, fx={cam_intrinsics['fx']:.2f}, fy={cam_intrinsics['fy']:.2f}")
    else:
        logger.info(f"Single camera mode: {transforms['w']}x{transforms['h']}")
        logger.info(f"Focal lengths: fx={transforms['fl_x']:.2f}, fy={transforms['fl_y']:.2f}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Convert nuScenes extrinsics and intrinsics data to transforms.json format.")
    
    # Required arguments
    parser.add_argument("--root", required=True, type=str, help="Path to root directory containing images and camera files")
    parser.add_argument("--extrinsics_dir", default="extrinsics", type=str, help="Path to extrinsics directory containing {timestep}_{camera}.txt files")
    parser.add_argument("--intrinsics_dir", default="intrinsics", type=str, help="Path to intrinsics directory containing {camera}.txt files")
    parser.add_argument("--output", required=True, type=str, help="Path to output transforms.json file")
    
    # Optional arguments
    parser.add_argument("--camera_id", type=str, default="0", help="Camera ID to use for intrinsics (default: '0') - only used in single camera mode")
    parser.add_argument("--multi_camera", action="store_true", help="Generate multi-camera transforms.json with per-frame intrinsics for all cameras")
    parser.add_argument("--images_dir", type=str, default="images", help="Directory containing images (default: 'images')")
    parser.add_argument("--image_ext", type=str, default=".jpg", help="Image file extension (default: .jpg)")
    parser.add_argument("--width", type=int, default=1600, help="Image width (default: 1600 for nuScenes)")
    parser.add_argument("--height", type=int, default=900, help="Image height (default: 900 for nuScenes)")
    parser.add_argument("--apply_nerf_transform", action="store_true", help="Apply NeRF coordinate system transformation")
    
    args = parser.parse_args()
    
    # Validate paths
    extrinsics_dir = os.path.join(args.root, args.extrinsics_dir)
    intrinsics_dir = os.path.join(args.root, args.intrinsics_dir)

    # Convert the data
    success = convert_nuscenes_to_transforms(
        extrinsics_path=extrinsics_dir,
        intrinsics_path=intrinsics_dir,
        output_path=args.output,
        images_dir=args.images_dir,
        image_ext=args.image_ext,
        width=args.width,
        height=args.height,
        camera_id=args.camera_id,
        apply_nerf_transform=args.apply_nerf_transform,
        multi_camera=args.multi_camera
    )
    
    if not success:
        exit(1)

if __name__ == "__main__":
    main()
