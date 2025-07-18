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
import pandas as pd
import json
import time
#import cv2

# System Settings
ct.set_appearance_mode("System")
ct.set_default_color_theme("blue")

#CONTROL PANEL FOR SELECTING SENSOR TO DISPLAY
class SensorSelectionModule(ct.CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        # vars
        self.title = title
        self.values = values
        self.radiobuttons = []
        self.variable = ct.IntVar(value=-1)

        # ui elements
        self.grid_columnconfigure(0, weight=1)
        self.title = ct.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
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
        self.minus1_btn = ct.CTkButton(self, text="-10", fg_color="gray30", width=0, corner_radius=6, command=lambda: self.ChangeVal(attr, -10))
        self.minus1_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.minus10_btn = ct.CTkButton(self, text="-100",fg_color="gray30", width=0, corner_radius=6, command=lambda: self.ChangeVal(attr, -100))
        self.minus10_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.minus100_btn = ct.CTkButton(self, text="-1000",fg_color="gray30", width=0, corner_radius=6, command=lambda: self.ChangeVal(attr, -1000))
        self.minus100_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        # + buttons
        self.plus100_btn = ct.CTkButton(self, text="+1000",fg_color="gray30", width=0, corner_radius=6, command=lambda: self.ChangeVal(attr, 1000))
        self.plus100_btn.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.plus10_btn = ct.CTkButton(self, text="+100",fg_color="gray30", width=0, corner_radius=6, command=lambda: self.ChangeVal(attr, 100))
        self.plus10_btn.grid(row=0, column=4, padx=5, pady=5, sticky="ew")
        self.plus1_btn = ct.CTkButton(self, text="+10",fg_color="gray30", width=0, corner_radius=6, command=lambda: self.ChangeVal(attr, 10))
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
        # vars
        self.title = "No Sensor Selected"
        self.selectionFrame = selectionFrame
        self.selectedSensor = None

        # ui elements
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # title/name of selected sensor
        self.title = ct.CTkLabel(self,fg_color="gray30", text=self.title, corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="new")
        self.values = ct.CTkLabel(self, text="Value:--\nPercent:--", anchor="nw", justify="left",corner_radius=6)
        self.values.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsew")
        # btns
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
class SaveCalibrationModule(ct.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # vars
        self.Path = os.path.dirname(__file__)
        self.FileName = "calibration_config.json"

        # ui elements
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
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

# RECORD DATA MODULE
class RecordModule(ct.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        # vars
        self.isRecording = False
        self.data = pd.DataFrame()
        self.startTime = None
        self.dataPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..','tests', 'data', 'sensor-arm-data'))
        self.vidPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..','tests', 'video'))
        self.filename_var = ct.StringVar(value="demo")
        
        # ui elements
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.record_btn = ct.CTkButton(self, text="Record", fg_color="red", width=0, corner_radius=6, command=self.ToggleRec)
        self.record_btn.grid(row=2, column=0, pady=(0,10))

        self.dir_label = ct.CTkLabel(self, text=f"file loc: tests/data/demo.csv",anchor="nw",justify="left")
        self.dir_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,0))
        self.filename_entry = ct.CTkEntry(self, 
                                          width=100,
                                          height=15,
                                          placeholder_text="filename(s) **data & video share name",
                                          textvariable=self.filename_var)
        self.filename_entry.grid(row=1, column=0)
        self.entry_btn = ct.CTkButton(self,width=0, text="Submit", command=self.ChangeName)
        self.entry_btn.grid(row=1, column=1)

        """ #video capture init
        try:
            self.cam = cv2.VideoCapture(0)

            self.cam_width = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.cam_height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            #self.vid_out_File = cv2.VideoWriter(os.path.join(self.vidPath, self.filename_var.get)+'.mp4', self.fourcc, 30.0, (self.cam_width, self.cam_height))
        except:
            self.cam = None """

    def ChangeName(self):
        self.dir_label.configure(text=f"file loc: tests/data/{self.filename_var.get()}.csv")

    def ToggleRec(self):
        #Start Recording
        if self.isRecording == False:
            self.record_btn.configure(text="Stop", fg_color="gray")
            self.data = []
            """ if self.cam:
                name = self.filename_var.get()
                self.vid_out_File = cv2.VideoWriter(os.path.join(self.vidPath, name)+'.mp4', self.fourcc, 30.0, (self.cam_width, self.cam_height)) """
            self.isRecording = True
        #End Recording
        elif self.isRecording == True:
            self.record_btn.configure(text="Record", fg_color="red")
            """ if self.cam:
                self.vid_out_File.release() """
            self.Save()
            self.isRecording = False
        return
    
    def Record(self):
        #data record
        row = {"time": f"{time.time()}"}
        sensorsInp = self.master.sensors
        armData = self.master.arm_data_callback()
        for k,v in sensorsInp.items():
            row[f"sensor_{k}_values"] = v.value
            row[f"sensor_{k}_percent"] = v.percent
        if armData != None:
            row["arm_pos"] = armData
        self.data.append(row)

        """ # video record
        if self.cam:
            ret, frame = self.cam.read()
            self.vid_out_File.write(frame)
            pass """

    def Save(self):
        filePath = os.path.join(self.dataPath, self.filename_var.get())+'.csv'
        dataFrame = pd.DataFrame(self.data)
        with open(filePath, 'w') as file:
            current_time = time.localtime()
            date = f"Date-- {current_time.tm_mon:02d}/{current_time.tm_mday:02d}/{current_time.tm_year}"
            clock = f"Clock-- {current_time.tm_hour}:{current_time.tm_min}:{current_time.tm_sec}"
            file.write(f"###  {date}\t{clock}\n")
            for s in self.master.sensors.values():
                file.write(f"### sensor_{s.id}:hiVal={s.hiVal},loVal={s.loVal}\n")
            dataFrame.to_csv(file, index=False, lineterminator='\n')

# MAIN GUI
class GUI(ct.CTk):
    def __init__(self, sensorDict, arm_behaviour_callback=None, arm_data_callback=None):
        super().__init__()
        print("Launching GUI...")
        self.title("DEBUG Screen")
        self.geometry("650x450")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.arm_behaviour_callback = arm_behaviour_callback or (lambda x:None)
        self.arm_data_callback = arm_data_callback or (lambda:None)
        self.sensors = sensorDict
        self.selection_frame = SensorSelectionModule(self, title="Visible Sensors:", values= self.sensors.keys())
        self.selection_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.record_frame = RecordModule(self)
        self.record_frame.grid(row=2,column=0,padx=10, pady=10 , sticky="new")

        self.data_frame = SensorDataModule(self, self.selection_frame)
        self.data_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="new")
        
        self.save_load = SaveCalibrationModule(self)
        self.save_load.grid(row=2,column=1, columnspan=2,padx=10, pady=10, sticky="ne")
        
        self.RefreshFrames()

    def RefreshFrames(self):
        self.sensors = comm.ReadPort() 
        self.arm_behaviour_callback(self.sensors)
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
    sensorGUI = GUI(sensorDict=sensors)
    sensorGUI.mainloop()