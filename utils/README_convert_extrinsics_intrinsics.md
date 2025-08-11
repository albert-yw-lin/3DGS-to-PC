# Extrinsics/Intrinsics to JSON Converter

This script converts camera extrinsics and intrinsics data to the `transforms.json` format expected by the 3DGS-to-PC pipeline.

## Usage

### Basic Usage

```bash
python convert_extrinsics_intrinsics_to_json.py \
    --extrinsics /path/to/extrinsics/directory \
    --intrinsics /path/to/intrinsics.txt \
    --output transforms.json
```

### Alternative Format (Separate Rotation/Translation)

```bash
python convert_extrinsics_intrinsics_to_json.py \
    --rotation_dir /path/to/rotations \
    --translation_dir /path/to/translations \
    --intrinsics /path/to/intrinsics.txt \
    --output transforms.json
```

## Supported Data Formats

### Extrinsics
1. **4x4 transformation matrices**: Each camera has a text file containing a 4x4 matrix
2. **3x4 matrices**: Each camera has a text file with [R|t] format (3x4 matrix)
3. **Separate rotation/translation**: Rotation matrices (3x3) and translation vectors (3x1) in separate directories

### Intrinsics
1. **Single file with 6 values**: `fx fy cx cy width height`
2. **K matrix format**: 3x3 camera calibration matrix
3. **4 values**: `fx fy cx cy` (requires --width and --height arguments)

## Arguments

- `--extrinsics`: Path to directory containing extrinsics files
- `--intrinsics`: Path to intrinsics file or directory
- `--output`: Path for output transforms.json file
- `--rotation_dir`: Directory with rotation matrices (alternative to --extrinsics)
- `--translation_dir`: Directory with translation vectors (alternative to --extrinsics)
- `--images_dir`: Image directory path (default: "images")
- `--image_ext`: Image file extension (default: ".jpg")
- `--width`: Image width (if not in intrinsics file)
- `--height`: Image height (if not in intrinsics file)
- `--no_nerf_transform`: Skip NeRF coordinate system transformation

## Example File Structures

### Extrinsics Directory
```
extrinsics/
├── cam_001.txt    # 4x4 or 3x4 transformation matrix
├── cam_002.txt
└── cam_003.txt
```

### Separate Rotation/Translation
```
rotations/
├── cam_001.txt    # 3x3 rotation matrix
├── cam_002.txt
└── cam_003.txt

translations/
├── cam_001.txt    # 3x1 translation vector
├── cam_002.txt
└── cam_003.txt
```

### Intrinsics File
```
# Format 1: fx fy cx cy width height
1234.5 1234.5 960.0 540.0 1920 1080

# Format 2: K matrix (3x3)
1234.5    0.0  960.0
   0.0 1234.5  540.0
   0.0    0.0    1.0
```

## Coordinate System

By default, the script applies a NeRF-style coordinate system transformation (similar to `convert_sfm_pose_to_nerf` in the original codebase). Use `--no_nerf_transform` to skip this if your data is already in the correct coordinate system.

## Output Format

The script generates a `transforms.json` file compatible with the 3DGS-to-PC pipeline:

```json
{
  "fl_x": 1234.5,
  "fl_y": 1234.5,
  "w": 1920,
  "h": 1080,
  "frames": [
    {
      "file_path": "images/cam_001.jpg",
      "transform_matrix": [
        [0.xxx, 0.xxx, 0.xxx, 0.xxx],
        [0.xxx, 0.xxx, 0.xxx, 0.xxx],
        [0.xxx, 0.xxx, 0.xxx, 0.xxx],
        [0.0, 0.0, 0.0, 1.0]
      ]
    }
  ]
}
```
