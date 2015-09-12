import cv2
import urllib
import numpy as np
import itertools
import pyjsonrpc
import math


import time

X_SIZE=320
MAX_X=X_SIZE
MAX_Y=240
FPS=10

THRESHOLD = 1.0/3

LEFT_THRESHOLD = X_SIZE*THRESHOLD
RIGHT_THRESHOLD = X_SIZE*(1-THRESHOLD)

VIDEO_URL="http://192.168.42.1:8080/?action=stream"
CONTROL_URL = "http://192.168.42.1:8081/"


def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects

front_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
profile_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


def draw_str(dst, (x, y), s):
    cv2.putText(dst, s, (x+1, y+1), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness = 2, lineType=cv2.LINE_AA)
    cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), lineType=cv2.LINE_AA)

def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

def clock():
    return cv2.getTickCount() / cv2.getTickFrequency()

class RoombaBrain(object):
    SEARCH_FACE = 0
    PRE_TRACKING = 1
    TRACKING = 2

    WAIT_FOR_STABLE_TIME = 1.5

    def do_face_search(self,img,gray):
        t = clock()
        rects = detect(gray, front_cascade)

        if len(rects) == 0:
            rects = detect(gray, profile_cascade)

        if len(rects) > 0:
            self.control_client.stop()

        vis = img.copy()
        draw_rects(vis, rects, (0, 255, 0))
        dt = clock() - t

        draw_str(vis, (20, 20), 'time: %.1f ms' % (dt*1000))
        cv2.imshow('facedetect', vis)
        return rects

    def init_tracking(self,img,gray,rects):

        # set up the ROI for tracking
        x1, y1, x2, y2 = rects[0]
        c = x1
        r = y1
        w = (x2 - x1)
        delta_w = int(w * 0.5)
        c = max(0,c - int(delta_w/2))
        w = min(c + delta_w,MAX_X-c)
        h = int((y2 - y1)*1.5)
        r = min(r + 2*h,MAX_Y-h)
        self.initial_window = (c,r,w,h)
        self.track_window = (c,r,w,h)

        self.tracker.init(img, self.track_window)

    def do_tracking(self,img,gray):
        t = clock()
        ret,self.track_window = self.tracker.update(img)
        dt = clock() - t

        # Draw it on image
        x,y,w,h = self.track_window
        print self.track_window
        img2 = cv2.rectangle(img, (int(x),int(y)), (int(x+w),int(y+h)), 255,2)
        x,y,w,h = self.initial_window
        img2 = cv2.rectangle(img2, (x,y), (x+w,y+h), (0,255,0),2)

        draw_str(img2, (20, 20), 'time: %.1f ms' % (dt*1000))
        cv2.imshow('img2',img2)
        mean_x = x+(w/2)
        return

        #if mean_x < RIGHT_THRESHOLD:
        #    self.control_client.right()
        #elif mean_x > LEFT_THRESHOLD:
        #    self.control_client.left()
        #else:
        #    self.control_client.straight()

    def handle_roomba(self):
        self.control_client = pyjsonrpc.HttpClient( url = CONTROL_URL)
        self.mode = self.SEARCH_FACE

        self.tracker = cv2.Tracker_create("KCF")

        self.control_client.safe()

        self.control_client.slow_spin()

        stream=urllib.urlopen(VIDEO_URL)
        bytes = ""

        stablize_clock = 0
        skip_frames = 0

        for i in itertools.count(1):
            bytes+=stream.read(1024)
            a = bytes.find('\xff\xd8')
            b = bytes.find('\xff\xd9')
            if a!=-1 and b!=-1:
                jpg = bytes[a:b+2]
                bytes= bytes[b+2:]
                if skip_frames > 0:
                    skip_frames -= 1
                    print "Dropped frame"
                    continue
                t = clock()
                img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray = cv2.equalizeHist(gray)

                if self.mode == self.SEARCH_FACE:
                    rects = self.do_face_search(img,gray)
                    if len(rects):
                        stablize_clock = clock()
                        self.mode = self.PRE_TRACKING
                elif self.mode == self.PRE_TRACKING:
                    if clock() - stablize_clock >= self.WAIT_FOR_STABLE_TIME:
                        rects = self.do_face_search(img,gray)
                        if len(rects):
                            self.init_tracking(img,gray,rects)
                            self.mode = self.TRACKING
                        else:
                            self.control_client.slow_spin()
                            self.mode = self.SEARCH_FACE
                elif self.mode == self.TRACKING:
                    self.do_tracking(img,gray)
                else:
                    print "Unknown mode:",self.mode
                    self.mode = self.SEARCH_FACE
                dt = clock() - t
                skip_frames = math.ceil((dt - 1.0/FPS)*FPS)

            if cv2.waitKey(1) == 27:
                self.control_client.stop()
                break

def main():
    brain = RoombaBrain()
    brain.handle_roomba()

if __name__ == "__main__":
    main()
