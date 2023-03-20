# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 14:35:26 2023

@author: joche
"""

import pyrealsense2 as rs
from realsense_depth import *
dc = DepthCamera()
ret, depth_frame, color_frame = dc.get_frame()

pipeline = rs.pipeline()

 # Configure streams
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

    # Start streaming
pipeline.start(config)
    
def convert_depth_to_phys_coord_using_realsense(x, y, depth, cameraInfo):
  _intrinsics = rs.intrinsics()
  _intrinsics.width = cameraInfo.width
  _intrinsics.height = cameraInfo.height
  _intrinsics.ppx = cameraInfo.K[2]
  _intrinsics.ppy = cameraInfo.K[5]
  _intrinsics.fx = cameraInfo.K[0]
  _intrinsics.fy = cameraInfo.K[4]
  #_intrinsics.model = cameraInfo.distortion_model
  _intrinsics.model  = rs.distortion.none
  _intrinsics.coeffs = [i for i in cameraInfo.D]
  result = rs.rs2_deproject_pixel_to_point(_intrinsics, [x, y], depth)
  #result[0]: right, result[1]: down, result[2]: forward
  return result[2], -result[0], -result[1]

_intrinsics = rs.intrinsics()
print(pyrealsense2.intrinsics())
convert_depth_to_phys_coord_using_realsense(1,1,1,dc)
sensor_msgs/CameraInfo