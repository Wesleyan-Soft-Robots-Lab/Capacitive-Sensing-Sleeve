# import sys
# import os
# import time
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import communication as cm
# from xarm.wrapper import XArmAPI

# # === CONFIGURATION ===
# Sensors = dict[int, cm.Sensor]()
# ip = '192.168.1.232'

# # === PING PONG PARAMETERS ===
# # These define when the arm should react to hand presence
# maxThres = 80   # If hand is closer than this (higher %), arm moves away
# minThres = 20   # If hand is farther than this (lower %), arm moves closer
# target_v = -5   # The "sweet spot" where arm tries to stay
# maxVelocity = 40  # Maximum speed in mm/s


# # === PD CONTROL PARAMETERS ===
# Kp = 0.5       # Proportional gain - how strongly to react to current error
# Kd = 0.5        # Derivative gain - how strongly to react to rate of change
# previous_error = 0.0    # Store previous error for derivative calculation
# previous_time = 0.0     # Store previous time for derivative calculation

# # === CONNECT TO ARM ===
# try:
#     arm = XArmAPI(ip)
#     print("Successfully connected to xArm")
# except Exception as e:
#     print(f"Failed to connect to xArm: {e}")
#     sys.exit(1)

# def CalculateVelocity(init_v):
#     """
#     PD Control: Calculate velocity using Proportional-Derivative control
    
#     PD Control components:
#     - P (Proportional): Reacts to current error (how far from ideal position)
#     - D (Derivative): Reacts to rate of change (how fast error is changing)
    
#     Benefits of PD over P-only:
#     - Reduces oscillations and overshoot
#     - Provides smoother, more stable movement
#     - Anticipates where the system is heading
#     """
#     global previous_error, previous_time
#     current_time = time.time()

    
#     # Calculate error (how far we are from ideal velocity)
#     error = target_v - init_v 
    
#     # Calculate time difference for derivative
#     dt = current_time - previous_time
#     if dt <= 0:  # Avoid division by zero on first run
#         dt = 0.01  # Use small default time step
    
#     # PROPORTIONAL TERM: React to current error
#     # Larger error = stronger response
#     P_term = Kp * error
    
#     # DERIVATIVE TERM: React to rate of change of error
#     # If error is changing quickly, this helps slow down the response
#     # This prevents overshoot and oscillations
#     derivative_error = (error - previous_error) / dt
#     D_term = Kd * derivative_error
    
#     # Combine P and D terms
#     vel = P_term + D_term
    
#     # Store values for next iteration
#     previous_error = error
#     previous_time = current_time
    
#     # Apply velocity limits for safety
#     init_v += max(-maxVelocity, min(maxVelocity, vel))
    
#     # Debug information
#     print(f"  PD Control - Error: {error:.1f}, P: {P_term:.1f}, D: {D_term:.1f}, Output: {velocity:.1f}")
    
#     return init_v

# def initArm():
#     """Initialize the arm and move it to starting position"""
#     print("Initializing arm...")
    
#     # Enable the arm motors
#     arm.motion_enable(enable=True)
#     arm.set_mode(0)  # Position control mode for setup
#     arm.set_state(state=0)  # Clear any error states

#     speed = 40
#     # Move to starting pose - a comfortable position for ping pong
#     print("Moving to starting pose...")
#     arm.set_servo_angle(angle=[0, 20.7, -37.7, 0, 16.9, 0], speed=speed, wait=True)

#     print("Moving to home position...")
#     arm.move_gohome(speed=speed, wait=True)

#     # Switch to velocity control mode for real-time movement
#     print("Switching to velocity control mode...")
#     arm.set_mode(5)  # Velocity control mode
#     arm.set_state(0)

#     time.sleep(1)
#     print("Arm initialized and ready!")

# def ping_pong():
#     pressed = False  # Track if sensor has been pressed at all 
#     init_vel = 20
#     while init_vel :
#         """
#         Main ping pong logic using PD control - read sensors and move arm accordingly
#         """
#         # Read current sensor values
#         if not cm.ReadPort():
#             return  # No valid sensor data
        
#         # Get the updated sensor data from communication module
#         # cm.ReadPort() updates the global cm.Sleeve dictionary
#         sleeve_sensors = cm.Sleeve
        
