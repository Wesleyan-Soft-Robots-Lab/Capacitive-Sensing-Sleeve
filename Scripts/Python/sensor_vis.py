import fast_communication as comm
import tkinter as tk
from collections import deque
import time
from scipy.signal import butter, lfilter, lfilter_zi

class LiveButterFilter:
    """
    Real-time Butterworth low-pass filter using scipy.signal.lfilter_zi for state tracking.
    """
    def __init__(self, cutoff=2, fs=33.0, order=2):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        self.b, self.a = butter(order, normal_cutoff, btype='low', analog=False)
        self.zi = lfilter_zi(self.b, self.a)
        self.initialized = False

    def process(self, value):
        if not self.initialized:
            # Scale initial state to the first incoming value to avoid sudden spikes
            self.zi = self.zi * value
            self.initialized = True
        
        y, self.zi = lfilter(self.b, self.a, [value], zi=self.zi)
        return float(y[0])

def get_color(sensorVal):
    "Given the sensor pf value, returns a more drastic color mapping (Blue -> Green -> Yellow -> Red)"
    val = max(0, min(100, float(sensorVal)))
    
    # Highly sensitive mapping: full transition happens by 35% (near the 30% hard press threshold)
    if val <= 15:  # Hover region: Blue to Green
        ratio = val / 15.0
        r = 0
        g = int(255 * ratio)
        b = int(255 * (1 - ratio))
    elif val <= 25:  # Light touch region: Green to Yellow
        ratio = (val - 15) / 10.0
        r = int(255 * ratio)
        g = 255
        b = 0
    elif val <= 35:  # Hard touch region: Yellow to Red
        ratio = (val - 25) / 10.0
        r = 255
        g = int(255 * (1 - ratio))
        b = 0
    else:  # Maxed out
        r = 255
        g = 0
        b = 0
        
    return f"#{r:02x}{g:02x}{b:02x}"
    
def create_plot(parent_frame):
    """
    Creates a small graph canvas underneath the sensor label.
    """
    canvas = tk.Canvas(parent_frame, width=100, height=40, bg='black', highlightthickness=0)
    canvas.pack(side=tk.BOTTOM, padx=5, pady=10)
    return canvas

def update_plot(canvas, history, max_val=35):
    """
    Updates the shape of the graph with a constant y-axis.
    """
    canvas.delete("all")
    if len(history) < 2:
        return
        
    width = int(canvas['width'])
    height = int(canvas['height'])
    
    points = []
    x_step = width / (history.maxlen - 1)
    
    # Start x at the correct offset so the graph visually scrolls to the left
    start_x = width - ((len(history) - 1) * x_step)
    
    for i, val in enumerate(history):
        x = start_x + (i * x_step)
        # Constant Y-axis mapping: 0 to max_val maps to height to 0
        y = height - (min(max(val, 0), max_val) / max_val * height)
        points.extend([x, y])
        
    canvas.create_line(*points, fill="cyan", width=2)

def make_draggable(frame):
    def on_drag_start(event):
        frame.lift()
        frame._drag_start_x = event.x_root
        frame._drag_start_y = event.y_root
        frame._start_x = frame.winfo_x()
        frame._start_y = frame.winfo_y()

    def on_drag_motion(event):
        dx = event.x_root - frame._drag_start_x
        dy = event.y_root - frame._drag_start_y
        frame.place(x=frame._start_x + dx, y=frame._start_y + dy)

    def on_drag_release(event):
        current_x = frame.winfo_x()
        current_y = frame.winfo_y()
        
        # Grid snapping
        GRID_X = 140
        GRID_Y = 180
        
        rel_x = current_x - 10
        rel_y = current_y - 10
        
        snapped_x = round(rel_x / GRID_X) * GRID_X + 10
        snapped_y = round(rel_y / GRID_Y) * GRID_Y + 10
        
        snapped_x = max(10, snapped_x)
        snapped_y = max(10, snapped_y)
        
        frame.place(x=snapped_x, y=snapped_y)

    # Bind events to the frame and all its current children
    for widget in (frame, *frame.winfo_children()):
        widget.bind("<ButtonPress-1>", on_drag_start)
        widget.bind("<B1-Motion>", on_drag_motion)
        widget.bind("<ButtonRelease-1>", on_drag_release)

