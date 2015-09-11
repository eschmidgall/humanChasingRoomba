import cv2
import urllib
import numpy as np
import itertools
import pyjsonrpc


import time



VIDEO_URL="http://192.168.42.1:8080/?action=stream"
CONTROL_URL = "http://192.168.42.1:8081/"


def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)
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


def handle_roomba():
    control_client = pyjsonrpc.HttpClient( url = CONTROL_URL)

    control_client.slow_spin()

    stream=urllib.urlopen(VIDEO_URL)
    bytes = ""

    for i in itertools.count(1):
        bytes+=stream.read(1024)
        a = bytes.find('\xff\xd8')
        b = bytes.find('\xff\xd9')
        if a!=-1 and b!=-1:
            jpg = bytes[a:b+2]
            bytes= bytes[b+2:]
            img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            t = clock()
            rects = detect(gray, front_cascade)

            if len(rects) == 0:
                rects = detect(gray, profile_cascade)

            if len(rects) > 0:
                control_client.stop()

            vis = img.copy()
            draw_rects(vis, rects, (0, 255, 0))
            dt = clock() - t

            draw_str(vis, (20, 20), 'time: %.1f ms' % (dt*1000))
            cv2.imshow('facedetect', vis)
        
            if cv2.waitKey(1) == 27:
                break

if __name__ == "__main__":
    handle_roomba()
