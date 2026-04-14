from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QProgressBar
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtCore import QTimer, Qt
import cv2

from vision.camera import Camera
from vision.face_landmarks import FaceLandmarks
from detection.eye import eye_aspect_ratio, check_drowsiness
from detection.yawn import mouth_aspect_ratio, check_yawn_status
from detection.distraction import check_distraction
from detection.vigilance_logic import calculate_drowsiness_score
from utils.alerts import play_warning, play_critical
from utils.colors import NORMAL, WARNING, CRITICAL


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DRIVEX: An AI Assisted Drivers Vigilance System")
        self.setGeometry(100, 100, 900, 700)

        self.camera = Camera()
        self.face = FaceLandmarks()

        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    # ---------------- UI ----------------
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        # Camera
        self.video = QLabel()
        self.video.setStyleSheet("background-color:black;")
        layout.addWidget(self.video, stretch=7)

        # Status labels
        self.eye_lbl = self.make_label("Eye: Normal")
        self.yawn_lbl = self.make_label("Yawn: Normal")
        self.distraction_lbl = self.make_label("Distraction: Normal")
        self.head_lbl = self.make_label("Head: Forward")
        self.att_lbl = self.make_label("Attentiveness: 100%")

        layout.addWidget(self.eye_lbl)
        layout.addWidget(self.yawn_lbl)
        layout.addWidget(self.distraction_lbl)
        layout.addWidget(self.head_lbl)
        layout.addWidget(self.att_lbl)

        # Progress bar
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(100)
        self.bar.setFixedHeight(18)
        self.bar.setFixedWidth(450)

        layout.addWidget(self.bar)
        layout.addStretch(1)

        self.setLayout(layout)

    def make_label(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color:{NORMAL}; padding:3px;")
        return lbl

    # ---------------- LOGIC ----------------
    def update_frame(self):
        ret, frame = self.camera.get_frame()
        if not ret:
            return

        eye_status = yawn_status = distraction_status = "Normal"
        head_status = "Forward"

        landmarks = self.face.get_landmarks(frame)

        # -------- Driver Face Filtering --------
        if landmarks:
            h, w, _ = frame.shape

            xs = [pt[0] for pt in landmarks]
            ys = [pt[1] for pt in landmarks]

            face_width = max(xs) - min(xs)
            face_height = max(ys) - min(ys)
            face_area = face_width * face_height

            face_center_x = (max(xs) + min(xs)) // 2
            frame_center_x = w // 2

            # Ignore background / side faces
            if face_area < 8000 or abs(face_center_x - frame_center_x) > w * 0.25:
                landmarks = None

        # -------- Detection Logic --------
        if landmarks and len(landmarks) == 468:

            # -------- Eyes --------
            left_eye = [landmarks[i] for i in [33,160,158,133,153,144]]
            right_eye = [landmarks[i] for i in [362,385,387,263,373,380]]
            ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2
            eye_status = check_drowsiness(ear)

            # -------- Yawn --------
            mouth = {
                13: landmarks[13],
                14: landmarks[14],
                61: landmarks[61],
                291: landmarks[291]
            }
            mar = mouth_aspect_ratio(mouth)
            yawn_status = check_yawn_status(mar)

            # -------- Head --------
            nose = landmarks[1]
            le = landmarks[33]
            re = landmarks[263]
            dx = nose[0] - (le[0] + re[0]) / 2

            if dx > 20:
                head_status = "Right"
            elif dx < -20:
                head_status = "Left"
            else:
                head_status = "Forward"

            # -------- Distraction --------
            distraction_status = check_distraction(head_status)

            # -------- Alerts --------
            if "Critical" in [eye_status, yawn_status, distraction_status]:
                play_critical()
            elif "Warning" in [eye_status, yawn_status, distraction_status]:
                play_warning()
        # -------- Draw Face Landmarks --------
        if landmarks and len(landmarks) == 468:
            for (x, y) in landmarks:
               cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        # -------- Attentiveness --------
        score = calculate_drowsiness_score(
            eye_status, yawn_status, head_status
        )
        attentiveness = max(0, 100 - int(score * 100))

        # -------- UI UPDATE --------
        self.update_label(self.eye_lbl, "Eye", eye_status)
        self.update_label(self.yawn_lbl, "Yawn", yawn_status)
        self.update_label(self.distraction_lbl, "Distraction", distraction_status)
        self.head_lbl.setText(f"Head: {head_status}")
        self.att_lbl.setText(f"Attentiveness: {attentiveness}%")
        self.bar.setValue(attentiveness)

        if attentiveness > 70:
            self.bar.setStyleSheet("QProgressBar::chunk{background:green;}")
        elif attentiveness > 40:
            self.bar.setStyleSheet("QProgressBar::chunk{background:yellow;}")
        else:
            self.bar.setStyleSheet("QProgressBar::chunk{background:red;}")

        # -------- Show camera --------
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        qt_img = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.video.setPixmap(
            QPixmap.fromImage(qt_img).scaled(
                self.video.width(),
                self.video.height(),
                Qt.AspectRatioMode.KeepAspectRatio
            )
        )

    def update_label(self, lbl, name, status):
        color = NORMAL if status == "Normal" else WARNING if status == "Warning" else CRITICAL
        lbl.setText(f"{name}: {status}")
        lbl.setStyleSheet(f"color:{color}; padding:3px;")
