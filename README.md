## Object Tracking and Detection with Servo Control

This project is an implementation of real-time object detection and tracking using YOLO (You Only Look Once) deep learning model along with servo motor control. The system detects objects, specifically "fire," in the video stream from a webcam and adjusts the position of the servo motors to track the detected object.





https://github.com/IibrahimEren/Servo-motor-controlling-with-python-Object-Detection-/assets/87008174/cc4dd1ce-a6a8-472c-84ea-9a1167fffa1a





### Hardware Requirements:
- Arduino Board with Servo Motors and Water Pump Motor
- Webcam (or any video source)

### Software Requirements:
- Python 3.x
- OpenCV
- PyFirmata

### Usage:

1. Connect the Arduino board to your computer.
2. Upload the StandardFirmata sketch to the Arduino board using Arduino IDE.
3. Install the required Python packages using the following command:
   ```
   pip install opencv-python numpy pyfirmata
   ```
4. Run the Python script (`object_tracking.py`) to start the object detection and tracking process.
5. Place objects in front of the webcam and observe how the system tracks the detected objects using servo motors.

### Description:

The script `object_tracking.py` performs the following tasks:
- Connects to the webcam and initializes the servo motors connected to the Arduino board.
- Loads a pre-trained YOLO model (YOLOv4) for object detection. The model is configured to use CUDA GPU for faster processing if available.
- Captures frames from the webcam, applies YOLO object detection, and identifies objects with a confidence threshold of 50%.
- If the system detects a "fire" object, it tracks the detected object's center using servo motors to keep it within the center of the frame.
- The servo motors are controlled using PyFirmata to rotate horizontally (X-axis) and vertically (Y-axis) to track the detected object.
- The system also displays real-time frames with bounding boxes around detected objects and calculates frames-per-second (FPS) for performance testing.
- To reset the servo motors to the initial position and stop tracking, press the 'r' key.
- To exit the program, press the 'Esc' key.

### Notes:

- The code is designed to track "fire" objects. You can modify the code to detect and track other objects by using different pre-trained YOLO models and updating the labels accordingly.
- Make sure the Arduino is correctly wired with the servo motors and water pump motor.
- Adjust the servo motor pins (pinX and pinY) in the code according to your setup.
