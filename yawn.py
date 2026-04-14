import math
import time

# Global variables
yawn_start = None
alert_triggered = False  # To prevent repeated alerts

def euclidean_dist(p1, p2):
    return math.hypot(p1[0]-p2[0], p1[1]-p2[1])

def mouth_aspect_ratio(mouth_points):
    upper = mouth_points[13]
    lower = mouth_points[14]
    left = mouth_points[61]
    right = mouth_points[291]

    vertical = math.hypot(upper[0]-lower[0], upper[1]-lower[1])
    horizontal = math.hypot(left[0]-right[0], left[1]-right[1])
    mar = vertical / horizontal
    return mar

def check_yawn_status(mar, threshold_open=0.35):
    """
    Mouth open detection:
    - Normal: mouth closed
    - Warning: mouth open 2-3 seconds
    - Critical: mouth open >3 seconds
    """
    global yawn_start, alert_triggered
    current_time = time.time()

    # Mouth closed
    if mar < threshold_open:
        yawn_start = None
        alert_triggered = False
        return "Normal"

    # Mouth open
    if yawn_start is None:
        yawn_start = current_time
        alert_triggered = False

    elapsed = current_time - yawn_start

    # Determine status
    if elapsed >= 3.0:
        if not alert_triggered:
            alert_triggered = True
            # beep() # trigger beep once
        return "Critical"
    elif elapsed >= 1.0:
        if not alert_triggered:
            alert_triggered = True
            # beep() # trigger beep once
        return "Warning"
    else:
        return "Normal"
