# Import the required modules
import dlib
import cv2
from imutils.object_detection import non_max_suppression
import argparse as ap
import numpy as np
import imutils
import threading

rpi = True

try:
   from picamera import PiCamera
except ImportError:
   rpi = False

if rpi:
    from picamera.array import PiRGBArray


class Vision_Subsystem(threading.Thread):

    def __init__(self, threadID, lat_value, logger, debug_mode=False):
        self.lat_value = lat_value
        self.logger = logger
        self.threadID = threadID
        self.debug_mode = debug_mode

        threading.Thread.__init__(self)


    def getInitialRoiPts(self, frame):

        print("Getting ROI points") 

        # Initialize the HOG descriptor/person detector with the default
        # Open CV 2 people detector
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        # Set up return values
        points = []

        # Get new frame width and height
        frameWidth = min(250, frame.shape[1])
        frameLength = (float(frameWidth)/frame.shape[1])*frame.shape[0]

        # Load the image and resize it to (1) reduce detection time
        # and (2) improve detection accuracy
        frame = imutils.resize(frame, width=frameWidth)
        orig = frame.copy()

        # Detect people in the image
        (rects, weights) = hog.detectMultiScale(frame, winStride=(4, 4),
            padding=(8, 8), scale=1.02)

        # Draw the original bounding boxes
        for (x, y, w, h) in rects:
            cv2.rectangle(orig, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Apply non-maxima suppression to the bounding boxes using a
        # fairly large overlap threshold to try to maintain overlapping
        # boxes that are still people
        rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
        pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)

        # Draw the final bounding boxes and return normalized points
        for (xA, yA, xB, yB) in pick:
            cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)
            subFactorX = 0.2*((xB-xA)/2)
            subFactorY = 0.2*((yA-yB)/2)
            points.append((float(xA+subFactorX)/frameWidth,float(yA-subFactorY)/frameLength,
                            float(xB-subFactorX)/frameWidth,float(yB+subFactorY)/frameLength))
            break

        cv2.imshow("After NMS", frame)

        return points

    def run(self, source=0, dispLoc=False):

        if rpi:
            cam = PiCamera()
            cam.resolution = (640, 480)
            cam.framerate = 8
            raw_capture = PiRGBArray(cam, size=(640, 480))
            camWidth = 640
            camHeight = 480
        
        else:
            # Create the VideoCapture object
            cam = cv2.VideoCapture(source)

            # Get the camera frame width and height
            camWidth = cam.get(3)
            camHeight = cam.get(4)

        # Determine the center coordinate
        frameCenterX = camWidth/2;
        frameCenterY = camHeight/2;

        # If raspberry pi, then get the frame iterator
        if rpi:
            frame_iter = cam.capture_continuous(raw_capture, format="bgr", use_video_port=True)

        print("Camera width: %s, height: %s" % (camWidth, camHeight))

        # If Camera Device is not opened, exit the program
        if not rpi and not cam.isOpened():
            print "Video device or file couldn't be opened"
            exit()

        # Human ROI points. Co-ordinates of the Human
        # to be tracked will be stored in this var.
        roiPts = []
        roiImg = 0

        while True:

            if rpi:
                retval = True
                img = frame_iter.next()
                img = img.array
                img.setflags(write=1)
                raw_capture.truncate(0)
            else:
                # Read from camera (get a frame)
                retval, img = cam.read()

            # Check successful frame capture
            if not retval:
                print "Cannot capture frame device"

            else:
                pts = []
                pts = self.getInitialRoiPts(img)

                if len(pts) != 0:
                    # Scale up the point according to the big frame
                    roiPts.append((int(pts[0][0]*camWidth), int(pts[0][1]*camHeight),
                                    int(pts[0][2]*camWidth), int(pts[0][3]*camHeight)))
                    roiImg = img
                    break
                cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
                cv2.imshow("Image", img)
        cv2.destroyWindow("Image")

        # Co-ordinates of objects to be tracked 
        # will be stored in a list named `points`

        if not roiPts:
            print "ERROR: No object to be tracked."
            exit()
        
        scaledImageRoi = img.copy()
        cv2.rectangle(scaledImageRoi, (roiPts[0][0], roiPts[0][1]), (roiPts[0][2], roiPts[0][3]), (0, 255, 0), 2)
        cv2.namedWindow("ScaledImageRoi", cv2.WINDOW_NORMAL)
        cv2.imshow("ScaledImageRoi", scaledImageRoi)

        # Initial co-ordinates of the object to be tracked 
        # Create the tracker object
        tracker = dlib.correlation_tracker()

        # Provide the tracker the initial position of the object
        tracker.start_track(img, dlib.rectangle(*roiPts[0]))

        while True:

            if rpi:
                retval = True
                img = frame_iter.next()
                img = img.array
                raw_capture.truncate(0)
            else:
                # Read from camera (get a frame)
                retval, img = cam.read()
            
            if not retval:
                print "Cannot capture frame device | CODE TERMINATING :("
                exit()

            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Update the tracker  
            tracker.update(img)

            # Get the position of the object, draw a 
            # bounding box around it and display it.
            rect = tracker.get_position()
            pt1 = (int(rect.left()), int(rect.top()))
            pt2 = (int(rect.right()), int(rect.bottom()))
            cv2.rectangle(img, pt1, pt2, (255, 255, 255), 3)

            # Calculate the lateral offset of the person
            # - Positive lateral offset indicates the center of the roi is to the right of the center
            # - Negative lateral offset indicates the center of the roi is to the left of the center
            roiCenterX = (rect.right() + rect.left())/2
            roiCenterY = (rect.top() + rect.bottom())/2
            lateralOffset = roiCenterX - frameCenterX
            normalizedLatOffset = lateralOffset/camWidth
            #print("ROI Center X is %s and the normalized lateral offset is %s" % (roiCenterX, normalizedLatOffset))

            # Add it to the control system queue
            if not self.debug_mode:
                self.lat_value[0] = normalizedLatOffset
        	#print("Sending!!!   --->" + str(normalizedLatOffset))


            # Show the ROI center on the image
            cv2.rectangle(img, (int(roiCenterX-10), int(roiCenterY+10)), 
                            (int(roiCenterX+10), int(roiCenterY-10)), (155, 155, 155), 5)

            #print "Object tracked at [{}, {}] \r".format(pt1, pt2),
            if dispLoc:
                loc = (int(rect.left()), int(rect.top()-20))
                txt = "Object tracked at [{}, {}]".format(pt1, pt2)
                cv2.putText(img, txt, loc , cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 1)
            cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
            cv2.imshow("Image", img)
            # Continue until the user presses ESC key
            if cv2.waitKey(1) == 27:
                break

        # Relase the VideoCapture object
        cam.release()

if __name__ == "__main__":
    # Run the vision system
    vision = Vision_Subsystem(1, None, None, True)
    vision.run(0, False)
