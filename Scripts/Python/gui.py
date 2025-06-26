""" 
Created by: Patton
Date Created: ??
Last Updated: 6/26/2025

Description:
  GUI using OpenCV to display PID controller information. 
  
  Modified by Miles Modeste 

TODO:
    -
"""

import cv2
import numpy as np
import time

_last_update_time = None

# Function to create a display window
cv2.namedWindow('PID Info', cv2.WINDOW_NORMAL)

# Function to update the display with PID information, current mode, and error
def update_display(percent, vel_cmd, pid, mode, error, cap_reading):
    global _last_update_time
    # Create a blank image
    display = 255 * np.ones((300, 400, 3), dtype=np.uint8)  # Increased height for additional text
    
    # Display the information
    cv2.putText(display, f'Percent: {percent:.2f}%', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    cv2.putText(display, f'Error: {error:.2f}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)  # Moved error below distance
    cv2.putText(display, f'Capacitance: {cap_reading:.2f}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)  # Added capacitance
    cv2.putText(display, f'Velocity: {vel_cmd:.2f}', (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    cv2.putText(display, f'Kp: {pid.Kp:.1f}', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    cv2.putText(display, f'Ki: {pid.Ki:.1f}', (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    cv2.putText(display, f'Kd: {pid.Kd:.1f}', (10, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    cv2.putText(display, f'Mode: {mode}', (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    if mode == 'Following Hand':
        current_time = time.time()
        if _last_update_time is not None:
            dt = current_time - _last_update_time
            freq = 1.0 / dt if dt > 0 else 0.0
        else:
            freq = 0.0
        _last_update_time = current_time
        cv2.putText(display, f'Freq: {freq:.2f} Hz', (10, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    # Show the image
    cv2.imshow('PID Info', display)
    cv2.moveWindow('PID Info', 0, 550)


# Function to handle key events using OpenCV
def get_key_cv2():
    key = cv2.waitKey(1) & 0xFF
    if key != 255:  # 255 is returned when no key is pressed
        return chr(key)
    return None

# Function to close all OpenCV windows
def close_windows():
    cv2.destroyAllWindows()