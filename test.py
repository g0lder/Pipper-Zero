#!/usr/bin/python3
import time
from pathlib import Path

FIFO_PATH = "/tmp/pisugar_fifo"

#open for reading
with open(FIFO_PATH, "r") as fifo:
    while True:
        cmd = fifo.readline().strip()
        if cmd:
            print("Button:", cmd)

