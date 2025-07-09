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

class ListSelectionFrame(ct.CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)

        self.title = title
        self.title = ct.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nw")

        self.values = values
        self.radiobuttons = []
        self.variable = ct.StringVar(value="") # stores value of selected btn w/in frame

        #create buttons
        for v in self.values:
            radiobutton = ct.CTkRadioButton(self, text=f"s{v}", value=v, variable=self.variable)
            radiobutton.grid(row=v + 1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.radiobuttons.append(radiobutton)

    def get(self):
        return self.variable.get()
    #i dont think i need this 
    def set(self, value):
        self.variable.set(value)

class SensorDataFrame(ct.CTkFrame):
    def __init__(self, master, list):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(0, weight=0)

        self.listFrame = list
        #title/name of selected sensor
        self.title = "No Sensor Selected"
        self.title = ct.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="new")
        #textbox showing data
        self.textbox = ct.CTkTextbox(self,fg_color="gray30",  corner_radius=6)
        self.textbox.grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 0), sticky="new")
        self.textbox.insert("0.0", "Value:\nPercent:")

        self.hi_label = ct.CTkLabel(self, text="High Point:", fg_color="gray30", corner_radius=6)
        self.hi_label.grid(row=2, column=0, columnspan=3, rowspan=2, padx=10, pady=(10, 0), sticky="new")
        self.hi_increase = ct.CTkButton(self, text="+",fg_color="gray30", corner_radius=6)
        self.hi_increase.grid(row=2, column=3, padx=10, pady=(10, 0), sticky="nsw")
        self.hi_decrease = ct.CTkButton(self, text="-",fg_color="gray30", corner_radius=6)
        self.hi_decrease.grid(row=3, column=3, padx=10, pady=(10, 0), sticky="nsw")

        self.lo_label = ct.CTkLabel(self, text="Low Point:", fg_color="gray30", corner_radius=6) 
        self.lo_label.grid(row=4, column=0, columnspan=3, rowspan=2, padx=10, pady=(10, 0), sticky="new")
        self.lo_increase = ct.CTkButton(self, text="+",fg_color="gray30", corner_radius=6)
        self.lo_increase.grid(row=4, column=3, padx=10, pady=(10, 0), sticky="nsw")
        self.lo_decrease = ct.CTkButton(self, text="-",fg_color="gray30", corner_radius=6)
        self.lo_decrease.grid(row=5, column=3, padx=10, pady=(10, 0), sticky="nsw")

    def set(self, sensor):
        self.variable.set(sensor)

class GUI(ct.CTk):
    def __init__(self):
        super().__init__()

        self.title("my app")
        self.geometry("720x480")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        ids = Sensors.keys()
        self.sensor_btn_frame = ListSelectionFrame(self, title="Sensors", values=ids)
        self.sensor_btn_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsw")

        self.sensor_display_frame = SensorDataFrame(self, list=self.sensor_btn_frame)
        self.sensor_display_frame.grid(row=0, column=2, padx=10, pady=(10, 0), sticky="nsew")

sensorGUI = GUI()

sensorGUI.mainloop()