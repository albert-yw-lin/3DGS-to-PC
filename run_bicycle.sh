# python gauss_to_pc.py \
#     --input_path data/bicycle_3dgstopc_test/point_cloud/iteration_30000/point_cloud.ply \
#     --output_path data/bicycle_3dgstopc_test/3dgs_pc.ply \
#     --transform_path data/bicycle_3dgstopc_test/transforms.json \

# for clean, bboxed pc:
python gauss_to_pc.py \
    --input_path data/bicycle_3dgstopc_test/point_cloud/iteration_30000/point_cloud.ply \
    --output_path data/bicycle_3dgstopc_test/3dgs_pc.ply \
    --transform_path data/bicycle_3dgstopc_test/transforms.json \
    --bounding_box_min -2 -2 -1 \
    --bounding_box_max 2 2 2 \
    --clean_pointcloud \
    --surface_distance_std 0.01 

# !!!!!!NOTE:  before running this script, make sure line 302-304 in transform_dataloader.py is {{{{{{{{{{{{{{uncommented}}}}}}}}}}}}}:
# #print("WARNING: Applying camera direction flip transform for 3DGS pre-trained bicycle model.")
# #print("         If this is not needed for your model, comment out the flip_camera_direction() call below.")
# #transform = flip_camera_direction(transform)