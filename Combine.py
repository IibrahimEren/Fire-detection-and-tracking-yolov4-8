import numpy as np
from time import time, sleep
import cv2
from pyfirmata import Arduino, SERVO, OUTPUT

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


port = 'COM3'
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

# Pretrained model for FIRE
model = cv2.dnn.readNetFromDarknet("dnn_model/spot_yolov4.cfg", "dnn_model/spot_yolov4_last.weights")

# set CUDA as the preferable backend and target
print("[INFO] setting preferable backend and target to CUDA...")
model.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
model.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

labels = ["fire"]
colors = ["0,0,255"]
colors = [np.array(color.split(",")).astype("int") for color in colors]
colors = np.array(colors)

cap = cv2.VideoCapture(0)
wCam, hCam = 1280, 720
cap.set(3, wCam)
cap.set(4, hCam)

# Center point of main frame
center_pointX, center_pointY = wCam / 2, hCam / 2

# Points of center rectangle
point1 = int(center_pointX) - 80, int(center_pointY) - 80
point2 = int(center_pointX) + 80, int(center_pointY) + 80

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
    success, frame = cap.read()
    #   check the video sources
    if not success:
        break
    frame = cv2.flip(frame, 1)

    frame_width = frame.shape[1]
    frame_height = frame.shape[0]

    frame_blob = cv2.dnn.blobFromImage(frame, 1 / 255, (416, 416), swapRB=True, crop=False)
    model.setInput(frame_blob)

    layers = model.getLayerNames()
    output_layer = [layers[layer - 1] for layer in model.getUnconnectedOutLayers()]
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

            if confidence > 0.50:
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
    ######################## END OF OPERATION 3 ############################

        end_x = start_x + box_width
        end_y = start_y + box_height

        box_color = colors[predicted_id]
        box_color = [int(each) for each in box_color]

        label = "{}: {:.2f}%".format(label, confidence * 100)

        # Algılanan nesnenin merkez noktasına uzaklığı
        merkeze_uzaklikX, merkeze_uzaklikY = box_center_x - center_pointX, box_center_y - center_pointY

        ######### CONTROL OF  THE OBJECT IS INSIDE OF THE BOX OR NOT ################################
        if (center_pointX - 80) < box_center_x < (center_pointX + 80) and (center_pointY - 80) < box_center_y < (center_pointY + 80):
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

        #   Draw a rectangle on the frame for detected object
        cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), box_color, 2)
        #   Draw a rectangle for features
        cv2.rectangle(frame, (start_x - 1, start_y), (end_x + 1, start_y - 30), box_color, -1)
        #   Write the confidence value above the object
        cv2.putText(frame, label, (start_x, start_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

####################### CHECKING IF FRAME HAS A OBJECT ##########################################
    if ids_list.__len__() == 0:  # if frame has no object close the engine
        board.digital[pinPipe].write(1)
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
