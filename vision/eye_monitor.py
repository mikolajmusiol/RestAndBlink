import cv2
import mediapipe as mp
import numpy as np
import time
import math
from PyQt5.QtCore import QThread, pyqtSignal

mp_face_mesh = mp.solutions.face_mesh


class FaceAngleTracker:
    def __init__(self, rest_threshold=10):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError("Camera not accessible")

        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
        self.last_focus_time = time.time()
        self.rest_threshold = rest_threshold
        self.h = 0
        self.w = 0

    def get_head_angles(self, landmarks):
        """Oblicz yaw i pitch (obrót i pochylenie głowy)."""
        nose = np.array([landmarks[1].x, landmarks[1].y, landmarks[1].z])
        left_eye = np.array([landmarks[33].x, landmarks[33].y, landmarks[33].z])
        right_eye = np.array([landmarks[263].x, landmarks[263].y, landmarks[263].z])
        forehead = np.array([landmarks[10].x, landmarks[10].y, landmarks[10].z])
        chin = np.array([landmarks[152].x, landmarks[152].y, landmarks[152].z])

        # Wektory osi twarzy
        horizontal = right_eye - left_eye
        vertical = chin - forehead

        yaw = math.degrees(math.atan2(horizontal[1], horizontal[0]))  # obrót w bok
        pitch = math.degrees(math.atan2(vertical[2], vertical[1]))    # pochylenie góra/dół

        return yaw, pitch

    def draw_face_mesh(self, frame, landmarks):
        """Rysuje siatkę twarzy."""
        for lm in landmarks:
            x, y = int(lm.x * self.w), int(lm.y * self.h)
            cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

        return frame

    def get_gaze(self, show_frame=False):
        ret, frame = self.cap.read()
        if not ret:
            return None

        self.h, self.w, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)

        looking_at_screen, yaw, pitch = None, None, None

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0].landmark

            yaw, pitch = self.get_head_angles(face_landmarks)

            # Czy patrzy w ekran (prosty próg)
            looking_at_screen = abs(yaw) < 10 and abs(pitch) < 10
            if looking_at_screen:
                self.last_focus_time = time.time()
            else:
                if time.time() - self.last_focus_time > self.rest_threshold:
                    looking_at_screen = False

            if show_frame:
                frame = self.draw_face_mesh(frame, face_landmarks)
                state = "Patrzysz 👀" if looking_at_screen else "Nie patrzysz 👁️"
                color = (0, 255, 0) if looking_at_screen else (0, 0, 255)
                cv2.putText(frame, f"Yaw: {yaw:.1f}°  Pitch: {pitch:.1f}°", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                cv2.putText(frame, state, (20, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        if show_frame:
            cv2.imshow("Face Angle Mesh Tracker", frame)
            cv2.waitKey(1)

        if looking_at_screen is not None:
            return looking_at_screen, yaw, pitch
        return None

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()


class EyeMonitorWorker(QThread):
    """Wątek roboczy, który używa FaceAngleTracker w tle (dla PyQt GUI)."""
    gaze_detected_signal = pyqtSignal(bool, float, float)

    def __init__(self, tracker_instance, parent=None):
        super().__init__(parent)
        self.running = True
        self.tracker = tracker_instance
        self.check_interval_ms = 100

    def run(self):
        while self.running:
            start_time = time.time()

            result = self.tracker.get_gaze(show_frame=True)
            if result:
                looking, yaw, pitch = result
                self.gaze_detected_signal.emit(looking, yaw, pitch)

            elapsed = time.time() - start_time
            sleep_time = (self.check_interval_ms / 1000) - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def stop(self):
        self.running = False
        self.wait()
        print("Eye Monitor: Zatrzymano wątek roboczy.")


if __name__ == "__main__":
    tracker = FaceAngleTracker()
    try:
        while True:
            result = tracker.get_gaze(show_frame=True)
            if result:
                looking, yaw, pitch = result
                print(f"Patrzy w ekran: {looking}, Yaw: {yaw:.1f}°, Pitch: {pitch:.1f}°")
            time.sleep(0.3)
    except KeyboardInterrupt:
        tracker.release()
