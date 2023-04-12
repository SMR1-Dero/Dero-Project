# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 19:11:28 2023

@author: joche
"""

import pyrealsense2 as rs
import cv2
import numpy as np

def initialize_camera():
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)
    pipeline.start(config)
    return pipeline

def calibrate_camera(pipeline, chessboard_size=(9, 6), square_size=25):
    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2) * square_size

    objpoints = []
    imgpoints = []

    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()

        if not color_frame:
            continue

        color_image = np.asanyarray(color_frame.get_data())
        gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(gray_image, chessboard_size, None)

        if ret:
            objpoints.append(objp)
            imgpoints.append(corners)

            cv2.drawChessboardCorners(color_image, chessboard_size, corners, ret)
            cv2.imshow('Chessboard', color_image)
            cv2.waitKey(500)

            if len(objpoints) >= 10:
                ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray_image.shape[::-1], None, None)
                return mtx, dist

        cv2.imshow('Chessboard', color_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    pipeline.stop()
    cv2.destroyAllWindows()

def get_real_world_coordinate(pipeline, mtx, dist, x, y):
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()

    depth_image = np.asanyarray(depth_frame.get_data())
    color_image = np.zeros((480, 640, 3), dtype=np.uint8)
    undistorted_pixel = cv2.undistortPoints(np.array([[x, y]], dtype=np.float32), mtx, dist)
    depth_in_meters = depth_image[int(undistorted_pixel[0][0][1]), int(undistorted_pixel[0][0][0])]/1000
    depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
    uv_depth = np.concatenate((undistorted_pixel[0][0], [depth_in_meters]), axis=0).reshape(1, 3)

    point = rs.rs2_deproject_pixel_to_point(depth_intrin, uv_depth)

    return point

if __name__ == '__main__':
    pipeline = initialize_camera()
    mtx, dist = calibrate_camera(pipeline)
    point = get_real_world_coordinate(pipeline, mtx, dist, 320, 240)
    print(point)