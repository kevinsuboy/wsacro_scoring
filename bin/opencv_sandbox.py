#!/usr/bin/env python

# import cv2 as cv
# img = cv.imread("../../fireworks_unedited.png")

# cv.imshow("Display window", img)
# k = cv.waitKey(0) # Wait for a keystroke in the window

#  ffmpeg -i gopro_small.MP4 -c:v copy -c:a aac -strict experimental output.MP4

import numpy as np
import cv2 as cv
import code
# cap = cv.VideoCapture('../../GH010420.mp4')
# cap = cv.VideoCapture('../../GX010612.mp4')
# cap = cv.VideoCapture('../../15-07-49-717.mp4')
cap = cv.VideoCapture('../../output.mp4')
# expectedFrameCount = cap.get(cv::CAP_PROP_FRAME_COUNT)
i = 0
# code.interact(local=locals())
try:
    while cap.isOpened():
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        # breakpoint()
        i+=1
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        if i%50 == 0:
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            cv.imshow('frame', gray)
        if cv.waitKey(1) == ord('q'):
            break
except:
    breakpoint()
cap.release()
cv.destroyAllWindows()