# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 13:03:11 2023

@author: joche
"""

import pyrealsense2 as rs

# Create a pipeline object
pipeline = rs.pipeline()

# Configure the pipeline to stream depth frames with the serial number filter
config = rs.config()
config.enable_stream(rs.stream.depth, rs.format.z16, 30)
serial_number = "839512061465"" # Replace this with the serial number of your camera
config.enable_device(serial_number)

# Start streaming with the configured pipeline
pipeline.start(config)

# Retrieve the serial number of the connected camera
device = pipeline.get_active_profile().get_device()
serial_number = device.get_info(rs.camera_info.serial_number)
print(f"The serial number of the connected camera is: {serial_number}")

# Stop the pipeline to release resources
pipeline.stop()