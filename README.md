# OpenPiAmp
(WIP) Open source WinAmp style music player for Raspberry Pi Zero 2 W.  Currently being tested on windows before port.

## Table of Contents
- [Dependencies](#dependencies)
- [Hardware](#hardware)
- [Installation](#installation)
- [Custom Themes](#custom-themes)
- [To Do](#to-do)

# Dependencies
Install the following packages:
```
pip install pygame mutagen
```
# Hardware
The hardware setup I plan to build for is the follow:
- Raspberry Pi Zero 2 W
- [2.4" (320x240) SPI Interface TFT Screen](https://www.aliexpress.com/item/1005005770033042.html)

# Installation
Currently, this is in testing stage while I get the screen drivers and other hardware for the Raspberry Pi Zero 2 W sorted. As such, you can run this on windows (or view preview.png) as follows:

```
python app.py
```

Default music directory provided is the ~/Music path, which on windows can be accessed by going to File Explorer > Music folder. On the Pi, it will be expected to make a folder called Music at the root.

# Custom Themes

- A HTML/JS based theme editor is provided in the ```assets/theme_editor``` folder. 
> **⚠️ Disclaimer:** The JS logic behind this tool was built with agentic help and will be rewritten at a later stage.

- Open ```index.html```in any browser (tested on chrome) and save the theme using the action button provided.
- Name your theme appropriately and place it in the assets folder.
- Edit the config.py file to use your theme of choice on startup.

# To Do
- Port to Pi
- Finalize audio components for audio playback on the Pi Zero 2
- Figure out how to connect portable power source
- Design 3D enclosure