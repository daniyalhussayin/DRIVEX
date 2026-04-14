import cv2

class Camera:
    def __init__(self, index=0):
        self.cap = cv2.VideoCapture(index)

    def get_frame(self):
        ret, frame = self.cap.read()
        return ret, frame

    def release(self):
        self.cap.release()
