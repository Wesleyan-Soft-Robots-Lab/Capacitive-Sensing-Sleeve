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

def get_color(val, loVal=4.2):
    "Given the sensor pf value, returns a more drastic color mapping (Blue -> Green -> Yellow -> Red) based on raw values"
    delta = val - loVal
    
    if delta <= 0.2:
        return "#0000ff"
        
    if delta <= 0.8:  # Hover region: Blue to Green
        ratio = (delta - 0.2) / 0.6
        r = 0
        g = int(255 * ratio)
        b = int(255 * (1 - ratio))
    elif delta <= 1.8:  # Light touch region: Green to Yellow
        ratio = (delta - 0.8) / 1.0
        r = int(255 * ratio)
        g = 255
        b = 0
    elif delta <= 3.0:  # Hard touch region: Yellow to Red
        ratio = (delta - 1.8) / 1.2
        r = 255
        g = int(255 * (1 - ratio))
        b = 0
    else:  # Maxed out
        r = 255
        g = 0
        b = 0
        
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
        
    return f"#{r:02x}{g:02x}{b:02x}"
    
def create_plot(parent_frame):
    """
    Creates a small graph canvas underneath the sensor label.
    """
    canvas = tk.Canvas(parent_frame, width=100, height=40, bg='white', highlightthickness=0)
    canvas.pack(side=tk.BOTTOM, padx=5, pady=10)
    return canvas

def update_plot(canvas, history):
    """
    Updates the shape of the graph with dynamic auto-scaling 
    """
    canvas.delete("all")
    if len(history) < 2:
        return
        
    width = int(canvas['width'])
    height = int(canvas['height'])
    
    current_max = max(history)
    max_val = max(5.0, current_max * 1.2)
    
    points = []
    x_step = width / (history.maxlen - 1)
    
    start_x = width - ((len(history) - 1) * x_step)
    
    for i, val in enumerate(history):
        x = start_x + (i * x_step)

        y = height - (min(max(val, 0), max_val) / max_val * height)
        points.extend([x, y])
        
    canvas.create_line(*points, fill="blue", width=2)

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

def create_sensor_window(sensor_values, ignoreID=None):
    """
    Creates a window with widgets for every sensor and their respective id,
    and changes their color from blue to red gradually based on the sensor pf value.
    """
    if ignoreID is None:
        ignoreID = []
        
    sensor_values = {k: v for k, v in sensor_values.items() if k not in ignoreID}
    
    print("Calibrating baselines for 3 seconds, please don't touch the sensors...")
    start_time = time.time()
    calib_data = {k: [] for k in sensor_values.keys()}
    
    while time.time() - start_time < 3.0:
        sensors = comm.ReadPort()
        if hasattr(comm, 'arduino'):
            while comm.arduino and comm.arduino.in_waiting > 50:
                sensors = comm.ReadPort()
                
        for s_id, s_obj in sensors.items():
            if s_id in calib_data:
                calib_data[s_id].append(s_obj.value)
        time.sleep(0.01)
        
    for s_id, s_obj in sensor_values.items():
        if calib_data[s_id]:
            s_obj.loVal = sum(calib_data[s_id]) / len(calib_data[s_id])
        else:
            s_obj.loVal = s_obj.value
        s_obj.hiVal = 25.0
        
    print("Calibration complete!")
    
    window = tk.Tk()
    window.title("Sensor Visualization")
    window.geometry("1400x1000") # Set initial window size for grid
    
    canvas = tk.Canvas(window, bg="white")
    v_scrollbar = tk.Scrollbar(window, orient="vertical", command=canvas.yview)
    h_scrollbar = tk.Scrollbar(window, orient="horizontal", command=canvas.xview)
    
    # Calculate a large enough frame size to fit everything
    GRID_X = 140
    GRID_Y = 180
    cols = 10 # 10 items per row to use the right side of the screen
    rows = ( (len(sensor_values) + cols - 1) // cols ) + 5
    frame_width = max(1400, cols * GRID_X + 100)
    frame_height = max(1000, rows * GRID_Y + 200)
    
    scrollable_frame = tk.Frame(canvas, width=frame_width, height=frame_height, bg="white")
    scrollable_frame.pack_propagate(False)
    
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    
    def on_canvas_configure(event):
        # Ensure the scrollable frame takes up at least the full canvas width
        canvas.itemconfig(canvas_window, width=max(frame_width, event.width))
    canvas.bind('<Configure>', on_canvas_configure)
    
    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set, scrollregion=(0, 0, frame_width, frame_height))
    
    v_scrollbar.pack(side="right", fill="y")
    h_scrollbar.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)
    
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta)), "units")
    window.bind("<MouseWheel>", _on_mousewheel)
    
    frames = {}
    labels = {}
    canvases = {}
    histories = {}
    last_states = {}
    butter_filters = {}
    
    for idx, (sensor_id, sensor) in enumerate(sensor_values.items()):
        v = sensor.value
            
        color = get_color(v, sensor.loVal)
        text = f"Sensor {sensor_id}\n{v:.2f} pF"
        
        frame = tk.Frame(scrollable_frame, bg=color, width=120, height=160, relief=tk.RAISED, borderwidth=2)
        frame.pack_propagate(False)
        
        row = idx // cols
        col = idx % cols
        frame.place(x=col * GRID_X + 10, y=row * GRID_Y + 10)
        
        lbl = tk.Label(frame, text=text, bg=color, fg="white", font=("Arial", 12, "bold"))
        lbl.pack(expand=True)
        
        canvas_plot = create_plot(frame)
        
        # Make the frame and its children draggable
        make_draggable(frame)
        
        frames[sensor_id] = frame
        labels[sensor_id] = lbl
        canvases[sensor_id] = canvas_plot
        histories[sensor_id] = deque([v], maxlen=50) # Keep history of last 50 points
        last_states[sensor_id] = (color, text)
        butter_filters[sensor_id] = LiveButterFilter(cutoff=0.5, fs=32.0, order=2)
        
    def update():
        try:
            sensors = comm.ReadPort()
            if hasattr(comm, 'arduino'):
                while comm.arduino and comm.arduino.in_waiting > 50:
                    sensors = comm.ReadPort()
                    
            for s_id, s_obj in sensors.items():
                if s_id in ignoreID:
                    continue
                
                v = s_obj.value
                    
                # Apply filter
                if s_id in butter_filters:
                    v = butter_filters[s_id].process(v)
                    
                    
                c = get_color(v, s_obj.loVal)
                text = f"Sensor {s_id}\n{v:.2f} pF"
                
                # Update history and plot
                if s_id in histories:
                    histories[s_id].append(v)
                    update_plot(canvases[s_id], histories[s_id])
                
                # Only redraw if the color or text actually changed to prevent lag
                if last_states.get(s_id) != (c, text):
                    last_states[s_id] = (c, text)
                    if s_id in frames and s_id in labels:
                        frames[s_id].configure(bg=c)
                        labels[s_id].configure(text=text, bg=c)
        except Exception as e:
            pass # print("Error reading port:", e)
            
        window.after(10, update) 
        
    window.after(10, update)
    return window

def channel2ID(mux=0, port=0, channel=0):
    return (mux << 5) | (port << 2) | channel

def main():
    ignoreChannel = []
    ignoreID = []
    
    for mux,port,ch in ignoreChannel:
        id = channel2ID(mux, port, ch)
        ignoreID.append(id)
        
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
    window = create_sensor_window(sensors, ignoreID)
    window.mainloop()

if __name__ == "__main__":
    main()
