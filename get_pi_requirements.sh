#!/bin/bash
#get latest raspbian os packages
testfile=~/station/restartmarker

if test -f "$testfile";
then
  printf "\033[0;35m####### Welcome Back we will proceed with the tasks #######\n\n"
  rm restartmarker
else
  printf "\033[0;35m####### Getting latest raspbian os packages#######\n\n"
  sudo apt update
  sudo apt upgrade -y
  printf "\033[0;35mWhen packages where updated, it´s a good decision to make a restart at this point, and run the script again.\033[0m\n"
  printf "\033[0;35mRestart now y/n ?[n]\033[0m\n"
  read -t 10 -n 1 Result

  if [ "$Result" == y ]
  then
    printf "#####  Restart now ####\n"
    printf "#####  BYE! ####\n"
    touch restartmarker
    sudo shutdown -r now System will perform reqboot
  else
    printf "\033[0;35m######  Restart skipped  ######\033[0m\n"
  fi
fi
printf "\033[0;35m####### Install general python packages#######\033[0m\n"
# General
pip3 install pyyaml
pip3 install schedule
pip3 install --upgrade numpy

printf "\033[0;35m####### Install Senors #######\033[0m\n"
# Sensors
sudo pip3 install adafruit-circuitpython-dht
sudo apt-get install libgpiod2

# Microphone
sudo pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/i2smic.py
printf '%s\n' y n | sudo python3 i2smic.py
yes | sudo apt-get install libatlas-base-dev libportaudio2 libasound-dev gfortran libopenblas-dev cmake python3-pydub
yes | python3 -m pip install --user sounddevice
python3 -m pip install --user scipy
pip3 install SoundFile

printf "\033[0;35m####### Set Autostart #######\033[0m\n"
# autostart
yes | sudo apt-get install xterm
mkdir -p ~/.config/autostart
cp ~/station/lxterm-autostart.desktop ~/.config/autostart
sed -i 's,~/station,'"$HOME"'/station,g' birdiary.desktop
cp ~/station/birdiary.desktop ~/Desktop
printf "\033[0;35m####### config interfaces -> enable camera and i2c #######\033[0m\n"
# config interfaces -> enable camera and i2c
sudo raspi-config nonint do_camera 0
sudo raspi-config nonint do_legacy 0
sudo raspi-config nonint do_vnc 0
sudo raspi-config nonint do_i2c 0
# activate the HDMI output, even if no monitor is detected
sudo sed -i '3ahdmi_force_hotplug=1' /boot/config.txt
sudo sed -i '4ahdmi_mode=16' /boot/config.txt


printf "\033[0;35m\n#######            Finished                  #######\n"
printf "\033[0;35m             )    \n"
printf "\033[0;35m             \   )   \n"
printf "\033[0;35m             ()  \                           )\n"
printf "\033[0;35m                 ()                       )  \\n"
printf "\033[0;35m                       .-\"\"\"-.            \\  \(\)\n"
printf "\033[0;35m              ____    \/  __   \`\\     __   \(\)\n"
printf "\033[0;35m           .'\`  __'. | o/__\o   |   / /|\n"
printf "\033[0;35m          /  o /__\o;\  \\//   /_  // /\n"
printf "\033[0;35m ._      _|    \\// |\`-.__.-'|\  \`;  /\n"
printf "\033[0;35m/  \   .'  \-.____.'|   ||   |/    \/\n"
printf "\033[0;35m\`._ '-/             |   ||   '.___./\n"
printf "\033[0;35m.  '-.\_.-'      __.'-._||_.-' _ /\n"
printf "\033[0;35m.\`""===(||).___.(||)(||)----'(||)===...__\n"
printf "\033[0;35m \`\"jgs\"\`\"\"=====\"\"\"\"========\"\"\"====...__  \`\"\"==._\n"
printf "\033[0;35m                                       \`\"=.     \`\"=.\n"
printf "\033[0;35m                                           \`\"=.\n"
printf "\033[0;35m Art by Joan Stark (https://www.asciiart.eu/animals/birds-land)\n"
