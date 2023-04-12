import numpy as np
import cv2
import pyrealsense2 as rs

def calibrate_realsense_camera(pattern_size=(18, 12), square_size=2):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    """Calibrates RealSense camera using a chessboard pattern"""

    # Start streaming
    pipeline.start(config)

    # Create arrays to store object points and image points from all the images
    objpoints = []  # 3D points in real world space
    imgpoints = []  # 2D points in image plane

    try:
        while True:
            # Wait for a coherent pair of frames: depth and color
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue

            # Convert images to numpy arrays
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # Find chessboard corners
            gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)

            # If corners are found, add object points and image points
            if ret == True:
                objp = np.zeros((pattern_size[0]*pattern_size[1], 3), np.float32)
                objp[:,:2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2) * square_size
                objpoints.append(objp)

                # Draw and display the corners
                cv2.drawChessboardCorners(color_image, pattern_size, corners, ret)
                print(objpoints)
                cv2.imshow('Calibration', color_image)
                cv2.waitKey(500)

            # If enough images have been captured, perform camera calibration
            if len(objpoints) >= 10:
                # Perform camera calibration
                ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

                # Stop streaming
                pipeline.stop()

                # Return the camera matrix and distortion coefficients
                return mtx, dist

            # Display the frames
            cv2.imshow('RealSense', color_image)
            cv2.waitKey(1)

    finally:
        pipeline.stop()
 
calibrate_realsense_camera()
pipeline.stop()