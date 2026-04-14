import math
import time

eye_closed_start = None

def euclidean_dist(p1, p2):
    return math.hypot(p1[0]-p2[0], p1[1]-p2[1])

def eye_aspect_ratio(eye):
    A = euclidean_dist(eye[1], eye[5])
    B = euclidean_dist(eye[2], eye[4])
    C = euclidean_dist(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def check_drowsiness(ear, threshold_warning=0.22, threshold_critical=0.18):
    global eye_closed_start
    status = "Normal"

    if ear < threshold_critical:
        if eye_closed_start is None:
            eye_closed_start = time.time()
        elapsed = time.time() - eye_closed_start
        if elapsed >= 2:
            status = "Critical"
        elif elapsed >= 1:
            status = "Warning"
    elif ear < threshold_warning:
        if eye_closed_start is None:
            eye_closed_start = time.time()
        elapsed = time.time() - eye_closed_start
        if elapsed >= 1:
            status = "Warning"
    else:
        eye_closed_start = None
    return status
