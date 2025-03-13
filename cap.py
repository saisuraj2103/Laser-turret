import cv2
import requests
import serial

#arduino = serial.Serial(port='COM25', baudrate=9600, timeout=.1)
URL = "http://192.168.114.178"
AWB = True

# Face recognition and opencv setup

cap = cv2.VideoCapture(URL + ":81/stream")
# initialize the camera 
# If you have multiple camera connected with  
# current device, assign a value in cam_port  
# variable according to that 
cam_port = 0
cam = cv2.VideoCapture(cam_port) 
  
# reading the input using the camera 
result, image = cam.read() 
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
# If image will detected without any error,  
# show result 

set_resolution(URL, index=8)
ret, image = cap.read()
if result: 
  
    # showing result, it take frame name and image  
    # output 
    cv2.imshow("test", image) 
  
    # saving image in local storage 
    cv2.imwrite("test.jpg", image) 
  
    # If keyboard interrupt occurs, destroy image  
    # window 
    cv2.waitKey(0) 
    cv2.destroyWindow("test") 
  
# If captured image is corrupted, moving to else part 
else: 
    print("No image detected. Please! try again")