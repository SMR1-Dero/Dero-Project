import cv2
import cv2.aruco as aruco
import numpy as np
import copy

print(f'cv2 version: {cv2.__version__}')
print(f'cv2.aruco verion: {aruco.__version__}')

original_image = cv2.imread("/Users/martreumer/Desktop/markers.jpg")
aruco_dictionary = aruco.getPredifinedDictionary(aruco.DICT_4x4_250)

cv2.imshow("Original input image", original_image)

def generateArucoMarker(dictionary, id=123):
    return aruco.drawMarker(dictionary, id, 200)

def calibrateRobotPosition(image):
    copy_image = copy.deepcopy(image)

    # Define the Aruco dictionary and parameters and create the detector with them
    dictionary = aruco.getPredefinedDictionary(cv2.aruco.DICT_4x4_250)
    parameters =  aruco.DetectorParameters()
    detector = aruco.ArucoDetector(dictionary, parameters)

    # Detect the Aruco markers in the image
    corners, ids, rejectedImgPoints = detector.detectMarkers(copy_image)

    print(f'Ids: {ids}')

    # Draw the detected Aruco markers on the image
    aruco.drawDetectedMarkers(copy_image, corners, ids)

    center = np.zeros((2,2))

    # # Find the center of each detected marker
    # for i in range(2):
    #     c = corners[i][0]
    #     x = (c[0][0] + c[1][0] + c[2][0] + c[3][0]) / 4
    #     y = (c[0][1] + c[1][1] + c[2][1] + c[3][1]) / 4
    #     center[i] = (int(x), int(y))

    return center, copy_image

# center_of_robot, image_with_marker = calibrateRobotPosition(original_image)

# print(f'Coordinates of center {center_of_robot[0]}')
# cv2.imshow("Picture with markers", image_with_marker)

cv2.imshow("generated marker", generateArucoMarker(aruco_dictionary))

while True:
    # Exit if the user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()