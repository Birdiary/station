# Vorbereitung Pi 
- Installiere den Raspberry Pi Imager auf deinem lokalen Computer (Den Imager findest du hier: https://www.raspberrypi.com/software/)
- Verbinde die SD Karte, die später einmal im Raspberry Pi genutzt wird, mit deinem Computer (in der Regel kannst du die Micro SD Karte mit einem beigelegten Adapter in deinen PC stecken)
  - Da alle Daten auf der SD Karte gelöscht werden, solltest du eventuelle Daten vor den folgenden Schritten abgespeichert haben 
  - Starte den Raspberry Pi Imager und wähle dann im User Interface "Raspberry PI OS (32-BIT)" als Betriebssystem aus 
    - Wähle im User Interface des Raspberry Pi Imager, die SD Karte aus, die du eben mit deinem Computer verbunden hast 
    - Um den Prozess, der Betriebssystemübertragung zu beginnen, wähle entsprechend "SCHREIBEN" aus 
    - Bestätige, dass alle Daten auf der SD Karte gelöscht werden können 
  - Sobald die Bestätigung angezeigt wird, dass "Raspberry Pi OS (32-bit)" auf der eingelegten SD Karte gespeichert wurde, kann diese vom Computer entfernt werden und in den Raspberry Pi eingelegt werden (der Slot dafür ist auf der Unterseite des RaspberryPi, gegenüber der USB-Anschlüsse)
    - Solange das Überspielen auf die SD-Karte läuft, können schon die nächsten Schritte bis zum Stromanschluss durchgeführt werden  
- Nutze zwei der vier USB Ports am Raspberry Pi um sowohl Tastatur, als auch eine Maus an den Raspberry Pi anzuschließen 
- Nutze den Mini-HDMI Port mit der Aufschrift "HDMI0" um einen Bildschrim mit dem Raspberry Pi zu verbinden
- Optional wäre über "HDMI1" ein weiter Bildschirm verbindbar 
- Schließe das RaspberryPi Netzteil an der Buchse mit der Bezeichnung "POWER IN" an, um den Raspberry Pi mit dem Strom zu verbinden 
- Sofern dein Bildschirm eingeschaltet ist, sollte der Raspberry Pi nun starten und eine graphische Nutzerberfläche angezeigt werden, dies kann ein paar Minuten dauern. 

# initiales Starten Raspberry Pi  
- Es kann sein, dass es zu der Meldung kommt "Resized root file system. Rebooting in 5 seconds". Dann einfach abwarten und der Raspberry Pi startet selbständig erneut 
- Erscheint die Oberfläche, gilt es noch einige Einstellungen durchzuführen 
  - Zunächst können Land, Sprache und Zeitzone eingestellt werden 
  - Anschließend können Nutzername und Passwort spezifiziert werden (in der Regel 
  - Anschließend kann die Bildschirmgröße angepasst werden 
  - Dann ist es möglich, dass WiFi Network festzulegen, dies am besten gleich tun 
- Anschließend kann optional das Betriebssystem aktualisiert werden 
- Mit einem Neustart wird der Raspberry Pi dann nutzbar  

# initiales Setup Raspberry Pi 
Für die folgenden Schritte öffnest du am einfachsten dieses Repository in dem Browser (Globus Icon, oben links neben der Himbeere) deines Raspberry Pi, um die Kommandos zu kopieren. 

Zur Info: Eingaben im Terminal können getätigt werden, wenn die (grüne) Zeile `pi@raspberry: ~ $` erscheint. Dies ist auch das Zeichen für eine abgeschlossene Eingabe / Installation.

## Kamera 
- Öffne das Terminal (Shortcut: Strg + Alt + T)
- Eingabe im Terminal: `sudo raspi-config`
  - Navigation mit Pfeiltasten
  - Auswahl von: 3 Interface Options  
  - Auswahl von: I1 Legacy Camera
  - Auswahl von: Ja
  - Auswahl von: Finish  
  - Auswahl von: Ja (Reboot)

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
  - Bestätige 'Load on reboot' mit `y` -> Enter
- Für die vorherigen drei Schritte ist eine detaillierte Anleitung unter folgendem Link zu finden: https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout/raspberry-pi-wiring-test 
- Eingabe im Terminal: `sudo apt-get install libatlas-base-dev libportaudio2 libasound-dev gfortran libopenblas-dev cmake python3-pydub`
- Eingabe im Terminal: `python3 -m pip install --user sounddevice`
  - Gegebenenfalls im Terminal bestätigen durch die Eingabe von `j` und Enter. 
- Eingabe im Terminal: `python3 -m pip install --user scipy`
- Für die vorherigen drei Schritte ist eine detaillierte Anleitung unter folgendem Link zu finden: https://github.com/Infineon/i2s-microphone/wiki/Raspberry-Pi-Audio-Processing-with-Python 
- Eingabe im Terminal: `pip3 install SoundFile`

# Hardware anschließen 

Die Belegung und Nummerierung der Pins / Ports des Raspberry Pi kann unter anderem hier nachgeguckt werden: https://www.raspberrypi-spy.co.uk/wp-content/uploads/2012/06/Raspberry-Pi-GPIO-Header-with-Photo.png 

## Kamera 
- Das breite weiße Kamerakabel an einem Ende an die Kamera anschließen und am anderen Ende an den RasperryPi (an den Anschluss der mit Kamera betitelt ist), so, dass das blaue Ende zu den USB Anschlüssen zeigt 
- Das Kabel lässt sich sowohl an Pi als auch an Kamera durch das hochziehen, der grauen Abdeckung befestigen. Dieses anschließend wieder runterdrücken um das Kabel zu fixieren 

## Luftfeuchte und Temperatursensor 
- "+" -> Port 1 (3,3 V)
- Out -> Port 36 (GPIO 16)
- "-" -> Port 9 (GND) 

## Waage 
- Kabel von der Waage (Dehnungsmessstreifen) zur Wägezelle:
  - Rot: E+ 
  - Schwarz: E-
  - Grün: A-
  - Weiß: A+
- Kabel vom Pi zur Wägezelle:
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
(Je nachdem mit welchen Benutzer man sich am RaspberryPi anmeldet, können die Verzeichnisse abweichen. Solltest du dich nicht mit dem Benutzer 'pi' anmelden, musst du den Verzeichnisnamen gegen Deinen austauschen. Aus /home/pi wird dann /home/<dein Benutzer>)
- Eingabe im Terminal: `cd /home/pi/`
- Eingabe im Terminal: `git clone https://github.com/CountYourBirds/station.git` 
- Erstelle unter https://wiediversistmeingarten.org/react/createbox deine eigene Station
- Kopiere die Box-Id in die config.yaml-Datei im Ordner `/home/pi/station`
- Navigiere in den Ordner station und öffne die `config.yaml`-Datei mit geany (Rechtsclick auf die Datei -> Geany)
  - Kopiere die Box-id an die entsprechende Stelle in der Datei
  - Speichere die Datei (Shortcut: Str + S)

# Ermöglichung des Zugriffs auf den Raspberry Pi via VNC  
- Eingabe im Terminal: `sudo nano /boot/config.txt` (detaillierte Anleitung für die Veränderung der Datei hier: https://www.shellhacks.com/raspberry-pi-force-hdmi-hotplug/)
  - Navigiere mit den Pfeiltasten der Tastatur zu den den folgenden Zeilen, entferne die Rauten am Anfang der Zeilen und nimm die entsprechenden Anpassungen vor:
    - Setze den Paramter hdmi_force_hotplug auf 1: `hdmi_force_hotplug=1`  
    - Setze den Parameter hdmi_group auf 1: `hdmi_group=1`
    - Setze den Parameter hdmi_mode auf 16: `hdmi_mode=16`
  - Zum Speichern: 
    - `Strg`+ `O` 
    - `Enter`
    - `Strg`+ `X` 
- Eingabe im Terminal: `sudo raspi-config`
  - Auswahl von: 2 Display Options
  - Auswahl von: D5 VNC Resolution  
  - Auswahl von: 1920x1080
  - Auswahl von: OK
  - Auswahl von: 3 Interface Options 
  - Auswahl von: VNC 
  - Auswahl von: Ja 
  - Auswahl von: Finish
  - Auswahl von: Ja (Reboot)
- Kurz abwarten und das `Va` Icon anklicken oben rechts neben dem WLAN Zeichen 
- IP Adresse die unter Konnektivität gelistet ist auf Rechner der auf PI zugreifen soll im VNC Viewer eintragen (vorheriger Download der VNC Viewer App für entsprechendes Betriebssystem: https://www.realvnc.com/de/connect/download/viewer/) und mit dem Raspberry Pi verbinden  
- Passwort und Benutzername des pis entsprechend eintragen
- Verbindung sollte funktioneren  

# Automatische Ausführung ermöglichen 
- Eingabe im Terminal: `sudo apt-get install xterm`
  - Bestätigung mit `J` -> Enter  
- Eingabe im Terminal: `mkdir -p ~/.config/autostart`
  - (Das Terminal gibt kein Feedback bei erfolgreicher Ausführung, außer, dass eine neue Zeile und keine Fehlermeldung erscheinen)  
- Eingabe im Terminal: `nano ~/.config/autostart/birdiary.desktop`
- In der Datei einfügen: 
```
[Desktop Entry]
Name=Birdiary Script Start
Comment=Start Birdiary via terminal
Exec=/usr/bin/lxterm -e 'bash ~/station/startup.sh & bash ~/station/internetTest.sh'
Type=Application
Terminal=true
Icon=~/station/files/birdiary.png
Categories=Utility;
```
- `Strg`+ `O` 
- `Enter`
- Eingabe im Terminal: `nano ~/.Xresources`
- In der Datei einfügen: 
```
xterm*faceName: UbuntuMono
xterm*faceSize: 10
```
- Eingabe im Terminal: `xrdb -merge ~/.Xresources`
- Eingabe im Terminal: `sudo reboot`
