import time

distraction_start = None

def check_distraction(head_status):
    """
    head_status: Forward, Left, Right
    """
    global distraction_start
    current_time = time.time()

    # Forward = no distraction
    if head_status == "Forward":
        distraction_start = None
        return "Normal"

    # Mirror checking allowed up to 3 sec
    if distraction_start is None:
        distraction_start = current_time

    elapsed = current_time - distraction_start

    if elapsed >= 4:
        return "Critical"
    elif elapsed >= 3:
        return "Warning"
    else:
        return "Normal"
