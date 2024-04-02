#!/usr/bin/python3
import tkinter as tk
from tkinter import messagebox, font, StringVar

import ruamel.yaml

import silolevel

GPIO1_PIN: int = 4
XSHUT_PIN: int = 26
i2cAddress: str = '0x29'


def read_configuration():
    print("Reading configuration file!")
    yaml = ruamel.yaml.YAML()
    with open("config.yaml", 'r') as stream:
        yaml_data = yaml.load(stream)
        stream.close()
    return yaml_data


def read_silolevel():
    silo = silolevel.SiloLevelSensor(gpio_gpio1=GPIO1_PIN, gpio_xshut=XSHUT_PIN, i2c_Address=i2cAddress)
    silolev = silo.read_plain_value()
    return silolev


class FutterSiloCheckerApp:
    option_var: StringVar
    languages: tuple[str, str]

    def __init__(self, mroot, empty_value: int = 0, full_value: int = 0, sensor_status: bool = True):
        self.chk_activate_Sensor = None
        self.opt_language = None
        self.lbl_activate_sensor = None
        self.btn_saveValue = None
        self.lbl_FullValue = None
        self.lbl_Step2 = None
        self.lbl_EmptyValue = None
        self.lbl_Step1 = None
        self.lbl_language = None
        self.lbl_titel = None
        self.btn_saveValues = None
        self.btn_capture_full = None
        self.btn_capture_empty = None
        self.root = mroot
        self.root.title("Futtersilo Sensor Abgleich")
        self.txt_EmptyValue = None
        self.txt_FullValue = None
        self.EmptyValue = empty_value
        self.FullValue = full_value
        self.sensor_status = sensor_status
        self.languages = ('Deutsch', 'English')
        self.option_var = tk.StringVar()
        self.chk_var = tk.BooleanVar()
        self.option_var.set(self.languages[0])
        self.langIndex = 0
        self.lbl_titel_text: tuple[str, str] = ("Mit diesem Tool wird der Futtersilosensor abgeglichen. Es werden die "
                                                "Werte erfasst wenn das Silo leer ist, und wenn das Silo komplett "
                                                "gefüllt ist.",
                                                "This tool is used to calibrate the feed silo sensor. The values are "
                                                "recorded "
                                                " when the silo is empty and when the silo is completely full.")
        self.lbl_language_text: tuple[str, str] = ("Sprache :", "Language :")
        self.lbl_Step1_text: tuple[str, str] = ("Schritt 1:", "Step 1:")
        self.lbl_Step2_text: tuple[str, str] = ("Schritt 2:", "Step 2:")
        self.btn_capture_text: tuple[str, str] = ("Erfassen", "Capture")
        self.lbl_EmptyValue_text: tuple[str, str] = (
            "Leeren Sie das Futtersilo komplett und achten Sie darauf, das der Sensor "
            "in Richtung boden zeigt und klicken Sie auf 'Erfassen'",
            "Empty the feed silo completely and make sure that the sensor "
            "is pointing towards the ground and click on 'Capture'")
        self.lbl_FullValue_text: tuple[str, str] = ("Legen Sie ein Stück Pappe o.ä. an der Oberkante des Silos "
                                                    "um ein volles Silo zu simulieren und klicken Sie auf 'Erfassen'",
                                                    "Place a piece of cardboard or similar on the top edge of the silo "
                                                    "to simulate a full silo and click on 'Capture'")
        self.btn_saveValues_text: tuple[str, str] = ("Werte speichern", "Save values")
        self.lbl_activate_sensor_text: tuple[str, str] = ("Futtersilosensor hier ein oder ausschalten",
                                                          "Silolevel Sensor activate or deactivate")
        self.chk_activate_sensor_text: tuple[str, str] = ("einschalten/ausschalten", "activate/deactivate")
        self.create_widgets()

    def create_widgets(self):

        bold_font = font.Font(weight=font.BOLD, size=11)

        self.lbl_titel = tk.Label(self.root,
                                  compound="left", justify="left",
                                  wraplength=500,
                                  text=self.lbl_titel_text[self.langIndex],
                                  font=bold_font
                                  )
        self.lbl_titel.grid(row=0, column=0, columnspan=2)

        self.lbl_language = tk.Label(self.root,
                                     compound="left", justify="right",
                                     wraplength=500,
                                     text=self.lbl_language_text[self.langIndex],
                                     )
        self.lbl_language.grid(row=0, column=2)

        self.opt_language = tk.OptionMenu(self.root,
                                          self.option_var,
                                          self.languages[0],
                                          *self.languages,
                                          command=self.language_changed
                                          )
        self.opt_language.grid(row=0, column=3)
        self.lbl_Step1 = tk.Label(self.root,
                                  justify="left",
                                  compound="left",
                                  wraplength=300,
                                  text=self.lbl_Step1_text[self.langIndex])
        self.lbl_Step1.grid(row=1, column=0, padx=5, pady=5)

        self.lbl_EmptyValue = tk.Label(self.root,
                                       justify="left",
                                       compound="left",
                                       wraplength=300,
                                       text=self.lbl_EmptyValue_text[self.langIndex])
        self.lbl_EmptyValue.grid(row=1, column=1, padx=5, pady=5)

        self.txt_EmptyValue = tk.Text(self.root,
                                      font=("Noto Mono", 14),
                                      height=1,
                                      width=3,
                                      relief=tk.RAISED
                                      )
        self.txt_EmptyValue.insert('1.0', str(self.EmptyValue))
        self.txt_EmptyValue.grid(row=1, column=3, padx=1, pady=5, )

        self.btn_capture_empty = tk.Button(self.root, text=self.btn_capture_text[self.langIndex],
                                           command=self.capture_empty)
        self.btn_capture_empty.grid(row=1, column=2, padx=1, pady=5)

        self.lbl_Step2 = tk.Label(self.root,
                                  justify="left",
                                  compound="left",
                                  wraplength=300,
                                  text=self.lbl_Step2_text[self.langIndex])
        self.lbl_Step2.grid(row=2, column=0, padx=5, pady=5)

        self.lbl_FullValue = tk.Label(self.root,
                                      justify="left",
                                      compound="left",
                                      wraplength=300,
                                      text=self.lbl_FullValue_text[self.langIndex])
        self.lbl_FullValue.grid(row=2, column=1, padx=5, pady=5)

        self.txt_FullValue = tk.Text(self.root,
                                     font=("Noto Mono", 14),
                                     height=1,
                                     width=3,
                                     relief=tk.RAISED)
        self.txt_FullValue.insert('1.0', str(self.FullValue))
        self.txt_FullValue.grid(row=2, column=3, padx=1, pady=5)

        self.btn_capture_full = tk.Button(self.root, text=self.btn_capture_text[self.langIndex],
                                          command=self.capture_full)
        self.btn_capture_full.grid(row=2, column=2, padx=1, pady=5)

        self.lbl_activate_sensor = tk.Label(self.root, text=self.lbl_activate_sensor_text[self.langIndex],
                                            justify=tk.LEFT,
                                            compound=tk.LEFT,
                                            wraplength=300)
        self.lbl_activate_sensor.grid(row=3, column=0, pady=5)
        
        if self.sensor_status:
            self.chk_var.set(True)
        #    self.chk_activate_Sensor.config(state=tk.ACTIVE)
                
        else:
            self.chk_var.set(False)
        #    self.chk_activate_Sensor.config(state=tk.DISABLED)
        
        self.chk_activate_Sensor = tk.Checkbutton(self.root,
                                                  text=self.chk_activate_sensor_text[self.langIndex],
                                                  onvalue=True,
                                                  offvalue=False,
                                                  command=self.activate_changed,
                                                  variable=self.chk_var)
       

        self.chk_activate_Sensor.grid(row=3, column=1, pady=5)

        self.btn_saveValues = tk.Button(self.root, text=self.btn_saveValues_text[self.langIndex],
                                        command=self.save_values)
        self.btn_saveValues.grid(row=4, column=3)

    def capture_empty(self):
        self.EmptyValue = read_silolevel()
        self.txt_EmptyValue.delete('1.0', tk.END)
        self.txt_EmptyValue.insert(tk.END, self.EmptyValue)

    def capture_full(self):
        self.FullValue = read_silolevel()
        self.txt_FullValue.delete('1.0', tk.END)
        self.txt_FullValue.insert(tk.END, self.FullValue)

    def language_changed(self, choice=None):
        choice = self.option_var.get()
        if choice == "Deutsch":
            self.langIndex = 0
        elif choice == "English":
            self.langIndex = 1
        self.lbl_titel.config(text=self.lbl_titel_text[self.langIndex])
        self.lbl_language.config(text=self.lbl_language_text[self.langIndex])
        self.lbl_Step1.config(text=self.lbl_Step1_text[self.langIndex])
        self.lbl_EmptyValue.config(text=self.lbl_EmptyValue_text[self.langIndex])
        self.lbl_Step2.config(text=self.lbl_Step2_text[self.langIndex])
        self.lbl_FullValue.config(text=self.lbl_FullValue_text[self.langIndex])
        self.btn_saveValues.config(text=self.btn_saveValues_text[self.langIndex])
        self.btn_capture_full.config(text=self.btn_capture_text[self.langIndex])
        self.btn_capture_empty.config(text=self.btn_capture_text[self.langIndex])
        self.chk_activate_Sensor.config(text=self.chk_activate_sensor_text[self.langIndex])
        self.lbl_activate_sensor.config(text=self.lbl_activate_sensor_text[self.langIndex])
        root.update()

    def activate_changed(self):
        choice = self.chk_var.get()
        if choice:
            self.sensor_status = True
        else:
            self.sensor_status = False

    def save_values(self):
        print("EmptyValue:", repr(self.EmptyValue))
        print("FullValue:", repr(self.FullValue))
        print("Sensor Status:", repr(self.sensor_status))
        e_value: int = self.EmptyValue
        f_value: int = self.FullValue
        if e_value > f_value:
            yaml = ruamel.yaml.YAML()
            with open("config.yaml", 'r') as stream:
                config_data = yaml.load(stream)
            config_data['hardware']['vl53l0x']['empty_value'] = self.EmptyValue
            config_data['hardware']['vl53l0x']['full_value'] = self.FullValue
            config_data['environment_values']['silolevel'] = self.sensor_status
            # write new values back to configuration file.
            with open("config.yaml", 'w') as stream:
                yaml.dump(config_data, stream)
                if self.langIndex == 0:
                    messagebox.showinfo(title="Speichern erfolgreich", message="Werte in config.yaml gespeichert")
                else:
                    messagebox.showinfo(title="Saving successful", message="Values save into config.yaml")
        else:
            if self.langIndex == 0:
                messagebox.showerror(title="Falsche Werte",
                                     message="Der Wert für das leere Silo muss größer Sein als für "
                                             "das volle Silo.\nBitte die Werte erneut ermitteln!")
            else:
                messagebox.showerror(title="Wrong Values",
                                     message="The value for the empty silo must be greater than for "
                                             "the full silo.\nPlease determine the values again!")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry('800x300+50+50')
    root.resizable(width=tk.FALSE, height=tk.FALSE)
    root.columnconfigure(4, weight=1)
    root.rowconfigure(5, weight=1)
    config_yaml = read_configuration()
    GPIO1_PIN = config_yaml['hardware']['vl53l0x']['GPIO1_PIN']
    XSHUT_PIN = config_yaml['hardware']['vl53l0x']['XSHUT_PIN']
    i2cAddress = config_yaml['hardware']['vl53l0x']['i2cAddress']
    app = FutterSiloCheckerApp(root, empty_value=config_yaml['hardware']['vl53l0x']['empty_value'],
                               full_value=config_yaml['hardware']['vl53l0x']['full_value'],
                               sensor_status=config_yaml['environment_values']['silolevel'])
    root.mainloop()
