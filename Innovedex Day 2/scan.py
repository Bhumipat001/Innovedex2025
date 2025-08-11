from pyfirmata2 import Arduino, util
import time
import zmq
import threading
import tkinter as tk
from tkinter import ttk

# ---- ZMQ Setup ----
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt_string(zmq.SUBSCRIBE, "")
socket.setsockopt(zmq.RCVHWM, 10)

received_message = None
received_lock = threading.Lock()

def listen_detection():
    global received_message
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    while True:
        socks = dict(poller.poll(1000))
        if socket in socks and socks[socket] == zmq.POLLIN:
            try:
                msg = socket.recv_string(zmq.NOBLOCK)
                with received_lock:
                    received_message = msg
            except zmq.Again:
                continue

listener_thread = threading.Thread(target=listen_detection, daemon=True)
listener_thread.start()

try:
    donelist = []
    anglelist = [0, 0, 0, 0]  # [Red, Green, Blue, Purple/Yellow]

    board = Arduino('COM5')
    iterator = util.Iterator(board)
    iterator.start()

    print("Arduino connected successfully.")

    servo1 = board.get_pin('d:2:s')
    servo2 = board.get_pin('d:3:s')
    servo3 = board.get_pin('d:4:s')
    servo4 = board.get_pin('d:5:s')
    servo5 = board.get_pin('d:6:s')

    offset1 = 4.5
    offset2 = 0

    # --- Servo helper functions ---
    def gripFAST():
        servo4.write(170)
        servo5.write(10)
        time.sleep(0.5)

    def grip():
        ser4end = 170
        ser5end = 10
        ser4now = 120
        ser5now = 60
        n_faster = 7
        step4 = (ser4end - ser4now) / n_faster
        step5 = (ser5now - ser5end) / n_faster
        for i in range(n_faster):
            ser4now = min(ser4now + step4, ser4end)
            ser5now = max(ser5now - step5, ser5end)
            servo4.write(round(ser4now))
            servo5.write(round(ser5now))
            time.sleep(0.02)

    def ungripFAST():
        servo4.write(120)
        servo5.write(60)
        time.sleep(0.5)

    def ungrip():
        ser4start = servo4.read() or 170
        ser5start = servo5.read() or 10
        ser4end = 120
        ser5end = 60
        n_fast = 7
        step4 = (ser4end - ser4start) / n_fast
        step5 = (ser5end - ser5start) / n_fast
        for i in range(n_fast):
            ser4start = max(ser4start + step4, ser4end) if step4 < 0 else min(ser4start + step4, ser4end)
            ser5start = max(ser5start + step5, ser5end) if step5 < 0 else min(ser5start + step5, ser5end)
            servo4.write(round(ser4start))
            servo5.write(round(ser5start))
            time.sleep(0.02)

    def defaultheight():
        servo3.write(175)
        time.sleep(0.6)

    def storeheight():
        servo3.write(140)
        time.sleep(0.6)

    def pickheight():
        servo3.write(0)
        time.sleep(0.6)

    def position1():
        servo1.write(146 + offset1)
        servo2.write(180 + offset2)
        time.sleep(1.2)

    def position4():
        servo1.write(50 + offset1)
        servo2.write(0 + offset2)
        time.sleep(1.2)

    def position5():
        for i in range(0, 11):
            servo1.write(50 + offset1 + (107 - 50) * i / 10.0)
            servo2.write(0 + offset2 + (50 - 0) * i / 10.0)
            time.sleep(0.05)

    def pick4():
        pickheight()
        time.sleep(0.4)

        grip()
        time.sleep(0.2)

        storeheight()
        time.sleep(0.2)

        for i in range(0, 11):
            servo1.write(50 + offset1 + (107 - 50) * i / 10.0)
            servo2.write(0 + offset2 + (50 - 0) * i / 10.0)
            time.sleep(0.05)

        pickheight()
        time.sleep(0.3)

        ungrip()
        time.sleep(0.2)

    def smallmove(ang):
        servo1.write(ang + offset1 + 3)
        time.sleep(0.1)
        servo1.write(ang + offset1 + 6)
        time.sleep(0.1)
        servo1.write(ang + offset1 + 9)
        time.sleep(0.1)
        servo1.write(ang + offset1 + 12)
        time.sleep(0.1)
        servo1.write(ang + offset1 + 15)
        time.sleep(0.1)

    def setGray():
        defaultheight()
        position4()
        ungrip()
        pickheight()
        grip()
        time.sleep(0.8)
        ungrip()
        time.sleep(0.6)
        defaultheight()
        time.sleep(0.5)

    def pickang1(ang):
        servo2.write(169.7 + offset2)
        servo1.write(ang + offset1)
        time.sleep(0.6)
        pickheight()
        time.sleep(0.3)
        smallmove(ang)
        grip()
        time.sleep(0.2)
        defaultheight()
        time.sleep(0.2)
        position4()
        time.sleep(0.5)
        storeheight()
        time.sleep(0.15)
        ungrip()
        time.sleep(0.15)
        defaultheight()
        time.sleep(0.2)

    def scan():
        start_angle = 155
        end_angle = 0
        step = -1
        while start_angle >= end_angle:
            shouldJump=0
            servo1.write(start_angle)
            with received_lock:
                msg = received_message
            if msg != "0" and msg not in donelist:
                donelist.append(msg)
                if msg == "Red Donut":
                    anglelist[0] = start_angle
                    shouldJump=1
                elif msg == "Green Donut":
                    anglelist[1] = start_angle
                    shouldJump=1
                elif msg == "Blue Donut":
                    anglelist[2] = start_angle
                    shouldJump=1
                elif msg in ("Purple Donut", "Yellow Donut"):
                    anglelist[3] = start_angle
                    shouldJump=1

                scan_list.insert(tk.END, f"{msg} - {start_angle}°")
                root.update()

            if shouldJump==1:
                start_angle += -20
            elif 0 not in anglelist:
                break
            else:
                start_angle += step
            time.sleep(0.07)

    def start_process():
        start_btn.config(text="Running...", state="disabled")
        title_label.config(text="Innovedex Day 2", fg="#FFD700")
        root.update()

        donelist.clear()
        for i in range(len(anglelist)):
            anglelist[i] = 0

        scan()
        setGray()

        # Pick in correct order: Red -> Green -> Blue
        if anglelist[0] != 0:
            pickang1(anglelist[0])
        if anglelist[1] != 0:
            pickang1(anglelist[1])
        if anglelist[2] != 0:
            pickang1(anglelist[2])

        pick4()
        root.after(1000, root.destroy)

    # ---- Move to start scan position ----
    servo1.write(160 + offset1)
    servo2.write(180 + offset2)
    servo3.write(90)
    servo4.write(120)
    servo5.write(60)

    # ---- UI Setup ----
    root = tk.Tk()
    root.title("Innovedex Day 2")
    root.geometry("350x300")
    root.configure(bg="#222222")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton",
                    font=("Arial", 16, "bold"),
                    padding=10,
                    background="#4CAF50",
                    foreground="white")
    style.map("TButton",
              background=[("active", "#45a049")])

    title_label = tk.Label(root,
                           text="Innovedex Day 2",
                           font=("Arial", 14, "bold"),
                           fg="white",
                           bg="#222222")
    title_label.pack(pady=10)

    start_btn = ttk.Button(root, text="START", command=start_process)
    start_btn.pack(pady=10)

    scan_list = tk.Listbox(root,
                           font=("Arial", 12),
                           bg="#333333",
                           fg="white",
                           width=30,
                           height=8,
                           borderwidth=0,
                           highlightthickness=0)
    scan_list.pack(pady=10)

    root.mainloop()

except Exception as e:
    print(f"Error during initialization: {e}")
    if 'board' in locals():
        board.exit()