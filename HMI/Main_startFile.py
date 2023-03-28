import cv2
import pyrealsense2 as rs
import numpy as np
import copy
from Vegetables_V4 import *
vegetabledict = {
    "id": "1_8",
    "product_name": "Tomaat",
    "product_image": "https://github.com/ItsJarik/CobotHMI/blob/main/Tomaten.png?raw=true",
    "product_package": "Curry Madras",
    "crateNumber": "2",
    "isActive": "on",
    "product_shape": "Round",
    "product_HSVRange": [0,80,80,255,255,255],
    "product_minSize": "",
    "product_maxSize": ""
}

def main(debug=False):
    # Initialize Camera Intel Realsense
    pipeline1,pipeline2=initizalize_rs()
    #create trackbar and images
    camera=2
    #calibrate_camera(pipeline2,camera)
    makeframe()
    while True:
        #read info from trackbars
        hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3=readtrackbar()
        #Use filters and circle detection to get center coordinate
        image_with_points,pickup_coordinates,gray_image,crop,original_color_frame,camera,pipeline,place=getpoint(pipeline1,pipeline2,vegetabledict)
        if pickup_coordinates != []:
            point=make_3D_point(pickup_coordinates[0][0][0]+crop[2], pickup_coordinates[0][0][1]+crop[0],pipeline,camera)
            print("3D Point in robot arm coordinates:", point,"and the following place:",place)
            #print(coor[0][0][0])
            #show edited and original frame with contours and center
            original_with_points=draw_original(original_color_frame, pickup_coordinates,crop[2],crop[0])
            if debug:
                cv2.imshow("Origineel frame", original_with_points)
        if debug:
            cv2.imshow("bewerkt frame", image_with_points)
            cv2.imshow("Grijs frame",gray_image)
        cv2.waitKey(100)
        key = cv2.waitKey(1)
        if key == 27:  # ESC
            break
        #maxheight,pos=find_high_points(depth)
    key = cv2.waitKey(0)
        #if key == 27:
            #        break
    cv2.destroyAllWindows()
    # Stop streaming
    pipeline1.stop()
    pipeline2.stop()
main(debug=True)