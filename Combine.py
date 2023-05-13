import numpy as np
from time import time, sleep
import cv2
from pyfirmata import Arduino, SERVO, OUTPUT


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


# kameradan alınan verinin hangi piksel üzerinde olduğuna göre hesaplanmış
# şekilde hareket ettiren fonksiyon
def rotateservo(pin, angle):
    board.digital[pin].write(angle)
    sleep(0.015)


#
#
# Hedef görmediği anlarda etrafı taraması için fonksiyon >> YOLOV'a göre yeniden düzenlenilmesi gerekiyor
# def scanArea(pin1, current):
#     for i in range(current, 180):
#         for i in range(180, 0):
#             board.digital[pin1].write(i)
#             # Hedef gördüğü an döngüden çıkması için if bloğu
#             if len(fire) != 0:
#                 break
#

#
#
port = 'COM3'
pin1 = 3  # X
pin2 = 4  # Y
pinTest = 5  # >>> Test Pini LED
pinPipe = 6  # For water motor
board = Arduino(port)
#
MAX_artis = 45
start_posX = 90
start_posY = 0
newX = start_posX  # for the first frame
newY = start_posY
#
board.digital[pin2].mode = SERVO  # Y
board.digital[pin1].mode = SERVO  # X
board.digital[pinTest].mode = OUTPUT  # LED >> **Led motorla birlikte aynı pine bağlanılabilir
board.digital[pinPipe].mode = OUTPUT  # MOTOR

# SET relay to start position
board.digital[pinPipe].write(0)  # bir olduğunda kapalı bir şekilde başlatıyor
board.digital[pinTest].write(0)

# SET servos to start position
rotateservo(pin1, start_posX)
rotateservo(pin2, start_posY)

board.digital[pin2].mode = SERVO  # Y
board.digital[pin1].mode = SERVO  # X
board.digital[pinTest].mode = OUTPUT  # LED
board.digital[pinPipe].mode = OUTPUT  # MOTOR

# SET relay to start position
board.digital[pinPipe].write(0)  # bir olduğunda kapalı bir şekilde başlatıyor
board.digital[pinTest].write(0)

# SET servos to start position
rotateservo(pin1, start_posX)
rotateservo(pin2, start_posY)
# FPS values for launch
pre_timeFrame = 0
new_timeFrame = 0
# Pretrained model for FIRE
model = cv2.dnn.readNetFromDarknet("dnn_model/spot_yolov4.cfg", "dnn_model/spot_yolov4_last.weights")
#
labels = ["fire"]
colors = ["0,0,255"]
colors = [np.array(color.split(",")).astype("int") for color in colors]
colors = np.array(colors)
#
cap = cv2.VideoCapture(0)
wCam, hCam = 1280, 720

cap.set(3, wCam)
cap.set(4, hCam)

# Center point of main frame
center_pointX, center_pointY = wCam / 2, hCam / 2
while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    # Points of center rectangle
    point1 = int(center_pointX) - 80, int(center_pointY) - 80
    point2 = int(center_pointX) + 80, int(center_pointY) + 80
    cv2.rectangle(frame, point1, point2, (255, 0, 0), 3)

    frame_width = frame.shape[1]
    frame_height = frame.shape[0]

    frame_blob = cv2.dnn.blobFromImage(frame, 1 / 255, (416, 416), swapRB=True, crop=False)

    layers = model.getLayerNames()
    output_layer = [layers[layer - 1] for layer in model.getUnconnectedOutLayers()]
    model.setInput(frame_blob)

    detection_layers = model.forward(output_layer)

    ############## NON-MAXIMUM SUPPRESSION - OPERATION 1 ###################
    ids_list = []
    boxes_list = []
    confidences_list = []
    ############################ END OF OPERATION 1 ########################

    for detection_layer in detection_layers:
        for object_detection in detection_layer:

            scores = object_detection[5:]
            predicted_id = np.argmax(scores)
            confidence = scores[predicted_id]

            if confidence > 0.20:
                label = labels[predicted_id]
                bounding_box = object_detection[0:4] * np.array([frame_width, frame_height, frame_width, frame_height])
                (box_center_x, box_center_y, box_width, box_height) = bounding_box.astype("int")

                start_x = int(box_center_x - (box_width / 2))
                start_y = int(box_center_y - (box_height / 2))

                ############## NON-MAXIMUM SUPPRESSION - OPERATION 2 ###################
                ids_list.append(predicted_id)
                confidences_list.append(float(confidence))
                boxes_list.append([start_x, start_y, int(box_width), int(box_height)])
                ############################ END OF OPERATION 2 ########################

    ############## NON-MAXIMUM SUPPRESSION - OPERATION 3 ###################
    max_ids = cv2.dnn.NMSBoxes(boxes_list, confidences_list, 0.5, 0.4)

    for max_id in max_ids:
        max_class_id = max_id
        box = boxes_list[max_class_id]

        start_x = box[0]
        start_y = box[1]
        box_width = box[2]
        box_height = box[3]

        predicted_id = ids_list[max_class_id]
        label = labels[predicted_id]
        confidence = confidences_list[max_class_id]
    ############################ END OF OPERATION 3 ########################

        end_x = start_x + box_width
        end_y = start_y + box_height

        box_color = colors[predicted_id]
        box_color = [int(each) for each in box_color]

        label = "{}: {:.2f}%".format(label, confidence * 100)
        ############
        # Algılanan nesnenin merkez noktasına uzaklığı
        merkeze_uzaklikX, merkeze_uzaklikY = box_center_x - center_pointX, box_center_y - center_pointY
    ######### CONTROL OF  THE OBJECT IS INSIDE OF THE BOX OR NOT ################################
        if (center_pointX - 80) < box_center_x < (center_pointX + 80):
            if (center_pointY - 80) < box_center_y < (center_pointY + 80):
                print("1")
                board.digital[pinPipe].write(0)  # 0 Olduğunda kapatıyor ve motorun çalışmasını sağlıyor
    ############################# END OF CONTROL ################################################

    ################## CALCULATING NEW VALUES OF SERVOS MOVEMENT TO GET OBJECT INSIDE THE BOX ###############
        else:
            print("0")
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
            if newY > 180:
                newY = 180
            # - kısma düşüyor
            if newY < 10:
                newY = 0
            # Kameranın x ve y koordinatlarındaki takibi
            rotateservo(pin1, newX)
            rotateservo(pin2, newY)
        ############################# END OF CALCULATING ################################################

        cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), box_color, 2)
        cv2.rectangle(frame, (start_x - 1, start_y), (end_x + 1, start_y - 30), box_color, -1)
        cv2.putText(frame, label, (start_x, start_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    ################ FRAME TESTING ###########################
    new_timeFrame = time()
    fps = 1 / (new_timeFrame - pre_timeFrame)
    pre_timeFrame = new_timeFrame
    fps = int(fps)
    cv2.putText(frame, "FPS: " + str(fps), (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 0), 2)
    ################ END OF TESTING ##########################

    if cv2.waitKey(1) == 27:
        break

    cv2.imshow("Detector", frame)

# %%
cap.release()
cv2.destroyAllWindows()
