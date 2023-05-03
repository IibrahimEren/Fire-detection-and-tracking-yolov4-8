# _*_ coding: utf-8 _*_

import cv2

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
# Aleve yönelik hareket yapıldıktan sonra görüş açısında çıkan alev için tarama fonksiyonu yazılması gerekir

wCam, hCam = 1280, 720

port = 'COM3'
pin1 = 3  # X
pin2 = 4  # Y
pinTest = 5  # >>> Test Pini LED
pinPipe = 6  # For water motor
board = Arduino(port)
MAX_artis = 45

start_posX = 90
start_posY = 0
newX = start_posX  # for the first frame
newY = start_posY

board.digital[pin2].mode = SERVO  # Y
board.digital[pin1].mode = SERVO  # X
board.digital[pinTest].mode = OUTPUT  # LED
board.digital[pinPipe].mode = OUTPUT  # MOTOR

# SET relay to start position
board.digital[pinPipe].write(0)  # bir olduğunda kapalı bir şekilde başlatıyor
board.digital[pinTest].write(0)


# kameradan alınan verinin hangi piksel üzerinde olduğuna göre hesaplanmış
# şekilde hareket ettiren fonksiyon
def rotateservo(pin, angle):
    board.digital[pin].write(angle)
    sleep(0.015)


# SET servos to start position
rotateservo(pin1, start_posX)
rotateservo(pin2, start_posY)


# Hedef görmediği anlarda etrafı taraması için fonksiyon
def scanArea(pin1, current):
    for i in range(current, 180):
        for i in range(180, 0):
            board.digital[pin1].write(i)
            # Hedef gördüğü an döngüden çıkması için if bloğu
            if len(face) != 0:
                break


# capture the video from camera
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

face_cascade = cv2.CascadeClassifier('dnn_model\\face.xml')

while True:
    # while True:
    #     value = input("bla")
    #     rotateservo(pin1,value)

    ret1, frames = cap.read()
    gray = cv2.cvtColor(frames, cv2.COLOR_BGR2GRAY)

    face = faces_cascade = face_cascade.detectMultiScale(gray, 1.1, 15)
    # Eğer algılanan görüntüde yüz/ateş yok ise tarama fonksiyonu çalışsın
    if len(face) == 0:
        scanArea(pin1, newX)

    for (x, y, w, h) in face:
        cv2.rectangle(frames, (x, y), (x + w, y + h), (0, 0, 255), 2)
        # print(face)

    # Vertical data is unnecessary for a moment
    # Center point of main frame
    center_pointX, center_pointY = wCam / 2, hCam / 2

    # Points of center rectangle
    point1 = int(center_pointX) - 80, int(center_pointY) - 80
    point2 = int(center_pointX) + 80, int(center_pointY) + 80
    cv2.rectangle(frames, point1, point2, (255, 0, 0), 3)

    for (x, y, w, h) in face:
        # Center point of rectangle
        regCenterX, regCenterY = (x + (x + w)) / 2, (y + (y + h)) / 2
        # Algılanan nesnenin merkez noktasına uzaklığı
        merkeze_uzaklikX, merkeze_uzaklikY = regCenterX - center_pointX, regCenterY - center_pointY

        if (center_pointX - 80) < regCenterX < (center_pointX + 80):
            board.digital[pinPipe].write(0)  # 0 Olduğunda kapatıyor ve motorun çalışmasını sağlıyor
        else:
            board.digital[pinPipe].write(1)
            # We may want to reduce to amount of increase and decrease
            valueX = merkeze_uzaklikX * MAX_artis / center_pointX
            valueY = merkeze_uzaklikX * MAX_artis / center_pointX
            newX = newX - valueX / 5  # from start point to new point with value increase -
            newY = newY - valueY / 5  # from start point to new point with value increase -
            if newX > 180:
                newX = 180
            # - kısma düşüyor
            if newX < 10:
                newX = 0

            # print(newX)
            # Kameranın x ve y koordinatlarındaki takibi
            rotateservo(pin1, newX)
            rotateservo(pin2, newY)

    # ...
    # Flip the frames for mirror effect
    frames = cv2.flip(frames, 1)

    cv2.imshow('Output', frames)

    if cv2.waitKey(33) == 27:
        rotateservo(pin1, start_posX)
        rotateservo(pin2, start_posY)
        board.digital[pinPipe].write(0) # it can be change depends on how you wire the role
        board.digital[pinTest].write(0) # it can be change depends on how you wire the role
        break                           # I will add the connection diagram for this project later.

cv2.destroyAllWindows()
cap.release()
