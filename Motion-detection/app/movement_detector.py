import numpy as np
import cv2 
import time
import socket

print("App starting")
SAVE_OUTPUT= False
UDP_IP = "192.168.1.243"
UDP_PORT = 5005
CAPTURE_SIZE = (600,600)

print("Creating socket")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_SIZE[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_SIZE[1])
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"RGB3"))

print("Capturing test frame")
ret, frame = cap.read()


# https://learnopencv.com/creating-a-virtual-pen-and-eraser-with-opencv/
print("Creating Background subtractor and BlobDetector")
fgbg = cv2.createBackgroundSubtractorMOG2()

# https://learnopencv.com/blob-detection-using-opencv-python-c/
params = cv2.SimpleBlobDetector_Params()

# Change thresholds
params.minThreshold = 10
params.maxThreshold = 200

# Filter by Area.
params.filterByArea = True
params.minArea = 1500

# Filter by Circularity
params.filterByCircularity = False
params.minCircularity = 0.1

# Filter by Convexity
params.filterByConvexity = False
params.minConvexity = 0.87

# Filter by Inertia
params.filterByInertia = False
params.minInertiaRatio = 0.01

detector = cv2.SimpleBlobDetector_create(params)
frame_counter=0
print("Starting")
while True:
    ret, frame = cap.read()
    if frame is None:
        time.sleep(0.1)
        continue
    frame_counter+=1
    fgmask = fgbg.apply(frame)
    keypoints = detector.detect(fgmask)
    print(keypoints)
    if SAVE_OUTPUT:
        im_with_keypoints = cv2.drawKeypoints(frame, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        cv2.imwrite("/app/output/img_"+str(frame_counter)+".jpg", im_with_keypoints)
    if len(keypoints)!=0:
        for keypoint in keypoints:
            message = "{}, {}, {}".format(keypoint.pt[0],keypoint.pt[1],keypoint.size)
            sock.sendto(bytes(message, "utf-8"), (UDP_IP, UDP_PORT))
