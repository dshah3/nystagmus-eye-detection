import tkinter as tk
from tkinter import simpledialog
import subprocess
import os
import threading
import time
from PIL import Image, ImageTk
import pexpect
from dotenv import load_dotenv
import os
import sys

load_dotenv()

RASPBERRY_PI_USERNAME = os.getenv("RASPBERRY_PI_USERNAME")
RASPBERRY_PI_IP_ADDR = os.getenv("RASPBERRY_PI_IP_ADDR")
RASPBERRY_PI_LOCAL_ENV = os.getenv("RASPBERRY_PI_LOCAL_ENV")
RASPBERRY_PI_SCRIPT_LOC = os.getenv("RASPBERRY_PI_SCRIPT_LOC")
RASPBERRY_PI_VIDEO_NAME = os.getenv("RASPBERRY_PI_VIDEO_NAME")
LOCAL_FILE_SAVE = os.getenv("LOCAL_FILE_SAVE")
SCRIPT = f"pwd; source {RASPBERRY_PI_LOCAL_ENV}/bin/activate; sudo {RASPBERRY_PI_LOCAL_ENV}/bin/python {RASPBERRY_PI_SCRIPT_LOC}"


import pexpect
import sys


def terminal_password(command, password, expect_pattern="riki@10.194.88.166's password:"):
    child = pexpect.spawn(command, encoding='utf-8')
    child.logfile = sys.stdout  # Directly log everything to stdout
    child.expect(expect_pattern)
    child.sendline(password)
    # After sending the password, we let the script run and finish on its own without waiting for EOF.

def password_scp(command, password):
    child = pexpect.spawn(command, encoding='utf-8')
    child.logfile = sys.stdout  # Directly log everything to stdout
    child.expect("password:")
    child.sendline(password)
    # Let the SCP command run and finish on its own without explicitly waiting for EOF.

def remote_execute():
    def ask_password():
        password = simpledialog.askstring("Password", "Enter Device Password", parent=root)  # Ensure parent=root for thread safety
        if password:
            # Execute SSH command
            terminal_password(f"ssh -l {RASPBERRY_PI_USERNAME} {RASPBERRY_PI_IP_ADDR} 'pwd; source bme436-final/bin/activate; sudo bme436-final/bin/python /home/riki/strandtest3.py'", password)
            # Optionally, execute SCP command to transfer files
            # Uncomment the following line if you want to enable SCP file transfer
            # password_scp(f"scp -r {RASPBERRY_PI_USERNAME}@{RASPBERRY_PI_IP_ADDR}:/home/{RASPBERRY_PI_USERNAME}/{RASPBERRY_PI_VIDEO_NAME} {LOCAL_FILE_SAVE}", password)

    root.after(0, ask_password)

def collect_video():
    threading.Thread(target=remote_execute, daemon=True).start()

def wait_for_video():
    while not os.path.exists("test_videos/test_random.mp4"):
        time.sleep(1)

root = tk.Tk()
root.title("Tipsy Trackers")

collect_video_button = tk.Button(root, text="Collect Video", command=collect_video)
collect_video_button.grid(row=0, column=0)

root.mainloop()