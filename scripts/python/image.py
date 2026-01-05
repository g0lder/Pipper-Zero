#!/usr/bin/python 
# The resources directory should have a directory labeled pictures.
# --white flag can be set to true or false for background.
# --rotate <degrees> rotates the image clockwise
# Display size is 250 by 122 pixels

import sys 
import os 

# directory of picture 
try: 
    resources = os.path.join(sys.argv[1]) 
except IndexError: 
    print("Please provide the directory as an argument: python3 image.py /path/to/resources") 
    sys.exit(1) 

# library directory 
libdir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))),
    'lib'
)
if os.path.exists(libdir): 
    sys.path.append(libdir) 

# rest of the modules 
import logging  
from waveshare_epd import epd2in13_V4 
from PIL import Image

logging.basicConfig(level=logging.DEBUG)

# -------------------------------
# Parse flags
# -------------------------------
white_bg = True
rotate_degrees = 0

if "--white" in sys.argv:
    idx = sys.argv.index("--white") + 1
    if idx < len(sys.argv) and sys.argv[idx].lower() in ("false", "0"):
        white_bg = False

if "--rotate" in sys.argv:
    idx = sys.argv.index("--rotate") + 1
    if idx < len(sys.argv):
        try:
            rotate_degrees = float(sys.argv[idx])
        except ValueError:
            logging.error("Invalid value for --rotate. Must be a number.")
            sys.exit(1)

# -------------------------------
# Initialize EPD
# -------------------------------
try:
    logging.info("Initializing e-Paper display...")
    epd = epd2in13_V4.EPD()
    epd.init()
    epd.Clear(0xFF)
    epd_width, epd_height = epd.width, epd.height
    logging.info(f"EPD size: {epd_height}x{epd_width}")

    # -------------------------------
    # Load image
    # -------------------------------
    image_files = [
        f for f in os.listdir(resources)
        if f.lower().endswith((".bmp", ".png", ".jpg", ".jpeg"))
    ]
    if not image_files:
        logging.error("No image found in resources folder.")
        sys.exit(1)

    img_path = os.path.join(resources, image_files[0])
    logging.info(f"Displaying image: {image_files[0]}")

    img = Image.open(img_path)

    # -------------------------------
    # Rotate image
    # -------------------------------
    if rotate_degrees != 0:
        logging.info(f"Rotating image {rotate_degrees} degrees")
        img = img.rotate(-rotate_degrees, expand=True)

    # -------------------------------
    # Background handling
    # -------------------------------
    bg_color = 255 if white_bg else 0  # 255=white, 0=black
    background = Image.new("1", (epd_height, epd_width), color=bg_color)

    background.paste(img, (0, 0))
    img = background.convert("1")

    epd.display(epd.getbuffer(img))

    logging.info("Going to sleep...")
    epd.sleep()

except KeyboardInterrupt:
    logging.info("Ctrl+C pressed. Exiting...")
    epd2in13_V4.epdconfig.module_exit(cleanup=True)
    sys.exit(0)

except Exception as e:
    logging.error(f"Error: {e}")
    epd2in13_V4.epdconfig.module_exit(cleanup=True)
    sys.exit(1)
