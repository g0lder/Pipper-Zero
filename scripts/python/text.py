#!/usr/bin/python
import os
resources = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'resources'),'text')
import logging
import traceback
import argparse
from waveshare_epd import epd2in13_V4
from PIL import Image,ImageDraw,ImageFont

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("Display Text")
    
    epd = epd2in13_V4.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear(0xFF)

    font = ImageFont.truetype(os.path.join(resources, 'Font.ttf'), 15)

    if 1:
        logging.info("Refresh...")
        epd.init()
        logging.info("Drawing Text...")
        image = Image.new('1', (epd.height, epd.width), 255) #255 clears the frame
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
                fontWSize = ImageFont.truetype(
                        os.path.join(resources, 'Font.ttf'),
                        int(size)
                )
                draw.text((int(x),int(y)), string, font=fontWSize)
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

