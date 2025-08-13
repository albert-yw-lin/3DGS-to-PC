python gauss_to_pc.py \
    --input_path data/nuscenes0/omnire_75_124/Background_gaussians.ply \
    --output_path data/nuscenes0/omnire_75_124/3dgs_pc_trans.ply \
    --transform_path data/nuscenes0/transforms.json \
    --clean_pointcloud \
    --bounding_box_min -20 -3 -20 \
    --bounding_box_max 20 3 20 \
    --num_points 100000000 \
    --colour_quality original \
    --surface_distance_std 0.05 \
    --min_opacity 0.2 \


# !!!!!!NOTE:  before running this script, make sure line 302-304 in transform_dataloader.py is {{{{{{{{{{{{{{commented out}}}}}}}}}}}}}:
# #print("WARNING: Applying camera direction flip transform for 3DGS pre-trained bicycle model.")
# #print("         If this is not needed for your model, comment out the flip_camera_direction() call below.")
# #transform = flip_camera_direction(transform)