def create_sensor_window(sensor_values):
    """
    Creates a window with widgets for every sensor and their respective id,
    and changes their color from blue to red gradually based on the sensor pf value.
    """
    window = tk.Tk()
    window.title("Sensor Visualization")
    window.geometry("800x600") # Set initial window size for grid
    
    frames = {}
    labels = {}
    canvases = {}
    histories = {}
    last_states = {}
    butter_filters = {}
    
    for idx, (sensor_id, sensor) in enumerate(sensor_values.items()):
        if hasattr(sensor, 'percent'):
            val = sensor.percent
        elif hasattr(sensor, 'value'):
            val = sensor.value
        else:
            val = float(sensor)
            
        color = get_color(val)
        text = f"Sensor {sensor_id}\n{val:.1f}"
        
        # Increased height to 160 to fit the plot canvas underneath
        frame = tk.Frame(window, bg=color, width=120, height=160, relief=tk.RAISED, borderwidth=2)
        frame.pack_propagate(False)
        
        # Calculate initial grid position
        GRID_X = 140
        GRID_Y = 180
        cols = 5 # 5 items per row
        row = idx // cols
        col = idx % cols
        frame.place(x=col * GRID_X + 10, y=row * GRID_Y + 10)
        
        lbl = tk.Label(frame, text=text, bg=color, fg="white", font=("Arial", 12, "bold"))
        lbl.pack(expand=True)
        
        # Create the plot
        canvas = create_plot(frame)
        
        # Make the frame and its children draggable
        make_draggable(frame)
        
        frames[sensor_id] = frame
        labels[sensor_id] = lbl
        canvases[sensor_id] = canvas
        histories[sensor_id] = deque([val], maxlen=50) # Keep history of last 50 points
        last_states[sensor_id] = (color, text)
        butter_filters[sensor_id] = LiveButterFilter(cutoff=1, fs=33.0, order=2)
        
    def update():
        try:
            # Drain the buffer a bit if it's falling behind, to match fast_comm's speed
            sensors = comm.ReadPort()
            if hasattr(comm, 'arduino'):
                while comm.arduino and comm.arduino.in_waiting > 50:
                    sensors = comm.ReadPort()
                    
            for s_id, s_obj in sensors.items():
                if hasattr(s_obj, 'percent'):
                    v = s_obj.percent
                elif hasattr(s_obj, 'value'):
                    v = s_obj.value
                else:
                    v = float(s_obj)
                    
                # Apply real-time Butterworth filter
                if s_id in butter_filters:
                    v = butter_filters[s_id].process(v)
                    
                c = get_color(v)
                text = f"Sensor {s_id}\n{v:.1f}"
                
                # Update history and plot
                if s_id in histories:
                    histories[s_id].append(v)
                    update_plot(canvases[s_id], histories[s_id])
                
                # Only redraw if the color or text actually changed to prevent Tkinter lag
                if last_states.get(s_id) != (c, text):
                    last_states[s_id] = (c, text)
                    if s_id in frames and s_id in labels:
                        frames[s_id].configure(bg=c)
                        labels[s_id].configure(text=text, bg=c)
        except Exception as e:
            pass # print("Error reading port:", e)
            
        window.after(10, update) # Running at ~100FPS to balance fast rendering with graphing logic
        
    window.after(10, update)
    return window

def main():
    print("Waiting for sensors to connect...")
    sensors = dict()
    while not sensors:
        try:
            sensors = comm.ReadPort()
            # for i,s in sensors.items(): 
            #     if not s.isCalibrated:
            #         s.Calibrate()
        except Exception:
            pass
            
    print(f"Connected to {len(sensors)} sensors.")
    window = create_sensor_window(sensors)
    window.mainloop()

if __name__ == "__main__":
    main()
