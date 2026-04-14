import winsound
import time

last_alert_time = 0

def play_warning():
    global last_alert_time
    if time.time() - last_alert_time > 1:
        winsound.Beep(1000, 300)  # soft beep
        last_alert_time = time.time()

def play_critical():
    global last_alert_time
    if time.time() - last_alert_time > 1:
        winsound.Beep(1500, 700)  # loud beep
        last_alert_time = time.time()
