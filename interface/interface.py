import tkinter as tk
from tkinter import simpledialog, filedialog, Entry
import subprocess
import os
import threading
import time
from PIL import Image, ImageTk
import pexpect
from dotenv import load_dotenv
import os
import shutil
import cv2
import glob
import sys
import numpy as np
load_dotenv()

RASPBERRY_PI_USERNAME = os.getenv("RASPBERRY_PI_USERNAME")
RASPBERRY_PI_IP_ADDR = os.getenv("RASPBERRY_PI_IP_ADDR")
RASPBERRY_PI_LOCAL_ENV = os.getenv("RASPBERRY_PI_LOCAL_ENV")
RASPBERRY_PI_SCRIPT_LOC = os.getenv("RASPBERRY_PI_SCRIPT_LOC")
RASPBERRY_PI_VIDEO_NAME = os.getenv("RASPBERRY_PI_VIDEO_NAME")
LOCAL_FILE_SAVE = os.getenv("LOCAL_FILE_SAVE")
SCRIPT = f"pwd; source {RASPBERRY_PI_LOCAL_ENV}/bin/activate; sudo {RASPBERRY_PI_LOCAL_ENV}/bin/python {RASPBERRY_PI_SCRIPT_LOC}"

global left_tolerance, right_tolerance, eye_height_min, eye_height_max, min_contour_area, max_contour_area, max_gray, min_gray

left_tolerance = 0.15
right_tolerance = 1.0
eye_height_min = 0.15
eye_height_max = 0.50
min_contour_area = 10
max_contour_area = 500
max_gray = 240
min_gray = 5

class MyVideoCapture:
    def __init__(self, video_source=0):
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)
        
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)
        
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

            


# def terminal_password(command, password):
#     child = pexpect.spawn(command)
#     child.expect('Password:')
#     child.sendline(password)
#     child.expect(pexpect.EOF)
#     print(child.before)

# def remote_execute():
#     password = simpledialog.askstring("Password", "Enter Device Password")
#     if password:
#         terminal_password(f"ssh -l ${RASPBERRY_PI_USERNAME} ${RASPBERRY_PI_IP_ADDR} \"{SCRIPT}\"", password)
#         terminal_password(
#             f"scp -r ${RASPBERRY_PI_USERNAME}@${RASPBERRY_PI_IP_ADDR}:/home/
#             ${RASPBERRY_PI_USERNAME}/${RASPBERRY_PI_VIDEO_NAME} ${LOCAL_FILE_SAVE}", password
#         )