#         # Check if we have sensor data
#         if not sleeve_sensors or "sensor_0" not in sleeve_sensors:
#             return  # No sensor data yet
        
#         sensor1 = sleeve_sensors["sensor_0"]
        
#         # Only apply PD control if hand is detected in reasonable range
#         if sensor1.percent < 0 or sensor1.percent > 100:
#             # Invalid sensor reading, stop movement
#             arm.vc_set_cartesian_velocity([0, 0, 0, 0, 0, 0])
#             return
#         if (sensor1.percent > maxThres) and (pressed == False):
#             # start with initial velocity
#             arm.vc_set_cartesian_velocity([0, init_vel, 0, 0, 0, 0])
#             # Send velocity command to arm
#             # [x, y, z, roll, pitch, yaw] - we only move in Z direction
#             zv = CalculateVelocity(init_vel)  # Calculate new velocity
#             arm.vc_set_cartesian_velocity([0, zv, 0, 0, 0, 0])
#             init_vel = zv  # Update initial velocity for next iteration
        
#             # Print debug info
#             print(f"Hand position: {sensor1.percent:.1f}%, Final Velocity: {zv:.1f} mm/s")
        


# # === MAIN LOOP ===
# if __name__ == "__main__":
#     print("Starting Ping Pong Arm Controller")
#     print("Make sure sensors are connected and calibrated!")
    
#     # Initialize the arm first
#     initArm()
    
#     # Calibrate sensors once at startup
#     print("\nCalibrating sensors...")
#     if not cm.calibrate_sensors():
#         print("Sensor calibration failed. Exiting...")
#         sys.exit(1)
    
#     print("Starting ping pong mode...")
#     print("Press Ctrl+C to stop")
    
#     try:
#         while True:
#             # cm.ReadPort() returns boolean but updates cm.Sleeve dictionary
#             # We don't need to assign its return value to Sensors
#             cm.ReadPort()
           
#             ping_pong()
            
#             # Small delay for smooth operation
#             time.sleep(0.05)  # 20Hz update rate
            
#     except KeyboardInterrupt:
#         print("\nShutting down...")
#         # Stop the arm safely
#         arm.vc_set_cartesian_velocity([0, 0, 0, 0, 0, 0])  # Stop movement
#         arm.set_state(4)  # Pause state
#         print("Arm stopped safely.")
#     except Exception as e:
#         print(f"Error occurred: {e}")
#         # Emergency stop
#         arm.vc_set_cartesian_velocity([0, 0, 0, 0, 0, 0])
#         arm.set_state(4)
#         print("Emergency stop activated.")






























































































































































































import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import communication as cm
from xarm.wrapper import XArmAPI

# === CONFIGURATION ===
Sensors = dict[int, cm.Sensor]()
ip = '192.168.1.232'

# === PING PONG PARAMETERS ===
press_threshold = 65    # When sensor reading is above this, consider it "pressed"
initial_velocity = 32   # Starting speed when moving away
target_velocity = -5    # Target velocity (negative = coming back)
maxVelocity = 40        # Maximum speed limit
bounce_distance_time = 3.2  # How long to move away before turning around (seconds)

# === PD CONTROL PARAMETERS ===
Kp = 1.2       # Proportional gain - responsive but not aggressive
Kd = 0.5       # Derivative gain - good damping without over-damping
previous_error = 0.0
previous_time = 0.0
error_history = []  # For derivative filtering

# === STATE MACHINE VARIABLES ===
# States: "WAITING", "BOUNCING_AWAY", "BOUNCING_BACK"
current_state = "WAITING"
current_velocity = 0.0
state_start_time = 0.0
last_press_time = 0.0   # Track when last press occurred

# === CONNECT TO ARM ===
try:
    arm = XArmAPI(ip)
    print("Successfully connected to xArm")
except Exception as e:
    print(f"Failed to connect to xArm: {e}")
    sys.exit(1)

