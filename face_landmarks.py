import cv2
import mediapipe as mp

class FaceLandmarks:
    def __init__(self, static_mode=False, max_faces=1, min_det_conf=0.5, min_track_conf=0.5):
        # Standard import works for all OS
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_draw = mp.solutions.drawing_utils

        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=static_mode,
            max_num_faces=max_faces,
            min_detection_confidence=min_det_conf,
            min_tracking_confidence=min_track_conf
        )

    def get_landmarks(self, frame):
        """
        Returns landmarks as list of (x, y) coordinates
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0]
            h, w, _ = frame.shape
            landmark_list = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks.landmark]
            return landmark_list
        return None
