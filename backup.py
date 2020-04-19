import numpy as np
import cv2

def nothing(x):
    pass

# Create a black control, a window
img = np.zeros((1,300,3), np.uint8)
cv2.namedWindow('control')

# create trackbars for color change
cv2.createTrackbar('R','control',0,255,nothing)
cv2.createTrackbar('G','control',0,255,nothing)
cv2.createTrackbar('B','control',0,255,nothing)

# create switch for ON/OFF functionality
switch = 'OFF / ON'
cv2.createTrackbar(switch, 'control',0,1,nothing)

while(1):
    cv2.imshow('control',img)
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

    # get current positions of four trackbars
    r = cv2.getTrackbarPos('R','control')
    g = cv2.getTrackbarPos('G','control')
    b = cv2.getTrackbarPos('B','control')
    s = cv2.getTrackbarPos(switch,'control')

    if s == 0:
        img[:] = 0
    else:
        img[:] = [b,g,r]

cv2.destroyAllWindows()