import cv2
import numpy as np
import copy

# Read in the camera footage
# original_image_unsized = cv2.imread("/Users/martreumer/Desktop/kokos.jpeg")
original_image_unsized = cv2.imread("/Users/martreumer/Desktop/inputimage.jpeg")
# original_image_unsized = cv2.imread("/Users/martreumer/Desktop/TomaatDetc.jpg")

original_image = cv2.resize(original_image_unsized, (480,640))

def nothing(x):
    pass

def makeframe(colorMask, cannyDebug):
    # Create windows
    cv2.namedWindow("Gray image")
    cv2.namedWindow("Original image with rectangles")
    # cv2.namedWindow("Image with Harris corners")

    if colorMask:
        cv2.namedWindow("Mask image")
        cv2.namedWindow("HSV colors")
        # Create trackbars
        cv2.createTrackbar('hsvunder1','HSV colors',92,180,nothing)
        cv2.createTrackbar('hsvunder2','HSV colors',153,255,nothing)
        cv2.createTrackbar('hsvunder3','HSV colors',21,255,nothing)
        cv2.createTrackbar('hsvupper1','HSV colors',130,180,nothing)
        cv2.createTrackbar('hsvupper2','HSV colors',255,255,nothing)
        cv2.createTrackbar('hsvupper3','HSV colors',255,255,nothing)
        # Voor kokos: 92,153,21 130,255,255

    if cannyDebug:
        cv2.namedWindow("Canny edges")
        # Create trackbars
        cv2.createTrackbar('Threshold1','Canny edges', 472,1000,nothing)
        cv2.createTrackbar('Threshold2','Canny edges', 514,1000,nothing)
    
def readtrackbarHSV():
    hsvunder1 = cv2.getTrackbarPos('hsvunder1','HSV colors')
    hsvunder2 = cv2.getTrackbarPos('hsvunder2','HSV colors')
    hsvunder3 = cv2.getTrackbarPos('hsvunder3','HSV colors')
    hsvupper1 = cv2.getTrackbarPos('hsvupper1','HSV colors')
    hsvupper2 = cv2.getTrackbarPos('hsvupper2','HSV colors')
    hsvupper3 = cv2.getTrackbarPos('hsvupper3','HSV colors')
    
    return hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3

def readtrackbarCanny():
    threshold1 = cv2.getTrackbarPos('Threshold1','Canny edges')
    threshold2 = cv2.getTrackbarPos('Threshold2','Canny edges')

    return threshold1,threshold2

def image_edits(image,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3,threshold1,threshold2):    
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    #set the lower and upper bounds for the HSV
    lower_hsv = np.array([hsvunder1,hsvunder2,hsvunder3])
    upper_hsv = np.array([hsvupper1,hsvupper2,hsvupper3])

    #create a mask for the colour using inRange function
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    masked_image = cv2.bitwise_and(image, image, mask=mask)
    
    # Apply pre-processing to enhance edges
    gray = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)

    # Equalize the histogram to account for reflections
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl1 = clahe.apply(gray)
    equalize_hist = cv2.equalizeHist(gray)
    edited_gray = np.hstack((gray, equalize_hist, cl1))

    edges = cv2.Canny(equalize_hist, threshold1, threshold2)

    # # Find corners
    # dst = cv2.cornerHarris(gray,2,3,0.04)
    #     #result is dilated for marking the corners, not important
    # dst = cv2.dilate(dst,None)
    #     #place corners in copy of original image
    # corner_image = copy.deepcopy(image)
    # corner_image[dst>0.01*dst.max()]=[0,0,255]

    # Find contours in the image
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return masked_image,equalize_hist,edges,contours

def drawHSV(hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3):
    # create an image with white background
    image = np.zeros((256, 512, 3), np.uint8)

    # convert the HSV value to an RGB value
    hsv_under = np.array([hsvunder1, hsvunder2, hsvunder3], np.uint8)
    under_color = cv2.cvtColor(np.array([[hsv_under]]), cv2.COLOR_HSV2BGR)[0][0]
    # print("under_color = ")
    # print(under_color)
    
    hsv_upper = np.array([hsvupper1, hsvupper2, hsvupper3], np.uint8)
    upper_color = cv2.cvtColor(np.array([[hsv_upper]]), cv2.COLOR_HSV2BGR)[0][0]
    # print("upper_color")
    # print(upper_color)

    # draw the first rectangle
    rect1 = (0, 0, image.shape[1] // 2, image.shape[0])
    cv2.rectangle(image, rect1, (int(under_color[0]),int(under_color[1]),int(under_color[2])), -1)

    # draw the second rectangle
    rect2 = (image.shape[1] // 2, 0, image.shape[1] // 2, image.shape[0])
    cv2.rectangle(image, rect2, (int(upper_color[0]),int(upper_color[1]),int(upper_color[2])), -1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    text1 = f'H: {hsvunder1} S: {hsvunder2} V: {hsvunder3}'
    text2 = f'H: {hsvupper1} S: {hsvupper2} V: {hsvupper3}'
    cv2.putText(image, text1, (20, 50), font, 0.65, (50, 50, 50), 2, cv2.LINE_AA)
    cv2.putText(image, text2, (image.shape[1] // 2 + 20, 50), font, 0.65, (50, 50, 50), 2, cv2.LINE_AA)

    return image

def main(colorMask=False, cannyDebug=False):
    
    makeframe(colorMask, cannyDebug)

    while True:
        copy_of_orignal = copy.deepcopy(original_image)

        if colorMask:
            #read info from trackbars
            hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3=readtrackbarHSV()
            hsv_image = drawHSV(hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3)
        else:
            hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3=0,0,0,0,0,0
        
        if cannyDebug:
            threshold1, threshold2 = readtrackbarCanny()

        else:
            threshold1, threshold2 = 100, 200

        mask_image,gray_image,edges_image,contours = image_edits(original_image,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3,threshold1,threshold2)

        if contours is not None:
            # Loop through all contours
            for cnt in contours:
                if (cv2.contourArea(cnt) > 100):
                    # Approximate the contour to a polygon
                    approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True)
                    
                    # If the polygon has 4 sides, it is likely a rectangle
                    # if len(approx) == 4:
                        # Calculate the center of the rectangle
                    M = cv2.moments(cnt)

                    if int(M['m10']) != 0:
                        cx = int(M['m10']/M['m00'])
                        cy = int(M['m01']/M['m00'])
                    
                        # Draw a circle on the center of the rectangle and draw the contour
                        cv2.circle(copy_of_orignal, (cx, cy), 5, (0, 0, 255), -1)
                        cv2.drawContours(copy_of_orignal, [approx], -1, (0, 255, 0), 4)

        # Display the resulting image with circles indicating the centers of the rectangles
        cv2.imshow('Gray image', gray_image)

        if cannyDebug:
            font = cv2.FONT_HERSHEY_SIMPLEX
            text1 = f'Threshold1: {threshold1}'
            text2 = f'Threshold2: {threshold2}'
            cv2.putText(edges_image, text1, (0, 25), font, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(edges_image, text2, (0, 75), font, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow('Canny edges', edges_image)
        cv2.imshow('Original image with rectangles', copy_of_orignal)
        # cv2.imshow('Image with Harris corners', corner_image)

        if colorMask:
            cv2.imshow('Mask image', mask_image)
            cv2.imshow('HSV colors', hsv_image)

        # Exit if the user presses 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

main(colorMask=True, cannyDebug=True)