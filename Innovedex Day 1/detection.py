# custom_model_detection.py
# ใช้โมเดล custom (best.pt) พร้อมกำหนดความมั่นใจขั้นต่ำที่จะแสดงผล

import cv2
from ultralytics import YOLO
import zmq

# โหลดโมเดลที่ฝึกเอง (เช่นจาก Roboflow, PyTorch ฯลฯ)
model = YOLO("best.pt")

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# ✅ ค่าความมั่นใจ (confidence) ต่ำสุดที่ยอมให้แสดงผล (0.0–1.0)
CONFIDENCE_THRESHOLD = 0.5

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ ไม่สามารถอ่านภาพจากกล้องได้")
        break

    results = model(frame, verbose=False)[0]

    for box in results.boxes:
        conf = float(box.conf)
        if conf < CONFIDENCE_THRESHOLD:
            continue
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        color = (0, 255, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        text = f"{label} {conf:.2f}"
        cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Collect boxes for position printing
    detected = []
    for box in results.boxes:
        conf = float(box.conf)
        if conf < CONFIDENCE_THRESHOLD:
            continue
        x1 = int(box.xyxy[0][0])
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        detected.append((x1, label, conf))

    detected.sort(key=lambda x: x[0])  # sort by x1 (left to right)
    possible_colors = {"Red Donut", "Green Donut", "Blue Donut"}
    detected_labels = [label for _, label, _ in detected]
    missing_colors = list(possible_colors - set(detected_labels))
    pos1 = f"Position 1: {detected[0][1]} {detected[0][2]:.2f}" if len(detected) > 0 else "Position 1: None"
    pos2 = f"Position 2: {detected[-1][1]} {detected[-1][2]:.2f}" if len(detected) > 1 else "Position 2: None"
    pos3 = f"Position 3: {missing_colors[0]}" if len(missing_colors) == 1 else "Position 3: None"
    position_str = f"{pos1} | {pos2} | {pos3}"
    print(position_str)
    socket.send_string(position_str)

    cv2.imshow("Custom YOLOv8 Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()