# Vorbereitung Pi 
- Installiere den Raspberry Pi Imager auf deinem lokalen Computer (Den Imager findest du hier: https://www.raspberrypi.com/software/)
- Verbinde die SD Karte, die später einmal im Raspberry Pi genutzt wird, mit deinem Computer 
- Da alle Daten auf der SD Karte gelöscht werden, solltest du eventuelle Daten vor den folgenden Schritten abgespeichert haben 
- Starte den Raspberry Pi Imager und wähle dann im User Interface "Raspberry PI OS (32-BIT)" als Betriebssystem aus 
- Wähle im User Interface des Raspberry Pi Imager, die SD Karte aus, die du eben mit deinem Computer verbunden hast 
- Um den Prozess, der Betriebssystemübertragung zu beginnen, wähle entsprechend "SCHREIBEN" aus 
- Bestätige, dass alle Daten auf der SD Karte gelöscht werden können 
- Sobald die Bestätigung angezeigt wird, dass "Raspberry Pi OS (32-bit)" auf der eingelegten SD Karte gespeichert wurde, kann diese vom Computer entfernt werden und in den Raspberry Pi eingelegt werden 
- Nutze zwei der vier USB Ports am Raspberry Pi um sowohl Tastatur, als auch eine Maus an den Raspberry Pi anzuschließen 
- Nutze den Mini-HDMI Port mit der Aufschrift "HDMI0" um einen Bildschrim mit dem Raspberry Pi zu verbinden
- Optional wäre über "HDMI1" ein weiter Bildschirm verbindbar 
- Schließe ein USB-C Kabel an der Buchse mit der Bezeichnung "POWER IN" an, um den Raspberry Pi mit dem Strom zu verbinden 
- Sofern dein Bildschirm eingeschaltet ist, sollte der Raspberry Pi nun starten und eine graphische Nutzerberfläche angezeigt werden 

# initiales Starten Raspberry Pi  
- Es kann sein, dass es zu der Meldung kommt "Resized root file system. Rebooting in 5 seconds". Dann einfach abwarten und der Raspberry Pi startet selbständig erneut 
- Erscheint die Oberfläche, gilt es noch einige Einstellungen durchzuführen 
- Zunächst können Land, Sprache und Zeitzone eingestellt werden 
- Anschließend können Nutzername und Passwort spezifiziert werden 
- Anschließend kann die Bildschirmgröße angepasst werden 
- Dann ist es möglich, dass WiFi Network festzulegen, dies am besten gleich tun 
- Anschließend kann optional das Betriebssystem aktualisiert werden 
- Mit einem Neustart wird der Raspberry Pi dann nutzbar  

# initiales Setup Raspberry Pi 
## Kamera 
- Eingabe im Terminal: `sudo raspi-config`
- Auswahl von: 3 Interface Options  
- Auswahl von: I1 Legacy Camera
- Auswahl von: Ja
- Auswahl von: Finish  

## Installation verschiedener Pakete 
- Eingabe im Terminal: `pip3 install pyyaml` (Definition der Parameter)
- Eingabe im Terminal: `pip3 install schedule` (zeitliche Wiederholung der Umweltdaten Sendung)
- Eingabe im Terminal: `pip3 install --upgrade numpy`

## Luftfeuchte und Temperatur Sensor 
- Eingabe im Terminal: `sudo pip3 install adafruit-circuitpython-dht`
- Eingabe im Terminal: `sudo apt-get install libgpiod2`

## Mikrofon 
- Eingabe im Terminal: `sudo pip3 install --upgrade adafruit-python-shell`
- Eingabe im Terminal: `wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/i2smic.py`
- Eingabe im Terminal: `sudo python3 i2smic.py`
- Für die vorherigen drei Schritte ist eine detaillierte Anleitung unter folgendem Link zu finden: https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout/raspberry-pi-wiring-test 
- Eingabe im Terminal: `sudo apt-get install libatlas-base-dev libportaudio2 libasound-dev`
- Eingabe im Terminal: `python3 -m pip install --user sounddevice`
- Eingabe im Terminal: `python3 -m pip install --user scipy`
- Für die vorherigen drei Schritte ist eine detaillierte Anleitung unter folgendem Link zu finden: https://github.com/Infineon/i2s-microphone/wiki/Raspberry-Pi-Audio-Processing-with-Python 

# Hardware anschließen 

## Kamera 
- Das breite Kamerakabel an einem Ende an die Kamera anschließen und am anderen Ende an den RasperryPi (an den Anschluss der mit Kamera betitelt ist), so, dass das blaue Ende zu den USB Anschlüssen zeigt 
- Das Kabel lässt sich sowohl an Pi als auch an Kamera durch das hochziehen, der grauen Abdeckung befestigen. Dieses anschließend wieder runterdrücken um das Kabel zu fixieren 

## Luftfeuchte und Temperatursensor 
- "+" -> Port 1 (3,3 V)
- Out -> Port 36 (GPIO 16)
- "-" -> Port 9 (GND) 

## Waage 
- VCC -> Port 2 (5 V)  
- SCK -> Port 16 (GPIO 23) 
- DT  -> Port 11 (GPIO 17)
- GND -> Port 6 (GND)

## Mikrofon 
- SEL -> Port 39 (GND)
- RCL -> Port 35 (GPIO 19)
- OUT -> Port 38 (GPIO 20)
- CLK -> Port 12 (GPIO 18) 
- GND -> Port 20 (GND)
- 3V  -> Port 17 (3,3 V)

# Setup Birdiary 
- Eingabe im Terminal: `cd /home/pi/`
- Eingabe im Terminal: `git clone https://github.com/CountYourBirds/station.git` 

# Ermöglichung des Zugriffs auf den Raspberry Pi via VNC  
- Eingabe im Terminal: `sudo nano /boot/config.txt` (detaillierte Anleitung für die Veränderung der Datei hier: https://www.shellhacks.com/raspberry-pi-force-hdmi-hotplug/)
- Setze den Paramter hdmi_force_hotplug auf 1: `hdmi_force_hotplug=1` 
- Setze den Parameter hdmi_group auf 1: `hdmi_group=1`
- Setze den Parameter hdmi_mode auf 16: `hdmi_mode=16`
- Eingabe im Terminal: `sudo raspi-config`
- Auswahl von: 2 Display Options
- Auswahl von: D5 VNC Resolution  
- Auswahl von: 1920x1080
- Auswahl von: OK
- Auswahl von: 3 Interface Options 
- Auswahl von: VNC 
- Auswahl von: Ja 
- Kurz abwarten und das `VA` Icon anklicken oben rechts neben dem WLAN Zeichen 
- IP Adresse die unter Konnektivität gelistet ist auf Rechner der auf PI zugreifen soll im VNC Viewer eintragen (vorheriger Download der VNC Viewer App für entsprechendes Betriebssystem: https://www.realvnc.com/de/connect/download/viewer/) und mit dem Raspberry Pi verbinden  
- Passwort und Benutzername des pis entsprechend eintragen
- Verbindung sollte funktioneren  

# Automatische Ausführung ermöglichen 
- Eingabe im Terminal: `sudo apt-get install xterm`
- Eingabe im Terminal: `mkdir -p ~/.config/autostart`
- Eingabe im Terminal: `nano ~/.config/autostart/lxterm-autostart.desktop`
- In der Datei einfügen: 
`[Desktop Entry]
Encoding=UTF-8
Name=Terminal autostart
Comment=Start a terminal and list directory
Exec=/usr/bin/lxterm -e 'bash /home/pi/station/startup.sh'` 
- `Strg`+ `O` 
- `Enter`
- Eingabe im Terminal: `sudo restart`