def CalculateVelocity(current_vel, target_vel):
    """
    Refined PD Control with advanced stability features:
    - Derivative filtering to reduce noise
    - Adaptive limiting based on error magnitude
    - Deadband for final settling
    - Smooth initialization
    """
    global previous_error, previous_time, error_history
    current_time = time.time()
    
    # Calculate error (how far we are from target velocity)
    error = target_vel - current_vel
    
    # Calculate time difference
    dt = current_time - previous_time
    if dt <= 0 or previous_time == 0:
        dt = 0.05  # Expected loop time
        derivative_error = 0
        previous_error = error  # Initialize for next iteration
        previous_time = current_time
        return current_vel  # No change on first run
    
    # === PROPORTIONAL TERM ===
    P_term = Kp * error
    
    # === DERIVATIVE TERM WITH FILTERING ===
    # Calculate raw derivative
    raw_derivative = (error - previous_error) / dt
    
    # Add to history for filtering
    error_history.append(raw_derivative)
    if len(error_history) > 3:  # Keep only last 3 values
        error_history.pop(0)
    
    # Use moving average of derivative to reduce noise
    if len(error_history) >= 2:
        filtered_derivative = sum(error_history) / len(error_history)
    else:
        filtered_derivative = raw_derivative
    
    # Apply derivative limiting
    max_derivative = 50.0
    filtered_derivative = max(-max_derivative, min(max_derivative, filtered_derivative))
    
    D_term = Kd * filtered_derivative
    
    # === ADAPTIVE VELOCITY CHANGE LIMITING ===
    # Larger errors allow larger changes, smaller errors get smaller changes
    error_magnitude = abs(error)
    if error_magnitude > 20:
        max_change = 4.0    # Large error = allow bigger steps
    elif error_magnitude > 10:
        max_change = 2.5    # Medium error = medium steps
    elif error_magnitude > 3:
        max_change = 1.5    # Small error = small steps
    else:
        max_change = 0.8    # Very small error = tiny steps
    
    # Calculate total velocity change
    velocity_change = P_term + D_term
    
    # Apply adaptive limiting
    velocity_change = max(-max_change, min(max_change, velocity_change))
    
    # === DEADBAND FOR SETTLING ===
    # If we're very close to target, make smaller adjustments
    if abs(error) < 1.0:
        velocity_change *= 0.5  # Reduce change when close to target
    
    # Apply change to current velocity
    new_velocity = current_vel + velocity_change
    
    # Final velocity limits
    new_velocity = max(-maxVelocity, min(maxVelocity, new_velocity))
    
    # Store for next iteration
    previous_error = error
    previous_time = current_time
    
    # Enhanced debug output
    convergence_rate = abs(velocity_change) / max(abs(error), 0.1)
    print(f"  PD: {current_vel:.1f}→{target_vel:.1f} | Err:{error:.1f} | P:{P_term:.1f} D:{D_term:.1f}")
    print(f"      Change:{velocity_change:.1f} | New:{new_velocity:.1f} | Conv:{convergence_rate:.2f}")
    
    return new_velocity

def initArm():
    """Initialize the arm and move it to starting position"""
    print("Initializing arm...")
    
    arm.motion_enable(enable=True)
    arm.set_mode(0)
    arm.set_state(state=0)

    speed = 40
    print("Moving to starting pose...")
    arm.set_servo_angle(angle=[0, 20.7, -37.7, 0, 16.9, 0], speed=speed, wait=True)
    
    print("Moving to home position...")
    arm.move_gohome(speed=speed, wait=True)

    print("Switching to velocity control mode...")
    arm.set_mode(5)
    arm.set_state(0)

    time.sleep(1)
    print("Arm initialized and ready!")

