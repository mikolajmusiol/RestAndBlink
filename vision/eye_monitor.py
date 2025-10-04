# eye_monitor.py (Zaktualizowany)
import cv2
import mediapipe as mp
import numpy as np
import time

from PyQt5.QtCore import QThread, pyqtSignal

# ---- MediaPipe ----
mp_face_mesh = mp.solutions.face_mesh

# ---- Punkty oczu ----
LEFT_EYE_LANDMARKS = [33, 133, 159, 145]
RIGHT_EYE_LANDMARKS = [362, 263, 386, 374]


class EyeTracker:
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

    def eye_ratio(self, eye_points, landmarks):
        points = np.array([(landmarks[i].x * self.w, landmarks[i].y * self.h) for i in eye_points])
        x_min, y_min = np.min(points, axis=0)
        x_max, y_max = np.max(points, axis=0)
        eye_center = np.mean(points, axis=0)
        return eye_center, (x_min, y_min, x_max, y_max)

    def gaze_angles(self, eye_center, pupil, eye_width, eye_height):
        dx = (pupil[0] - eye_center[0]) / eye_width
        dy = (pupil[1] - eye_center[1]) / eye_height
        angle_x = dx * 30
        angle_y = dy * 20
        return angle_x, angle_y

    def get_gaze(self, show_frame=False):
        ret, frame = self.cap.read()
        if not ret:
            return None

        self.h, self.w, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)

        looking_at_screen, avg_angle_x, avg_angle_y = None, None, None

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0].landmark

            if len(face_landmarks) <= 473:
                return None

            # Środek oczu i prostokąty
            left_eye_center, (lx1, ly1, lx2, ly2) = self.eye_ratio(LEFT_EYE_LANDMARKS, face_landmarks)
            right_eye_center, (rx1, ry1, rx2, ry2) = self.eye_ratio(RIGHT_EYE_LANDMARKS, face_landmarks)

            # Źrenice
            left_pupil = np.array([face_landmarks[468].x * self.w, face_landmarks[468].y * self.h])
            right_pupil = np.array([face_landmarks[473].x * self.w, face_landmarks[473].y * self.h])

            # Kąty patrzenia
            angle_x_left, angle_y_left = self.gaze_angles(left_eye_center, left_pupil, lx2 - lx1, ly2 - ly1)
            angle_x_right, angle_y_right = self.gaze_angles(right_eye_center, right_pupil, rx2 - rx1, ry2 - ry1)
            avg_angle_x = (angle_x_left + angle_x_right) / 2
            avg_angle_y = (angle_y_left + angle_y_right) / 2

            # Czy patrzy w ekran
            left_dx = (left_pupil[0] - left_eye_center[0]) / (lx2 - lx1)
            right_dx = (right_pupil[0] - right_eye_center[0]) / (rx2 - rx1)
            avg_dx = (left_dx + right_dx) / 2

            left_dy = (left_pupil[1] - left_eye_center[1]) / (ly2 - ly1)
            right_dy = (right_pupil[1] - right_eye_center[1]) / (ry2 - ry1)
            avg_dy = (left_dy + right_dy) / 2

            looking_at_screen = abs(avg_dx) < 0.15 and abs(avg_dy) < 0.15
            if looking_at_screen:
                self.last_focus_time = time.time()
            else:
                if time.time() - self.last_focus_time > self.rest_threshold:
                    looking_at_screen = False

            if show_frame:
                color = (0, 255, 0) if looking_at_screen else (0, 0, 255)
                cv2.rectangle(frame, (int(lx1), int(ly1)), (int(lx2), int(ly2)), color, 1)
                cv2.rectangle(frame, (int(rx1), int(ry1)), (int(rx2), int(ry2)), color, 1)
                cv2.circle(frame, tuple(left_pupil.astype(int)), 2, (255, 0, 0), -1)
                cv2.circle(frame, tuple(right_pupil.astype(int)), 2, (255, 0, 0), -1)
                cv2.putText(frame, f"X:{avg_angle_x:.1f} Y:{avg_angle_y:.1f}", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        if show_frame:
            cv2.imshow("Eye Tracker", frame)
            cv2.waitKey(1)

        if looking_at_screen is not None:
            return looking_at_screen, avg_angle_x, avg_angle_y
        return None

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()


class EyeMonitorWorker(QThread):
    """
    Wątek roboczy do obsługi EyeTracker (OpenCV), aby nie blokować UI.
    """
    gaze_detected_signal = pyqtSignal(bool, float, float)

    def __init__(self, tracker_instance, parent=None, debounce_time=0.5):
        super().__init__(parent)
        self.running = True
        self.tracker = tracker_instance
        self.check_interval_ms = 100

        # Histereza czasowa (debouncing)
        self.debounce_time = debounce_time  # Czas w sekundach (domyślnie 1.5s)
        self.last_state_change_time = time.time()
        self.current_state = None  # Aktualny "oficjalny" stan
        self.pending_state = None  # Stan który czeka na potwierdzenie
        self.pending_state_start = None  # Kiedy rozpoczął się pending state

    def run(self):
        """Główna pętla wątku monitorującego z debouncing."""
        while self.running:
            start_time = time.time()

            # 1. Wywołanie metody śledzenia wzroku
            result = self.tracker.get_gaze(show_frame=False)

            if result:
                looking, x, y = result
                current_time = time.time()

                if self.current_state is None:
                    self.current_state = looking
                    self.gaze_detected_signal.emit(looking, x, y)

                elif looking != self.current_state:
                    if self.pending_state != looking:
                        self.pending_state = looking
                        self.pending_state_start = current_time

                    elif current_time - self.pending_state_start >= self.debounce_time:
                        self.current_state = looking
                        self.gaze_detected_signal.emit(looking, x, y)
                        self.pending_state = None
                        self.pending_state_start = None

                else:
                    if self.pending_state is not None:
                        self.pending_state = None
                        self.pending_state_start = None

            elapsed_time = time.time() - start_time
            sleep_time = (self.check_interval_ms / 1000) - elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)

    def stop(self):
        """Bezpieczne zatrzymanie wątku."""
        self.running = False
        self.wait()
        print("Eye Monitor: Zatrzymano wątek roboczy.")