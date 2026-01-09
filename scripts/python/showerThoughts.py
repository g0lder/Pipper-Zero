#!/usr/bin/env python3
import os
import time
MAIN_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
FIFO_PATH = os.path.join(MAIN_PATH, "pisugar_fifo")
LAUNCHER_PATH = os.path.join(MAIN_PATH, "launcher.py")
SCRIPT_DIR = os.path.dirname(__file__)
time_elapsed = 3600
try:
    os.remove(FIFO_PATH)
except Exception:
    pass
os.mkfifo(FIFO_PATH)
with open(FIFO_PATH, "r") as fifo:
    while True:
        cmd = fifo.readline().strip()
        if time_elapsed > 560:
            os.system(f"bash {SCRIPT_DIR}/showerThoughts.sh")
            time_elapsed = 0
        time.sleep(5)
        time_elapsed += 5

        if cmd == "triggerThree" or cmd == "triggerTwo":
            os.execlp("python3", "python3", LAUNCHER_PATH)
            exit()
