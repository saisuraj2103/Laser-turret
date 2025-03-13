#
#Developed by Vikrant Fernandes
#

import numpy as np
import cv2
import requests
import serial

#Serial object for communication with Arduino
arduino = serial.Serial(port='COM9', baudrate=9600, timeout=.1)
URL = "http://192.168.114.178"
AWB = True

# Face recognition and opencv setup
cap = cv2.VideoCapture(URL + ":81/stream")
#Capture from external USB webcam instead of the in-built webcam (shitty quality)
#cap = cv2.VideoCapture(0)

#kernel window for morphological operations
kernel = np.ones((5,5),np.uint8)

#resize the capture window to 640 x 480
ret = cap.set(3,640)
ret = cap.set(4,480)

#upper and lower limits for the color yellow in HSV color space
lower_yellow = np.array([14,178,0])
upper_yellow = np.array([69,255,255])
def set_resolution(url: str, index: int=1, verbose: bool=False):
    try:
        if verbose:
            resolutions = "10: UXGA(1600x1200)\n9: SXGA(1280x1024)\n8: XGA(1024x768)\n7: SVGA(800x600)\n6: VGA(640x480)\n5: CIF(400x296)\n4: QVGA(320x240)\n3: HQVGA(240x176)\n0: QQVGA(160x120)"
            print("available resolutions\n{}".format(resolutions))

        if index in [10, 9, 8, 7, 6, 5, 4, 3, 0]:
            requests.get(url + "/control?var=framesize&val={}".format(index))
        else:
            print("Wrong index")
    except:
        print("SET_RESOLUTION: something went wrong")

def set_quality(url: str, value: int=1, verbose: bool=False):
    try:
        if value >= 10 and value <=63:
            requests.get(url + "/control?var=quality&val={}".format(value))
    except:
        print("SET_QUALITY: something went wrong")

def set_awb(url: str, awb: int=1):
    try:
        awb = not awb
        requests.get(url + "/control?var=awb&val={}".format(1 if awb else 0))
    except:
        print("SET_QUALITY: something went wrong")
    return awb
#begin capture

set_resolution(URL, index=8)
while(True):
    ret, frame = cap.read()

    #Smooth the frame
    frame = cv2.GaussianBlur(frame,(11,11),0)

    #Convert to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    #Mask to extract just the yellow pixels
    mask = cv2.inRange(hsv,lower_yellow,upper_yellow)

    #morphological opening
    mask = cv2.erode(mask,kernel,iterations=2)
    mask = cv2.dilate(mask,kernel,iterations=2)

    #morphological closing
    mask = cv2.dilate(mask,kernel,iterations=2)
    mask = cv2.erode(mask,kernel,iterations=2)

    #Detect contours from the mask
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)[-2]

    if(len(cnts) > 0):
        #Contour with greatest area
        c = max(cnts,key=cv2.contourArea)
        #Radius and center pixel coordinate of the largest contour
        ((x,y),radius) = cv2.minEnclosingCircle(c)

        if radius > 5:
            #Draw an enclosing circle
            cv2.circle(frame,(int(x), int(y)), int(radius),(0, 255, 255), 2)

            #Draw a line from the center of the frame to the center of the contour
            cv2.line(frame,(320,240),(int(x), int(y)),(0, 0, 255), 1)
            #Reference line
            cv2.line(frame,(320,0),(320,480),(0,255,0),1)

            radius = int(radius)

            #distance of the 'x' coordinate from the center of the frame
            #wdith of frame is 640, hence 320
            length = 320-(int(x))
            lengthy = 320-(int(y))
            lengthy = lengthy-80
            print("x",length,"y",lengthy)
            if(length<10 and length>-10 and lengthy<10 and lengthy>-10):
                print("stop")
            if(length>10):
                arduino.write('2'.encode())
                print("right")
            if(length<-10):
                arduino.write('1'.encode())
                print("left")
            if(lengthy>10):
                arduino.write('3'.encode())
                print("up")
            if(lengthy<-10):
                arduino.write('4'.encode())
                print("down")
            #write distance and radius to Arduino through Serial Communication
            #ser.write(str(length))
            #ser.write('#')
            #ser.write(str(radius))
            #ser.write('/')

    #display the image
    cv2.imshow('frame',frame)
    #Mask image
    cv2.imshow('mask',mask)
    #Quit if user presses 'q'
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

#Release the capture
cap.release()
cv2.destroyAllWindows()
