def calculate_drowsiness_score(eye_status, yawn_status, head_status):
    # Weighted sum: Eye 50%, Yawn 30%, Head Tilt 20%
    eye_score = {"Normal":0, "Warning":0.5, "Critical":1}[eye_status]
    yawn_score = {"Normal":0, "Warning":0.5, "Critical":1}[yawn_status]
    head_score = {"Forward":0, "Left":0.2, "Right":0.2}[head_status]

    score = 0.5*eye_score + 0.3*yawn_score + 0.2*head_score
    return min(score,1.0)
