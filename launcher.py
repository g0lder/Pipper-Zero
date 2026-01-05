#!/usr/bin/python3
import os
import time
from pathlib import Path
from PIL import Image, ImageDraw
from waveshare_epd import epd2in13_V4

# ------------------------
# Config
# ------------------------
SELF_PATH=os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = Path(f"{SELF_PATH}/scripts")
IMAGES_DIR = Path(f"{SELF_PATH}/logos")
FIFO_PATH = f"{SELF_PATH}/pisugar_fifo"
try:
    os.remove(FIFO_PATH)
except Exception:
    pass
os.mkfifo(FIFO_PATH,0o666)

VISIBLE_ITEMS = 3
CENTER_SCALE = 1.0
SIDE_SCALE = 0.6
SQUIRCLE_SIZE = (100, 100)
PARTIAL_REFRESH_LIMIT = 3
IDLE_TIMEOUT = 30  # seconds

# ------------------------
# Helper functions
# ------------------------
def load_scripts():
    scripts = [f for f in SCRIPTS_DIR.iterdir() if f.is_file() and f.suffix == ".sh"]
    return sorted(scripts)

MAX_LOGO_SIZE = (100, 100)  # maximum width/height on screen

def load_logo(script_name):
    logo_file = IMAGES_DIR / f"{script_name}.bmp"
    if logo_file.exists():
        img = Image.open(logo_file)
    else:
        img = Image.new("1", (100, 100), 1)
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([0,0,99,99], radius=20, fill=0)

    # scale down to fit max width/height
    img.thumbnail(MAX_LOGO_SIZE, Image.LANCZOS)
    return img


def draw_carousel(epd, scripts, selected_index):
    height, width = epd.width, epd.height
    display = Image.new("1", (width, height), 255)
    draw = ImageDraw.Draw(display)

    start_index = max(0, selected_index - VISIBLE_ITEMS//2)
    end_index = min(len(scripts), start_index + VISIBLE_ITEMS)
    items = scripts[start_index:end_index]

    # horizontal spacing
    x_spacing = width // VISIBLE_ITEMS
    y_center = height // 2
    for idx, script in enumerate(items):
        x_center = x_spacing * idx + x_spacing // 2

        logo = load_logo(script.stem)
        scale = CENTER_SCALE if start_index + idx == selected_index else SIDE_SCALE
        logo_w, logo_h = logo.size
        logo = logo.resize((int(logo_w*scale), int(logo_h*scale)))
        logo_w, logo_h = logo.size

        display.paste(logo, (x_center - logo_w//2, y_center - logo_h//2))

        if start_index + idx == selected_index:
            draw.rectangle([x_center - logo_w//2 - 2, y_center - logo_h//2 - 2,
                            x_center + logo_w//2 + 2, y_center + logo_h//2 + 2], outline=0)

    return display

# ------------------------
# Main
# ------------------------
def main():
    epd = epd2in13_V4.EPD()
    epd.init()
    epd.Clear()

    scripts = load_scripts()
    if not scripts:
        print("No scripts found!")
        return

    selected_index = 0
    partial_count = 0
    last_display = None
    last_activity = time.time()
    img = draw_carousel(epd, scripts, selected_index)
    epd.display(epd.getbuffer(img))
    # open FIFO
    with open(FIFO_PATH, "r") as fifo:
        while True:
            # check idle timeout
            if time.time() - last_activity > IDLE_TIMEOUT:
                epd.sleep()
                print("Display sleeping due to inactivity.")

            cmd = fifo.readline().strip()
            if not cmd:
                time.sleep(0.05)
                continue

            last_activity = time.time()
            changed = False

            if cmd == "triggerOne":
                if selected_index > 0:
                    selected_index -= 1
                    changed = True
            elif cmd == "triggerTwo":
                if selected_index < len(scripts) - 1:
                    selected_index += 1
                    changed = True
            elif cmd == "triggerThree":
                 epd.Clear()
                 epd.sleep()
                 os.execlp("bash", "bash", scripts[selected_index])
            if changed:
                img = draw_carousel(epd, scripts, selected_index)
                if img != last_display:
                    if partial_count < PARTIAL_REFRESH_LIMIT:
                        epd.display(epd.getbuffer(img))
                        partial_count += 1
                    else:
                        epd.display(epd.getbuffer(img))
                        partial_count = 0 #change later for partial refresh lol
                    last_display = img

def sleepyBye():
    epd = epd2in13_V4.EPD()
    epd.init()
    epd.Clear()
    epd.sleep()

if __name__ == "__main__":
    try:
        main()
    finally:
        sleepyBye()
