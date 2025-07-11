""" 
Name: Miles Modeste
Date Created: 7/10/2025

Description:
  This script shows a GUI for calibrating Sensors communicating between Arduino and Python.
  This module is intended to be run instead of communication.py 

TODO:
    - Add module to save/load calibration data
    - Add module to start recording data
"""
import os
import customtkinter as ct
import communication as comm
import json

# System Settings
ct.set_appearance_mode("System")
ct.set_default_color_theme("blue")

#CONTROL PANEL FOR SELECTING SENSOR TO DISPLAY
class SensorSelectionModule(ct.CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)

        self.title = title
        self.title = ct.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        self.values = values
        self.radiobuttons = []
        self.variable = ct.IntVar(value=-1)
        self.variable.trace_add("write", self.on_selection_change)

        #create buttons
        for v in self.values:
            radiobutton = ct.CTkRadioButton(self, text=f"s{v}", value=v, variable=self.variable)
            radiobutton.grid(row=v + 1, column=0, padx=10, pady=(10, 0), sticky="ew")
            self.radiobuttons.append(radiobutton)

    def on_selection_change(self, *args):
        self.master.data_frame.UpdateVals()

    def get(self):
        return self.variable.get()
    
    def Update_Buttons(self, values):
        for b in self.radiobuttons:
            b.destroy()
        self.radiobuttons.clear()

        self.values = values
        for v in self.values:
            radiobutton = ct.CTkRadioButton(self, text=f"s{v}", value=v, variable=self.variable)
            radiobutton.grid(row=v + 1, column=0, padx=10, pady=(10, 0), sticky="ew")
            self.radiobuttons.append(radiobutton)

# CONTROL BUTTONS FOR TWEAKING VALUES
class ControlButtons(ct.CTkFrame):
    def __init__(self, master, attr):
        super().__init__(master)
        # - buttons
        self.minus1_btn = ct.CTkButton(self, text="-1", fg_color="gray30", width=0, corner_radius=6, command=lambda: self.ChangeVal(attr, -1))
        self.minus1_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.minus10_btn = ct.CTkButton(self, text="-10",fg_color="gray30", width=0, corner_radius=6, command=lambda: self.ChangeVal(attr, -10))
        self.minus10_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.minus100_btn = ct.CTkButton(self, text="-100",fg_color="gray30", width=0, corner_radius=6, command=lambda: self.ChangeVal(attr, -100))
        self.minus100_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        # + buttons
        self.plus100_btn = ct.CTkButton(self, text="+100",fg_color="gray30", width=0, corner_radius=6, command=lambda: self.ChangeVal(attr, 100))
        self.plus100_btn.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.plus10_btn = ct.CTkButton(self, text="+10",fg_color="gray30", width=0, corner_radius=6, command=lambda: self.ChangeVal(attr, 10))
        self.plus10_btn.grid(row=0, column=4, padx=5, pady=5, sticky="ew")
        self.plus1_btn = ct.CTkButton(self, text="+1",fg_color="gray30", width=0, corner_radius=6, command=lambda: self.ChangeVal(attr, 1))
        self.plus1_btn.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

    def ChangeVal(self, attr, val):
        sensor = self.master.GetSelectedSensor()
        if sensor:
            setattr(sensor, attr, getattr(sensor, attr) + val)
    def SetValue(self, var, val):
        var = val

