#!/usr/bin/python3
import os
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
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
IDLE_TIMEOUT = 45  # seconds

# ------------------------
# Helper functions
# ------------------------
def load_scripts():
    scripts = [f for f in SCRIPTS_DIR.iterdir() if f.is_file() and f.suffix == ".sh"]
    return sorted(scripts)

MAX_LOGO_SIZE = (50,50)

def load_logo(script_name):
    # Start with placeholder or load logo
    logo_file = IMAGES_DIR / f"{script_name}.bmp"
    if logo_file.exists():
        img = Image.open(logo_file).convert("1")
    else:
        img = Image.new("1", (MAX_LOGO_SIZE[0], MAX_LOGO_SIZE[1]), 1)
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([0,0,MAX_LOGO_SIZE[0]-1,MAX_LOGO_SIZE[1]-1], radius=20, fill=0)

    # Resize logo to fit max size while preserving aspect ratio
    img.thumbnail(MAX_LOGO_SIZE, Image.LANCZOS)

    # Draw text on top
    draw = ImageDraw.Draw(img)

    # Start with max font size and shrink until text fits
    font = ImageFont.truetype(os.path.join(SELF_PATH, 'scripts', 'resources', 'text', 'Font.ttf'), 9)
    bbox = draw.textbbox((0, 0), script_name, font=font)
    w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]

    # Center and draw text on a white background
    padding = 2  # small padding around text
    text_x = (img.width - w) / 2
    text_y = img.height - h - padding - 1

    # Draw white rectangle behind text
    #draw.rectangle(
    #    [text_x - padding, text_y - padding, text_x + w + padding, text_y + h + padding],
    #    fill=255  # white background
    #)

    draw.rectangle(
        [0, text_y - padding, 50, text_y + h + padding],
        fill=255
    )

    # Draw the text itself
    draw.text((text_x, text_y), script_name, fill=0, font=font)

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
    idle_time = 0
    # open FIFO
    with open(FIFO_PATH, "r") as fifo:
        while True:
            # check idle timeout
            if time.time() - last_activity > IDLE_TIMEOUT:
                epd.sleep()
                print("Display sleeping due to inactivity.")
                idle = True
                if time.time() - last_activity > IDLE_TIMEOUT+1:
                    os.execlp("bash","bash",f"{SCRIPTS_DIR}/resources/showerThoughts.sh")

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
                idle_time = 0
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
                 time.sleep(5)
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
    except Exception as e:
        print(e)
        sleepyBye()
