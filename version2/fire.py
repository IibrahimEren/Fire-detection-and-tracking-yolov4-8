from pyfirmata import Arduino, SERVO, OUTPUT
from ultralytics import YOLO
from time import time, sleep
import numpy as np
import cvzone
import math
import cv2

'''''       
           width 1280
.________________________________.
.                                .
.                                .
.                                .
.           Our video            . height 720
.                                .
.                                .
.                                .
.                                .
.________________________________.

'''''


# kameradan alınan verinin hangi piksel üzerinde olduğuna göre hesaplanmış
# şekilde hareket ettiren fonksiyon
def rotateservo(pin, angle):
    board.digital[pin].write(angle)
    sleep(0.015)


port = 'COM5'
board = Arduino(port)
pinX = 3  # X
pinY = 4  # Y
pinPipe = 5  # For water motor

board.digital[pinPipe].mode = OUTPUT  # MOTOR
board.digital[pinY].mode = SERVO  # Y
board.digital[pinX].mode = SERVO  # X

MAX_artis = 45
start_posX = 90
start_posY = 0
newX = start_posX  # for the first frame
newY = start_posY

# SET relay to start position
print("preparing relay")
board.digital[pinPipe].write(1)  # bir olduğunda kapalı bir şekilde başlatıyor

# FPS values for fps testing
pre_timeFrame = 0
new_timeFrame = 0


# Running real time from webcam
cap = cv2.VideoCapture(1)
wCam, hCam = 1080, 720
cap.set(3, wCam)
cap.set(4, hCam)

model = YOLO('best.pt')

# Center point of main frame
center_pointX, center_pointY = int(wCam / 2), int(hCam / 2)

# Points of center rectangle
point1 = int(center_pointX) - 80, int(center_pointY) - 80
point2 = int(center_pointX) + 80, int(center_pointY) + 80

# Reading the classes
classnames = ['fire']

##### REBOOTING #####
print("REBOOTING")
for i in range(0, 180, 5):
    rotateservo(pinX, i)
    rotateservo(pinY, i)
for i in range(180, 0, -5):
    rotateservo(pinX, i)
    rotateservo(pinY, i)
#### END OF REBOOTING #####

# SET servos to start position
print("Set servos to start positions")
rotateservo(pinX, start_posX)
rotateservo(pinY, start_posY)

while True:
    ret,frame = cap.read()
    frame = cv2.resize(frame,(1080,720))
    frame = cv2.flip(frame, 1)
    result = model(frame,stream=True)
    #   Draw a rectangle in the center of window for targeting
    cv2.rectangle(frame, point1, point2, (255, 0, 0), 3)

    frame_width = frame.shape[1]
    frame_height = frame.shape[0]

    # Getting bbox,confidence and class names informations to work with
    for info in result:
        boxes = info.boxes
        for box in boxes:
            confidence = box.conf[0]
            confidence = math.ceil(confidence * 100)
            Class = int(box.cls[0])
            if confidence > 50:
                x1,y1,x2,y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1),int(y1),int(x2),int(y2)
                
                box_center_x = int(x1 + (x2-x1)/2)
                box_center_y = int(y1 + (y2-y1)/2)
#TODO algılanan nesnenin konumu ayarlanacak
                # Algılanan nesnenin merkez noktasına uzaklığı
                merkeze_uzaklikX, merkeze_uzaklikY = box_center_x - center_pointX, box_center_y - center_pointY
                
                # alevin çizgisi
                cv2.rectangle(frame,(x1,y1),(x2,y2),(0,0,255),5)
                # merkezden aleve giden çizgi
                cv2.line(frame,(center_pointX , center_pointY),(box_center_x, box_center_y), (255,255,255), 4)

                cv2.putText(frame, f'{classnames[Class]} {confidence}%', (x1+8,y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
                ######### CONTROL OF  THE OBJECT IS INSIDE OF THE BOX OR NOT ################################
                if (center_pointX - 80) < box_center_x < (center_pointX + 80) and (center_pointY - 80) < box_center_y < (center_pointY + 80):
                    cv2.rectangle(frame, point1, point2, (0, 0, 255), 3)                   
                    print("1")
                    board.digital[pinPipe].write(0)  # 0 Olduğunda kapatıyor ve motorun çalışmasını sağlıyor
                ############################# END OF CONTROL ################################################

                ################## CALCULATING NEW VALUES OF SERVOS MOVEMENT TO GET OBJECT INSIDE THE BOX ###############
                else:
                    board.digital[pinPipe].write(1)

                    # We may want to reduce to amount of increase and decrease
                    valueX = merkeze_uzaklikX * MAX_artis / center_pointX
                    valueY = merkeze_uzaklikY * MAX_artis / center_pointY
                    newX = newX + valueX / 4  # from start point to new point with value increase -
                    newY = newY - valueY / 4  # from start point to new point with value increase -
                    if newX > 180:
                        print("newX: " + str(newX))
                        newX = 180
                    # - kısma düşüyor
                    if newX < 10:
                        print("newX: " + str(newX))
                        newX = 0
                    if newY > 180:
                        print("newY: " + str(newY))
                        newY = 180
                    # - kısma düşüyor
                    if newY < 5:
                        print("newY: " + str(newY))
                        newY = 0
                    # Kameranın x ve y koordinatlarındaki takibi
            rotateservo(pinX, newX)
            rotateservo(pinY, newY)
            ############################# END OF CALCULATING ################################################

    ####################### CHECKING IF FRAME HAS A OBJECT #########################################
#TODO: alev algılanmadığında motorun kapanmasını sağla
        # if ids_list.__len__() == 0:  # if frame has no object close the engine
        #     board.digital[pinPipe].write(1)
    ############################## END OF CHECKING ##################################################

        #   Draw a rectangle in the center of window for targeting
        cv2.rectangle(frame, point1, point2, (255, 0, 0), 3)

    ################ FRAME TESTING ###########################
    new_timeFrame = time()
    fps = 1 / (new_timeFrame - pre_timeFrame)
    pre_timeFrame = new_timeFrame
    fps = int(fps)
    cv2.putText(frame, "FPS: " + str(fps), (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 0), 2)
    ################ END OF TESTING ##########################

    if cv2.waitKey(33) == ord('r'):
        print("Return to start position")
        rotateservo(pinX, start_posX)
        rotateservo(pinY, start_posY)
        board.digital[pinPipe].write(1)
        newX = start_posX
        newY = start_posY
    elif cv2.waitKey(1) == 27:
        rotateservo(pinX, start_posX)
        rotateservo(pinY, start_posY)
        board.digital[pinPipe].write(1)  # it can be change depends on how you wire the role
        break

    cv2.imshow("Detector", frame)

cap.release()
cv2.destroyAllWindows()