def create_placeholder(parent, width, height, text):
    canvas = tk.Canvas(parent, width=width, height=height, bg='gray')
    canvas.create_text(width//2, height//2, text=text, fill="darkblue")
    return canvas

def check_and_display_video(video_frame):
    print("Current working directory:", os.getcwd())
    video_files = [f for f in os.listdir("../output_videos") if f.endswith(('.mp4', '.avi'))]  # Check for common video file extensions
    if video_files:
        video_path = os.path.join("../output_videos", video_files[0])  # Just take the first video for simplicity
        play_video(video_frame, video_path)
    else:
        create_placeholder(video_frame, 400, 300, "No Video Available")

def check_and_display_graph(graph_frame):
    def update_graph_display():
        graph_files = [f for f in os.listdir('../output_graphs') if f.endswith('.png')]
        if graph_files:
            graph_path = os.path.join('../output_graphs', graph_files[0])
            display_graph(graph_path, graph_frame)
        else:
            create_placeholder(graph_frame, 400, 300, "No Graph Available")
        graph_frame.after(5000, update_graph_display)  # Check for new graph every 5 seconds

    update_graph_display()
    
    
    
def check_and_display_metric(metric_frame):
    def update_metric_display():
        metric_files = [f for f in os.listdir('../') if f.endswith('.npy')]
        if metric_files:
            metric_path = os.path.join('../', metric_files[0])
            display_metric(metric_path, metric_frame)
        else:
            create_placeholder(metric_frame, 400, 300, "No Metric Available")
        metric_frame.after(5000, update_metric_display)  # Check for new graph every 5 seconds

    update_metric_display()
    

def setup_settings_frame(parent):
    global left_tolerance, right_tolerance, eye_height_min, eye_height_max, min_contour_area, max_contour_area, max_gray, min_gray

    settings_frame = tk.Frame(parent)
    settings_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    settings = {
        "Left Tolerance": (0, 1, 0.01, 'left_tolerance'),
        "Right Tolerance": (0, 1, 0.01, 'right_tolerance'),
        "Eye Height Min": (0, 1, 0.01, 'eye_height_min'),
        "Eye Height Max": (0, 1, 0.01, 'eye_height_max'),
        "Min Contour Area": (0, 5000, 1, 'min_contour_area'),
        "Max Contour Area": (0, 5000, 1, 'max_contour_area'),
        "Max Gray": (0, 255, 1, 'max_gray'),
        "Min Gray": (0, 255, 1, 'min_gray'),
    }

    def update_global_setting(name, value):
        globals()[name] = float(value)
        print(f"{name} updated to {value}")  # Optional: for debugging

    for i, (name, (start, end, step, var_name)) in enumerate(settings.items()):
        row_frame = tk.Frame(settings_frame)
        row_frame.grid(row=i, column=0, sticky="ew")
        tk.Label(row_frame, text=name).pack(side=tk.LEFT, anchor="w")
        slider = tk.Scale(row_frame, from_=start, to=end, resolution=step, orient=tk.HORIZONTAL)
        slider.set(globals()[var_name])  # Set the initial value of the slider
        slider.pack(side=tk.LEFT, anchor="w")
        entry = Entry(row_frame, width=5)
        entry.insert(0, str(globals()[var_name]))  # Set the initial value of the entry
        entry.pack(side=tk.LEFT, pady=(20,0))  # Adjust vertical padding to align with the slider

        # Update the global variable when the slider is released
        slider.bind("<ButtonRelease-1>", lambda event, name=var_name, s=slider: update_global_setting(name, s.get()))
        # Update the global variable when the entry value is submitted
        entry.bind("<Return>", lambda event, name=var_name, e=entry: update_global_setting(name, e.get()))

def reset_folders():
    folders = ["../test_videos", "../output_videos", "../output_graphs"]
    for folder in folders:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

def play_video(frame, video_path):
    video_capture = MyVideoCapture(video_path)
    
    def update_frame():
        ret, frame = video_capture.get_frame()
        if ret:
            frame_image = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=frame_image)
            label.imgtk = imgtk
            label.configure(image=imgtk)
            label.after(10, update_frame)
        else:
            video_capture.vid.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop the video
            update_frame()

    label = tk.Label(frame)
    label.grid(row=0, column=0)
    update_frame()

def execute_ssh_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, encoding='utf-8')
        print(output)
    except subprocess.CalledProcessError as e:
        print("Error executing command:", e.output)

def remote_execute():
    def execute_commands():
        # Execute SSH command

        print("We are in here")
        ssh_command = f"ssh {RASPBERRY_PI_USERNAME}@{RASPBERRY_PI_IP_ADDR} \"{SCRIPT}\""
        execute_ssh_command(ssh_command)
        # Optionally, execute SCP command to transfer files
        # Uncomment the following line if you want to enable SCP file transfer
        scp_command = "scp -r riki@10.194.88.166:/home/riki/test_video_random.mp4 ../test_videos"
        execute_ssh_command(scp_command)

    root.after(0, execute_commands)

def analyze_video():

    print("We are analyzing the video now")

    input_video_path = glob.glob("../test_videos/*.mp4")
    if not input_video_path:
        print("No video found in test_videos to analyze.")
        return
    input_video_path = input_video_path[0]

    output_video_path = "../output_videos/test.mp4"

    command = [
        sys.executable, "../engine/analysis.py",
        "--input_video_path", input_video_path,
        "--output_video_path", output_video_path,
        "--left_tolerance", str(left_tolerance),
        "--right_tolerance", str(right_tolerance),
        "--eye_height_min", str(eye_height_min),
        "--eye_height_max", str(eye_height_max),
        "--min_contour_area", str(min_contour_area),
        "--max_contour_area", str(max_contour_area),
        "--max_gray", str(max_gray),
        "--min_gray", str(min_gray)
    ]

    try:
        subprocess.run(command, check=True)
        print("Video analysis completed successfully.")
        # After analysis, check and display the new video
        check_and_display_video(video_frame)
    except subprocess.CalledProcessError as e:
        print(f"Error during video analysis: {e}")


