import zmq
from position import pick1, pick2, pick3, pick4
import re
import threading
import tkinter as tk
from tkinter import messagebox

# ---------------- ZeroMQ Setup ---------------- #
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt_string(zmq.SUBSCRIBE, "")

latest_msg = None  # Stores the latest received message

def get_color_from_position(pos_str):
    """Extract donut color name before any numbers."""
    match = re.search(r":\s*([A-Za-z ]+?)(?:\s+\d|$)", pos_str.strip())
    return match.group(1).strip() if match else None

def fetch_message_on_start():
    """Fetch the first message when program launches."""
    global latest_msg
    latest_msg = socket.recv_string()
    print(f"Received on startup: {latest_msg}")

    # Parse positions
    positions = latest_msg.split("|")
    colors = [get_color_from_position(p) for p in positions]

    # Update "Received" text in GUI
    received_text = "Received:\n"
    for i, color in enumerate(colors, start=1):
        received_text += f"Position {i}: {color}\n"
    received_label.config(text=received_text.strip())

    # Determine detected pick order (without pick4)
    color_order = ["Red Donut", "Green Donut", "Blue Donut"]
    pick_funcs = {0: "pick1", 1: "pick2", 2: "pick3"}
    pick_sequence = []

    for target_color in color_order:
        for idx, color in enumerate(colors):
            if color == target_color:
                pick_sequence.append(pick_funcs[idx])

    detected_order_str = ", ".join(pick_sequence)

    # Auto-fill manual entry with detected order
    manual_order_var.set(detected_order_str)

def validate_manual_order(order_str):
    """Validate manual input: must be a permutation of pick1, pick2, pick3."""
    valid_picks = {"pick1", "pick2", "pick3"}
    parts = [p.strip() for p in order_str.split(",")]
    if set(parts) == valid_picks and len(parts) == 3:
        return parts
    return None

def main_process():
    """Run sorting based on stored message and manual order if any."""
    global latest_msg
    if not latest_msg:
        print("⚠ No data received yet!")
        return

    positions = latest_msg.split("|")
    colors = [get_color_from_position(p) for p in positions]
    position_to_pick_func = {0: pick1, 1: pick2, 2: pick3}

    # Use manual order if valid
    manual_order = manual_order_var.get()
    manual_order = manual_order.strip()
    pick_sequence = validate_manual_order(manual_order)

    if pick_sequence is None:
        # Use detected order if manual invalid or empty
        color_order = ["Red Donut", "Green Donut", "Blue Donut"]
        pick_sequence = []
        for target_color in color_order:
            for idx, color in enumerate(colors):
                if color == target_color:
                    pick_sequence.append(f"pick{idx+1}")

    print("Using pick sequence:", pick_sequence)

    # Execute picks in sequence
    for action in pick_sequence:
        idx = int(action[-1]) - 1
        func = position_to_pick_func.get(idx)
        color = colors[idx]
        if func:
            print(f"Calling {func.__name__} for {color} at Position {idx+1}")
            func()

    print("Calling pick4 to finish job")
    pick4()

    print("✅ Done!")
    root.quit()

def start_process():
    """Run main_process in a separate thread."""
    manual_order = manual_order_var.get().strip()
    if manual_order and not validate_manual_order(manual_order):
        messagebox.showerror("Invalid Input", 
            "Manual pick order must be all of pick1, pick2, pick3 separated by commas.\nExample: pick3, pick1, pick2")
        return

    start_btn.config(text="Running...", state="disabled", bg="#999")
    thread = threading.Thread(target=main_process, daemon=True)
    thread.start()

# ---------------- UI Setup ---------------- #
root = tk.Tk()
root.title("Innovedex Day 1")
root.geometry("400x280")
root.resizable(False, False)

title_label = tk.Label(root, text="", font=("Arial", 16, "bold"))
title_label.pack(pady=(10, 0))
title_label.config(text="Innovedex Day 1")

frame = tk.Frame(root, padx=15, pady=15)
frame.pack(expand=True, fill="both")

received_label = tk.Label(frame, text="Waiting for data...", font=("Arial", 10), justify="left", anchor="w")
received_label.pack(fill="x", pady=(0, 5))

manual_label = tk.Label(frame, text="Pick Order:", font=("Arial", 10, "bold"), fg="blue")
manual_label.pack(anchor="w")

manual_order_var = tk.StringVar()
manual_entry = tk.Entry(frame, textvariable=manual_order_var, font=("Consolas", 11), width=30)
manual_entry.pack(pady=(0,15))

start_btn = tk.Button(
    frame, 
    text="START", 
    command=start_process, 
    font=("Arial", 12, "bold"), 
    bg="#4CAF50", 
    fg="white", 
    activebackground="#45a049", 
    width=20, 
    height=2
)
start_btn.pack()

# Fetch data immediately when program launches
threading.Thread(target=fetch_message_on_start, daemon=True).start()

root.mainloop()