# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 09:24:08 2023

@author: joche
"""

import pyrealsense2 as rs
import numpy as np

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)

# Get the depth sensor's depth scale
depth_sensor = pipeline.get_active_profile().get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()

# Wait for a coherent pair of frames: depth and color
frames = pipeline.wait_for_frames()
depth_frame = frames.get_depth_frame()
color_frame = frames.get_color_frame()

# Convert images to numpy arrays
depth_image = np.asanyarray(depth_frame.get_data())
color_image = np.asanyarray(color_frame.get_data())

# Choose a pixel location to get depth information from
x = 135
y = 167

# Get the depth value of the pixel location
depth = depth_image[y, x] * depth_scale

# Calculate the real world coordinates of the pixel location
depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
depth_pixel = [x, y]
depth_point = rs.rs2_deproject_pixel_to_point(depth_intrin, depth_pixel, depth)
depth_point = np.array(depth_point)

# Print the depth value and real world coordinates of the pixel location
print(f"Depth value at pixel ({x}, {y}): {depth} meters")
print(f"Real world coordinates at pixel ({x}, {y}): {depth_point} meters")

# Stop streaming
pipeline.stop()