def ping_pong():
    """
    Ping pong wall behavior - like bouncing a ball off a wall
    One touch triggers complete away→back cycle
    """
    global current_state, current_velocity, state_start_time, last_press_time
    
    # Read current sensor values
    if not cm.ReadPort():
        return
    
    sleeve_sensors = cm.Sleeve
    if not sleeve_sensors or "sensor_0" not in sleeve_sensors:
        return
    
    sensor1 = sleeve_sensors["sensor_0"]
    
    # Invalid sensor reading check
    if sensor1.percent < 0 or sensor1.percent > 100:
        arm.vc_set_cartesian_velocity([0, 0, 0, 0, 0, 0])
        return
    
    current_time = time.time()
    
    # STATE MACHINE LOGIC
    if current_state == "WAITING":
        # ============ WAITING FOR PRESS (like ball waiting to be hit) ============
        current_velocity = 0
        arm.vc_set_cartesian_velocity([0, 0, 0, 0, 0, 0])
        
        # Detect press (only if enough time has passed since last press to avoid double-triggering)
        if sensor1.percent > press_threshold and (current_time - last_press_time) > 1.0:
            print(f"PING! Touch detected: {sensor1.percent:.1f}% - Ball bouncing away!")
            current_state = "BOUNCING_AWAY"
            current_velocity = initial_velocity
            state_start_time = current_time
            last_press_time = current_time
    
    elif current_state == "BOUNCING_AWAY":
        # ============ BOUNCING AWAY (like ball moving away from wall) ============
        
        # Move away for a certain time, then automatically turn around
        time_moving_away = current_time - state_start_time
        
        if time_moving_away > bounce_distance_time:
            print(f"PONG! Turning around - Ball bouncing back!")
            current_state = "BOUNCING_BACK"
            state_start_time = current_time  
            # Reset PD control variables for clean transition
            global previous_error, previous_time, error_history
            previous_error = 0.0
            previous_time = 0.0  
            error_history = []  # Clear derivative history
        
        # Maintain the initial velocity while moving away
        # Don't use PD control here - just maintain constant speed
        current_velocity = initial_velocity
        arm.vc_set_cartesian_velocity([0, current_velocity, 0, 0, 0, 0])
    
    elif current_state == "BOUNCING_BACK":
        # ============ BOUNCING BACK (like ball returning to paddle) ============
        
        # Use refined PD control for smooth velocity transition
        current_velocity = CalculateVelocity(current_velocity, target_velocity)
        arm.vc_set_cartesian_velocity([0, current_velocity, 0, 0, 0, 0])
        
        # Enhanced completion detection
        time_coming_back = current_time - state_start_time
        velocity_settled = abs(current_velocity - target_velocity) < 1.5
        min_time_elapsed = time_coming_back > 10.0 
        
        if min_time_elapsed and velocity_settled:
            print(f" READY! Ball returned (took {time_coming_back:.1f}s) - Waiting for next hit...")
            current_state = "WAITING"
            current_velocity = 0
            arm.vc_set_cartesian_velocity([0, 0, 0, 0, 0, 0])
        elif time_coming_back > 8.0:  # Safety timeout
            print(f" TIMEOUT! Returning to waiting after {time_coming_back:.1f}s")
            current_state = "WAITING"
            current_velocity = 0
            arm.vc_set_cartesian_velocity([0, 0, 0, 0, 0, 0])
    
    # Debug output
    state_emoji = {"WAITING": "⚪", "BOUNCING_AWAY": "🏓", "BOUNCING_BACK": "🔄"}
    print(f"{state_emoji.get(current_state, '❓')} {current_state}: Sensor {sensor1.percent:.1f}%, Vel {current_velocity:.1f} mm/s")

# === MAIN LOOP ===
if __name__ == "__main__":
    print("Starting Ping Pong Arm Controller with State Machine")
    print("Make sure sensors are connected and calibrated!")
    
    # Initialize the arm first
    initArm()
    
    # Calibrate sensors once at startup
    print("\nCalibrating sensors...")  
    if not cm.calibrate_sensors():
        print("Sensor calibration failed. Exiting...")
        sys.exit(1)
    
    # "Starting ping pong mode..."
    # "Press Ctrl+C to stop"
    # "\nPing Pong Wall Behavior:"
    # "🏓 Touch → Bounce Away → 🔄 Turn Around → Come Back → ⚪ Wait"
    
    try:
        while True:
            cm.ReadPort()
            ping_pong()
            time.sleep(0.05)  # 20Hz update rate
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        arm.vc_set_cartesian_velocity([0, 0, 0, 0, 0, 0])
        arm.set_state(4)
        print("Arm stopped safely.")
    except Exception as e:
        print(f"Error occurred: {e}")
        arm.vc_set_cartesian_velocity([0, 0, 0, 0, 0, 0])
        arm.set_state(4)
        print("Emergency stop activated.")