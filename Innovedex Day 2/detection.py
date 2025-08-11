import cv2
from ultralytics import YOLO
import zmq
import math
import time

model = YOLO("best.pt")

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

CONFIDENCE_THRESHOLD = 0.3

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555")

time.sleep(1)  # Give subscriber time to connect

# Define line segment endpoints
line_pt1 = (200, 300)
line_pt2 = (450, 150)
tolerance = 40  # pixels

def point_line_distance(px, py, x1, y1, x2, y2):
    line_mag = math.hypot(x2 - x1, y2 - y1)
    if line_mag < 1e-6:
        return math.hypot(px - x1, py - y1)

    t = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_mag ** 2)
    t = max(0, min(1, t))

    closest_x = x1 + t * (x2 - x1)
    closest_y = y1 + t * (y2 - y1)

    dist = math.hypot(px - closest_x, py - closest_y)
    return dist

donut_labels = {"Red Donut", "Green Donut", "Blue Donut", "Purple Donut", "Yellow Donut"}

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ ไม่สามารถอ่านภาพจากกล้องได้")
        break

    results = model(frame, verbose=False)[0]

    frame_height, frame_width = frame.shape[:2]
    cv2.line(frame, line_pt1, line_pt2, (255, 0, 0), 1)

    near_line_labels = []

    for box in results.boxes:
        conf = float(box.conf[0])
        if conf < CONFIDENCE_THRESHOLD:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls_id = int(box.cls[0])
        label = model.names.get(cls_id, f"Unknown_{cls_id}")

        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        color = (0, 255, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        text = f"{label} {conf:.2f}"
        cv2.putText(frame, text, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

        if label in donut_labels:
            dist = point_line_distance(center_x, center_y, *line_pt1, *line_pt2)
            if dist <= tolerance:
                near_line_labels.append(label)

    if near_line_labels:
        # Send each detected near-line donut once per frame
        for label in near_line_labels:
            print(f"{label}")
            socket.send_string(label)
    else:
        socket.send_string("0")

    cv2.imshow("Custom YOLOv8 Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()