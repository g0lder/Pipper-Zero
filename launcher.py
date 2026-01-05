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

VISIBLE_ITEMS = 5
CENTER_SCALE = 1.0
SIDE_SCALE = 0.6
SQUIRCLE_SIZE = (100, 100)
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

GRID_COLS = 3
GRID_ROWS = 2
ITEMS_PER_PAGE = GRID_COLS * GRID_ROWS
CELL_PADDING = 5  # padding inside each grid cell

def draw_grid(epd, scripts, selected_index):
    height, width = epd.width, epd.height
    display = Image.new("1", (width, height), 255)
    draw = ImageDraw.Draw(display)

    current_page = selected_index // ITEMS_PER_PAGE
    page_start = current_page * ITEMS_PER_PAGE
    page_end = min(len(scripts), page_start + ITEMS_PER_PAGE)

    cell_w = width // GRID_COLS
    cell_h = height // GRID_ROWS

    for page_offset, script in enumerate(scripts[page_start:page_end]):
        global_index = page_start + page_offset

        row = page_offset // GRID_COLS
        col = page_offset % GRID_COLS

        x_center = col * cell_w + cell_w // 2
        y_center = row * cell_h + cell_h // 2

        logo = load_logo(script.stem)

        # scale logo to fit cell with padding
        max_w = cell_w - 2 * CELL_PADDING
        max_h = cell_h - 2 * CELL_PADDING
        logo.thumbnail((max_w, max_h), Image.LANCZOS)

        logo_w, logo_h = logo.size

        display.paste(
            logo,
            (x_center - logo_w // 2, y_center - logo_h // 2)
        )

        if global_index == selected_index:
            draw.rectangle(
                [
                    x_center - logo_w // 2 - 3,
                    y_center - logo_h // 2 - 3,
                    x_center + logo_w // 2 + 3,
                    y_center + logo_h // 2 + 3,
                ],
                outline=0
            )

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
    idle = False
    selected_index = 0
    partial_count = 0
    last_display = None
    last_activity = time.time()
    img = draw_grid(epd, scripts, selected_index)
    time.sleep(0.2)
    epd.Clear()
    epd.display(epd.getbuffer(img))
    # open FIFO
    with open(FIFO_PATH, "r") as fifo:
        while True:
            # check idle timeout
            if time.time() - last_activity > IDLE_TIMEOUT:
                epd.sleep()
                print("Display sleeping due to inactivity.")
                idle = True

            cmd = fifo.readline().strip()
            if not cmd:
                time.sleep(0.05)
                continue

            last_activity = time.time()
            changed = False


            if cmd and idle==True:
                epd.init()
                img = draw_grid(epd, scripts, selected_index)
                epd.Clear()
                epd.display(epd.getbuffer(img))
                idle=False
            if cmd == "triggerOne":
                if selected_index < len(scripts) -1:
                    old_index=selected_index
                    selected_index += 1
                    changed = True
            elif cmd == "triggerTwo":
                if selected_index > 0:
                    old_index=selected_index
                    selected_index -= 1
                    changed = True
            elif cmd == "triggerThree":
                 epd.Clear()
                 epd.sleep()
                 os.execlp("bash", "bash", scripts[selected_index])
            if changed:
                img = draw_grid(epd, scripts, selected_index)
                if img != last_display:
                    if (old_index // ITEMS_PER_PAGE == selected_index // ITEMS_PER_PAGE) and (abs(old_index - selected_index) == 1) and ((old_index % ITEMS_PER_PAGE == 0) or (selected_index % ITEMS_PER_PAGE == 0)) and not (selected_index or old_index == 0):
                        epd.Clear()
                        epd.display(epd.getbuffer(img))
                    else:
                        epd.displayPartial(epd.getbuffer(img))
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
