# Pipper Zero: What is it?
The Pipper Zero is a cross between the Pi Zero and the Flipper Zero. It has a basic launcher and I plan to add scripts for things such as BadUSB, IR blasting, and such. The Pi Zero 02W actually has a better processor than the Flipper and WiFi so with added hardware it should be better.

## Hardware:
I am using a Raspberry Pi 02W, Waveshare V4, and Pisugar 3. More scripts may require an IR transceiver, RTL-SDR dongle, GPS, or more. If you are okay with python it should be easy to port to something else.

## Pipper Installation
1. **Don't.** *Its not finished.*
2. Run `sudo raspi-config`, go to Interface Options, and ensure that SPI and I2C are both enabled.
3. Install the [Pisugar Power Manager](https://docs.pisugar.com/docs/product-wiki/battery/pisugar-power-manager) using `wget https://cdn.pisugar.com/release/pisugar-power-manager.sh && bash pisugar-power-manager.sh -c release`  
4. Run `sudo apt install git`  
5. Make the button shells `echo triggerOne > /path/to/pisugar_fifo` for click, `echo triggerTwo > /path/to/pisugar_fifo` for double click, and `echo triggerThree > /path/to/pisugar_fifo` for long clicks using the web ui on port 8421 of the pi.
6. Install dependencies: `sudo apt install python3-pillow<10 python3-setuptools`
7. Install waveshare stuff. I cloned [this repo](https://github.com/waveshareteam/e-Paper) using `git clone https://github.com/waveshareteam/e-Paper`, `cd ./e-Paper/RaspberryPi_JetsonNano/python`, and `python3 setup.py install`.  
8. Clone this repo. You might have to change some of the paths for it to work. `git clone https://github.com/g0lder/Pipper-Zero.git`
9. Run the launcher.  

## Make an app
1. Create the SH file in the scripts directory.
2. Add a logo with the same name but .bmp in the logos directory.
3. Congrats, you're done. Wow.

### TODO:
- Make the full refresh for the UI work better.  
- Make an install script to void all that crap.  
- Web UI.  
- BadUSB.  
- SDR sniffer.  