# FRAME DISPLAYING DATA
class SensorDataModule(ct.CTkFrame):
    def __init__(self, master, selectionFrame:SensorSelectionModule):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.selectionFrame = selectionFrame
        self.selectedSensor = None
        #title/name of selected sensor
        self.title = "No Sensor Selected"
        self.title = ct.CTkLabel(self,fg_color="gray30", text=self.title, corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="new")
        #textbox showing data
        self.values = ct.CTkLabel(self, text="Value:--\nPercent:--", anchor="nw", justify="left",corner_radius=6)
        self.values.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.hi_label = ct.CTkLabel(self, text="High Point:", corner_radius=6)
        self.hi_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="new")
        self.hi_ctrl = ControlButtons(self, "hiVal")
        self.hi_ctrl.grid(row=3, column=0, padx=10, sticky="ne")
        self.lo_label = ct.CTkLabel(self, text="Low Point:", corner_radius=6) 
        self.lo_label.grid(row=4, column=0, padx=10, pady=(10, 0), sticky="new")
        self.lo_ctrl = ControlButtons(self, "loVal")
        self.lo_ctrl.grid(row=5, column=0, padx=10, sticky="ne")

        self.calibrated_label = ct.CTkLabel(self, text=f"is_Calibrated:", anchor="nw", justify="left")
        self.calibrated_label.grid(row=6, column=0, padx=10, pady=(10, 0), sticky="nw")
        self.calib_switch_var = ct.StringVar(value="off")
        self.calibration_switch = ct.CTkSwitch(self, text="", command=self.toggle_calibration, variable=self.calib_switch_var, onvalue="on", offvalue="off")
        self.calibration_switch.grid(row=6, column=0, padx=10, pady=(10, 0), sticky="e")
    def GetSelectedSensor(self):
        i = self.selectionFrame.variable.get()
        if (i == -1):
            return None
        return self.master.sensors[i]
    
    def UpdateVals(self):
        self.selectedSensor = self.GetSelectedSensor()
        if (self.selectedSensor == None):
            return
        else:
            self.title.configure(text=f"Viewing Sensor_{self.selectedSensor.id} Data")
            self.values.configure(text=f"Value: {self.selectedSensor.value}fF\nPercent: {self.selectedSensor.percent}%")
            self.hi_label.configure(text=f"High Point: {self.selectedSensor.hiVal}")
            self.lo_label.configure(text=f"Low Point: {self.selectedSensor.loVal}")
            self.calibrated_label.configure(text=f"is_Calibrated: {self.selectedSensor.isCalibrated}")
            if self.selectedSensor.isCalibrated: 
                self.calibration_switch.select()
            else:
                self.calibration_switch.deselect()

    def toggle_calibration(self):
        if (self.selectedSensor == None):
            return
        else:
            setattr(self.selectedSensor, "isCalibrated", False if self.calibration_switch.get()=="off" else True)

# SAVE MODULE
class SaveModule(ct.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)

        self.Path = os.path.dirname(__file__)
        self.FileName = "calibration_config.json"

        self.save_btn = ct.CTkButton(self,text="Save Calibration",fg_color="green", width=0, corner_radius=6, command=self.SaveConfig)
        self.save_btn.grid(row=1,column=1,padx=10, pady=10)
        self.load_btn = ct.CTkButton(self,text="Load Previous Calibration",fg_color="grey30", width=0, corner_radius=6, command=self.LoadConfig)
        self.load_btn.grid(row=1,column=2,padx=10, pady=10)
    
    def SaveConfig(self):
        with open(os.path.join(self.Path, self.FileName), "w") as file:
            data:dict[int,list[str]] = {}
            for s in self.master.sensors.values():
                data[s.id] = {
                    "hiVal":s.hiVal,
                    "loVal":s.loVal
                }
            json.dump(data,file)

    def LoadConfig(self):
        with open(os.path.join(self.Path, self.FileName), "r") as file:
            data = json.load(file)
            for key in data:
                for attr in data[key]:
                    s = self.master.sensors[int(key)]
                    setattr(s, attr, data[key][attr])
                    #setattr(s, "isCalibrated", True) # not a great feature when controlling large robot arm lmao


# RECORD DATA MODULE
class RecordModule(ct.CTkFrame):
    def __init__(self, master, data):
        super().__init__(master)
        self.isRecording = False
        self.record_btn = ct.CTkButton(self, text="Record", fg_color="red", width=0, corner_radius=6, command=self.ToggleRec)
        self.record_btn.grid(row=0, column=0)
    def ToggleRec(self):
        if self.isRecording == False:
            self.isRecording = True
            self.record_btn.configure(text="Stop", fg_color="gray")
        elif self.isRecording == True:
            self.isRecording = False
            self.record_btn.configure(text="Record", fg_color="red")  
        return
    def Record(self):
        return

# MAIN GUI
class GUI(ct.CTk):
    def __init__(self, sensors, *callback_behaviors):
        super().__init__()

        self.title("DEBUG Screen")
        self.geometry("650x450")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.callbacks = callback_behaviors
        self.sensors = sensors
        self.selection_frame = SensorSelectionModule(self, title="Visible Sensors:", values= self.sensors.keys())
        self.selection_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.record_frame = RecordModule(self,self.sensors)
        self.record_frame.grid(row=2,column=0,padx=10, pady=10 , sticky="n")

        self.data_frame = SensorDataModule(self, self.selection_frame)
        self.data_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="new")
        
        self.save_load = SaveModule(self)
        self.save_load.grid(row=2,column=1, columnspan=2,padx=10, pady=10, sticky="ne")
        
        self.RefreshFrames()

    def RefreshFrames(self):
        self.sensors = comm.ReadPort()
        for callback in self.callbacks:
            callback(self.sensors)
        self.data_frame.UpdateVals()
        if (self.record_frame.isRecording == True):
            self.record_frame.Record()
        self.after(10, self.RefreshFrames)

if __name__=="__main__":
    global sensors
    sensors = dict[int,comm.Sensor]()
    while not sensors:
        sensors = comm.ReadPort()
        continue
    sensorGUI = GUI(sensors)
    sensorGUI.mainloop()