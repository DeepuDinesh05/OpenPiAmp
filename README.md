# OpenPiAmp
(WIP) Open source WinAmp style music player for Raspberry Pi Zero 2 W.

# Table of Contents
- [Dependencies](#dependencies)
- [Hardware](#hardware)
- [Installation](#installation)
  - [Virtual Environment (Pi)](#virtual-environment-pi)
  - [Calibration](#calibration)
  - [How To Run](#how-to-run)
- [Custom Themes](#custom-themes)
- [To Do](#to-do)

# Hardware
The hardware setup I plan to build for is as follows:
- Raspberry Pi Zero 2 W (Pi OS Lite 64 Bit)
- [2.4" (320x240) SPI Interface TFT Screen](https://www.aliexpress.com/item/1005005770033042.html)
    - Drivers for these screens can be found here: 
        - https://github.com/katzenjens/lcd32 (Recommended)
        - https://github.com/goodtft/LCD-show (Old)

# Installation

## Screen Drivers
- To get the terminal to show up in case you're using the old drivers, you need to map the console output to framebuffer.
- I've provided a script that runs this as a service on boot, which can be executed by running:
```bash
bash con2fbmap_old_drivers.sh
``` 

## Virtual Environment (Pi)
On the Pi, set up a venv inside the project folder to prevent dependency isolation errors:

```bash
cd OpenPiAmp
python3 -m venv .venv
source .venv/bin/activate

sudo apt update
sudo apt install -y python3-dev build-essential
pip install evdev

pip install pygame mutagen
```
Default music directory provided is the ~/Music path, which on windows can be accessed by going to File Explorer > Music folder. On the Pi, it will be expected to make a folder called Music at the root.

## Calibration

For touch based calibration, you will have to run your screen driver provided rotate script first. For example:

```bash
cd LCD-show/
sudo ./rotate.sh 180 
```

And run evtest input test tool:
```sudo evtest /dev/input/event0```

Use the smallest ABS values for better results.

## How To Run

- For a quick test run, you can executed the provided bash script
```bash 
bash run.sh
```

- To use the application as a service on boot, you can run the provided bash script:
```bash 
bash autoboot_install.sh
```

- To remove the application as a service on boot, you can run the provided bash script:
```bash 
bash autoboot_uninstall.sh
```


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
