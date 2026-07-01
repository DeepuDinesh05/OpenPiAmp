# OpenPiAmp
(WIP) Open source WinAmp style music player for Raspberry Pi Zero 2 W.  Currently being tested on windows before port.

## Table of Contents
- [Dependencies](#dependencies)
- [Hardware](#hardware)
- [Installation](#installation)
- [Calibration](#calibration)
- [Custom Themes](#custom-themes)
- [To Do](#to-do)

# Hardware
The hardware setup I plan to build for is the follow:
- Raspberry Pi Zero 2 W
- [2.4" (320x240) SPI Interface TFT Screen](https://www.aliexpress.com/item/1005005770033042.html)

# Installation
Currently, this is in testing stage while I get the screen drivers and other hardware for the Raspberry Pi Zero 2 W sorted. 

```
python app.py
```

## Virtual Environment (Pi)
On the Pi, set up a venv inside the project folder so dependencies stay isolated:

```bash
cd OpenPiAmp
python3 -m venv .venv
source .venv/bin/activate

sudo apt update
sudo apt install -y python3-dev build-essential
pip install evdev

pip install pygame mutagen evdev
```
Reactivate it in future sessions with:
```bash
source .venv/bin/activate
```
> **⚠️ Disclaimer:** Custom boot logic to run the application on boot will be worked on in future commits

Default music directory provided is the ~/Music path, which on windows can be accessed by going to File Explorer > Music folder. On the Pi, it will be expected to make a folder called Music at the root.

# Calibration

For touch based calibration, you will have to run your screen driver provided rotate script first. For example:

```bash
cd LCD-show/
sudo ./rotate.sh 180 
```

And run evtest input test tool:
```sudo evtest /dev/input/event0```

Use the smallest ABS values for better results.

# Custom Themes

- A HTML/JS based theme editor is provided in the ```assets/theme_editor``` folder. 
> **⚠️ Disclaimer:** The JS logic behind this tool was built with agentic help and will be rewritten as a learning exercise at a later stage as my goal is to learn python for raspberry pi hardware projects.

- Open ```index.html```in any browser (tested on chrome) and save the theme using the action button provided.
- Name your theme appropriately and place it in the assets folder.
- Edit the config.py file to use your theme of choice on startup.

# To Do
- Port to Pi
- Finalize audio components for audio playback on the Pi Zero 2
- Figure out how to connect portable power source
- Design 3D enclosure