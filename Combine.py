import cv2
import numpy as np

from pyfirmata import Arduino, SERVO
from time import sleep

################################
wCam, hCam = 1280, 960
###### Setup For arduino

port = 'COM3'
pin1 = 3  # X
pin2 = 4  # Y
board = Arduino(port)
board.digital[pin2].mode = SERVO
board.digital[pin1].mode = SERVO

def rotateservo(pin,angle):
    board.digital[pin].write(angle)
    sleep(0.015)

    #SET to start position
rotateservo(pin1,90)
rotateservo(pin2,90)

# for i in range(0, 181):
#     rotateservo(pin1, i)
#     rotateservo(pin2, i)
#
# for i in range(180, -1,-1):
#     rotateservo(pin1, i)
#     rotateservo(pin2, i)
#######
#capture the video from camera
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0


k = np.ones((3, 3), np.uint8)
t0 = cap.read()[1]
t1 = cap.read()[1]

face_cascade = cv2.CascadeClassifier('dnn_model\\face.xml')

while True:
    ret1, frames = cap.read()
    gray = cv2.cvtColor(frames, cv2.COLOR_BGR2GRAY)

    # gray_flip =cv2.flip(gray,-1)
    # cv2.imshow("gray",gray_flip)

    face = faces_cascade = face_cascade.detectMultiScale(gray, 1.1, 5)



    for (x, y, w, h) in face:
        cv2.rectangle(frames, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # frames = cv2.flip(frames, -1)
    frames = cv2.flip(frames,1)


    # for (x, y, w, h) in face:
    #     cv2.putText(frames, "face", (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 3, (200, 0, 50), 2)

    d = cv2.absdiff(t1, t0)

    ## Servonun 0/180 derece aralığı için aldığımız görüntünün piksel miktarı orantısı hesabı >> Yeniden hesaplanması gerekiyor
    anglex = x * 180 / wCam
    angley = y * 180 / hCam
    ## Merkezden uzaklığına göre halledilecek bir dahakinde

    rotateservo(pin1, angley)
    rotateservo(pin2, anglex)

    t2 = frames
    cv2.imshow('Output', t2)
    t0 = t1
    t1 = cap.read()[1]

    if cv2.waitKey(33) == 27:
        break

cv2.destroyAllWindows()
cap.release()