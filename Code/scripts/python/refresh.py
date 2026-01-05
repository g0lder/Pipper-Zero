#!/usr/bin/python3
from waveshare_epd import epd2in13_V4
epd = epd2in13_V4.EPD()
epd.init()
epd.Clear()
epd.sleep()
