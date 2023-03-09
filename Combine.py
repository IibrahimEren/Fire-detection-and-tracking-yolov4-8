import cv2
import numpy as np

from pyfirmata import Arduino, SERVO, OUTPUT
from time import sleep

################################
#           width 1280
# .--------------------------------.#
# .                                .#
# .                                .#
# .                                .#
# .           Our video            .#   height 720
# .                                .#
# .                                .#
# .                                .#
# .                                .#
# .--------------------------------.#
#################################

wCam, hCam = 1280, 720
# Setup For arduino

port = 'COM3'
# pin1 = 3  # X
# pin2 = 4  # Y
pinTest = 5  # >>> Test Pini LED
board = Arduino(port)
# board.digital[pin2].mode = SERVO
# board.digital[pin1].mode = SERVO
board.digital[pinTest].mode = OUTPUT


def rotateservo(pin, angle):
    board.digital[pin].write(angle)
    sleep(0.015)


# SET to start position
# rotateservo(pin1, 90)
# rotateservo(pin2, 90)

# capture the video from camera
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

face_cascade = cv2.CascadeClassifier('dnn_model\\face.xml')

while True:
    ret1, frames = cap.read()
    gray = cv2.cvtColor(frames, cv2.COLOR_BGR2GRAY)

    face = faces_cascade = face_cascade.detectMultiScale(gray, 1.1, 5)

    for (x, y, w, h) in face:
        cv2.rectangle(frames, (x, y), (x + w, y + h), (0, 0, 255), 2)


    # Vertical data is unnecessary for a moment
    # Center point of main frame
    center_pointX, center_pointY = wCam / 2, hCam / 2

    # Points of center rectangle
    point1 = int(center_pointX) - 100, int(center_pointY) - 100
    point2 = int(center_pointX) + 100, int(center_pointY) + 100
    cv2.rectangle(frames, point1, point2, (255, 0, 0), 3)

    for (x, y, w, h) in face:
        # Center point of rectangle
        regCenterX, regCenterY =(x+ (x + w))/ 2,(y + (y + h)) / 2
        # Algılanan nesnenin merkez noktasına uzaklığı
        merkeze_uzaklikX, merkeze_uzaklikY = regCenterX - center_pointX, regCenterY - center_pointY

        if regCenterX > (center_pointX - 100) and regCenterX < (center_pointX + 100):
            board.digital[pinTest].write(1)
        else:
            board.digital[pinTest].write(0)
            # rotateservo(pin1, #)
            # rotateservo(pin2, #)

    # ...
    # Flip the frames for mirror effect
    frames = cv2.flip(frames, 1)

    cv2.imshow('Output', frames)

    if cv2.waitKey(33) == 27:
        break

cv2.destroyAllWindows()
cap.release()
