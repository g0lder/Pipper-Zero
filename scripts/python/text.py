#!/usr/bin/python
import os
import logging
import argparse
from waveshare_epd import epd2in13_V4
from PIL import Image, ImageDraw, ImageFont

# Path to resources
resources = os.path.join(
    os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'resources'), 'text'
)

logging.basicConfig(level=logging.DEBUG)

def wrap_text(draw, text, font, max_width):
    """
    Wrap text to fit within max_width in pixels.
    Returns a list of lines.
    """
    words = text.split()
    lines = []
    line = ""
    for word in words:
        test_line = line + (" " if line else "") + word
        bbox = draw.textbbox((0,0), test_line, font=font)
        w = bbox[2] - bbox[0]  # width of test_line
        if w <= max_width:
            line = test_line
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

try:
    logging.info("Display Text")
    
    epd = epd2in13_V4.EPD()
    logging.info("Init and Clear")
    epd.init()
    epd.Clear(0xFF)

    font_path = os.path.join(resources, 'Font.ttf')

    logging.info("Drawing Text...")
    # Create a blank image
    image = Image.new('1', (epd.height, epd.width), 255)  # height/width swap is common for 2.13" screens
    draw = ImageDraw.Draw(image)

    parser = argparse.ArgumentParser(description="Get text")
    parser.add_argument(
        "--text",
        action="append",
        nargs=4,
        metavar=("STRING", "X", "Y", "SIZE"),
        help="Format: --text STRING x y size (repeatable)"
    )

    args = parser.parse_args()

    if args.text:
        for string, x, y, size in args.text:
            fontWSize = ImageFont.truetype(font_path, int(size))
            x = int(x)
            y = int(y)

            # Wrap text to fit the screen width
            max_width = epd.height - x  # leave margin
            lines = wrap_text(draw, string, fontWSize, max_width)

            # Draw each line
            bbox = draw.textbbox((0,0), 'A', font=fontWSize)
            line_height = bbox[3] - bbox[1]  # approximate line height
            for line in lines:
                draw.text((x, y), line, font=fontWSize, fill=0)
                y += line_height+3

    else:
        logging.warning("No --text STRING X Y provided.")

    epd.display(epd.getbuffer(image))
    logging.info("Finishing...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("Rude")
    epd2in13_V4.epdconfig.module_exit(cleanup=True)
    exit()
