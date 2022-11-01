#!/bin/bash

# General
pip3 install pyyaml
pip3 install schedule
pip3 install --upgrade numpy

# Sensors
sudo pip3 install adafruit-circuitpython-dht
sudo apt-get install libgpiod2

# Microphone
sudo pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/i2smic.py
printf '%s\n' y n | sudo python3 i2smic.py
yes | sudo apt-get install libatlas-base-dev libportaudio2 libasound-dev
yes | python3 -m pip install --user sounddevice
python3 -m pip install --user scipy
pip3 install SoundFile

# autostart
yes | sudo apt-get install xterm
mkdir -p ~/.config/autostart
cp /home/pi/station/lxterm-autostart.desktop ~/.config/autostart

# config interfaces -> enable camera and i2c
sudo raspi-config nonint do_camera 0
sudo raspi-config nonint do_i2c 0
