import tkinter
import customtkinter as ct
#demo
class Sensor:
    def __init__(self, id):
        self.id = id
        self.value = 0 # in femtoFarads
        self.loVal = 11000 
        self.hiVal = 30000
        self.percent = 0
        self.isCalibrated = False
        
Sensors = {
    0: Sensor(1),
    1: Sensor(2),
    2: Sensor(3),
    3: Sensor(4)
}
# System Settings
ct.set_appearance_mode("System")
ct.set_default_color_theme("blue")

""" class SensorListFrame(ct.CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.title = title
        self.radiobuttons = []
        self.variable = ct.StringVar(value="")

        self.title = ct.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(self.values):
            radiobutton = ct.CTkRadioButton(self, text=value, value=value, variable=self.variable)
            radiobutton.grid(row=i + 1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.radiobuttons.append(radiobutton)

    def get(self):
        return self.variable.get()

    def set(self, value):
        self.variable.set(value)

class SensorDataFrame(ct.CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        #self.id = id
        #self.value = 0 # in femtoFarads
        #self.loVal = 11000 
        #self.hiVal = 30000
        #self.percent = 0
        #self.isCalibrated = False

    def set(self, sensor):
        self.variable.set(sensor)

class GUI(ct.CTk):
    def __init__(self):
        super().__init__()

        self.title("my app")
        self.geometry("720x480")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        values = ["value 1", "value 2", "value 3", "value 4", "value 5", "value 6"] #num sensors in dict
        self.scrollable_radiobtn_frame = SensorListFrame(self, title="Sensors", values=values)
        self.scrollable_radiobtn_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.button = ct.CTkButton(self, text="my button", command=self.button_callback)
        self.button.grid(row=3, column=0, padx=10, pady=10, sticky="ew", columnspan=2)

    def button_callback(self):
        print("radiobutton_frame:", self.radiobutton_frame.get()) """