def collect_video():
    threading.Thread(target=remote_execute, daemon=True).start()

def wait_for_video():
    while not os.path.exists("test_videos/test_random.mp4"):
        time.sleep(1)
    
    load_and_play_video("test_videos/test_random.mp4")

def load_and_play_video(video_path):
    pass

def display_metric(file_path, metrics_window, threshold = 3):
    for widget in metrics_window.winfo_children():
        widget.destroy()  # Clear the previous graph or placeholder
        
    
    if not file_path:
        print("No file selected.")
        return

    # Load the .npy file
    data = np.load(file_path)
    if data.size < 2:
        print("The selected file does not contain enough data.")
        return

    # Assuming the first two values are the metrics we need to display
    metric1, metric2 = np.round(data[0], 1), np.round(data[1], 1)
    # Add labels to display the metrics
    
    if metric1 > threshold:
        tk.Label(metrics_window, text=f"RMS Left ({metric1}) is over the threshold ({threshold})").pack(pady=10)
    else: 
        tk.Label(metrics_window, text=f"RMS Left: ({metric1}) is under the threshold ({threshold})").pack(pady=10)
    
    if metric2 > threshold:
        tk.Label(metrics_window, text=f"RMS Right: ({metric2}) is over the threshold ({threshold})").pack(pady=10)
    else: 
        tk.Label(metrics_window, text=f"RMS Right: ({metric2}) is under the threshold ({threshold})").pack(pady=10)
    
    
    if metric1 > threshold and metric2 > threshold:
        tk.Label(metrics_window, text="NYSTAGMUS LIKELY!!!").pack(pady=10)
    else:
        tk.Label(metrics_window, text="NYSTAGMUS UNLIKELY!!!").pack(pady=10)
            

# Bind this function to an appropriate event or button in your tkinter GUI


def display_graph(graph_image_path, graph_frame):
    for widget in graph_frame.winfo_children():
        widget.destroy()  # Clear the previous graph or placeholder
    img = Image.open(graph_image_path)
    img = img.resize((600, 300))  # Resize the image to fit the frame
    imgtk = ImageTk.PhotoImage(image=img)
    graph_label = tk.Label(graph_frame, image=imgtk)
    graph_label.image = imgtk  # Keep a reference so it's not garbage collected
    graph_label.pack()


root = tk.Tk()
root.title("Tipsy Trackers")
root.geometry("1050x850")  # Adjust the size as needed

top_frame = tk.Frame(root)
top_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

collect_video_button = tk.Button(top_frame, text="Collect Video", command=remote_execute)  # Implement command
collect_video_button.pack(side=tk.LEFT, padx=5)

analyze_video_button = tk.Button(top_frame, text="Analyze Video", command=analyze_video)
analyze_video_button.pack(side=tk.LEFT, padx=5)

reset_button = tk.Button(top_frame, text="Reset", command=reset_folders)
reset_button.pack(side=tk.LEFT)

video_frame = tk.Frame(root, width=200, height=100)
video_frame.grid(row=1, column=0, padx=10, pady=10)

check_and_display_video(video_frame)

setup_settings_frame(root)

bottom_frame = tk.Frame(root)
bottom_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

graph_panel = tk.Canvas(bottom_frame, width=600, height=300, bg='gray')
graph_panel.pack(side=tk.LEFT, padx=10)

check_and_display_graph(graph_panel)

# Create a new window for displaying the metrics
metric_window = tk.Frame(bottom_frame, width=300, height=150)
metric_window.pack(side=tk.RIGHT, padx=10)
check_and_display_metric(metric_window)
    
    
root.mainloop()