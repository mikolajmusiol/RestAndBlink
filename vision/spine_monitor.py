import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque

mp_pose = mp.solutions.pose


class PostureTracker:
    def __init__(self, smooth_window=10):
        self.cap = cv2.VideoCapture(0)
        self.pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)
        self.history = deque(maxlen=smooth_window)
        self.h, self.w = 0, 0

        # Kalibracja
        self.calibrated = False
        self.base_dy = 0.0
        self.base_dz = 0.0
        self.base_torso_angle = 0.0
        self.threshold_y = 0.05     # różnica pionowa
        self.threshold_z = 0.07     # różnica głębokości
        self.threshold_torso = 10.0 # różnica kąta (stopnie)

    def _get_point(self, landmarks, idx):
        p = landmarks[idx]
        return np.array([p.x, p.y, p.z])

    def _visible(self, landmarks, idx):
        return landmarks[idx].visibility > 0.5

    def _angle(self, a, b, c):
        """Kąt między trzema punktami (a-b-c)."""
        a, b, c = np.array(a), np.array(b), np.array(c)
        ab = a - b
        cb = c - b
        cosine = np.dot(ab, cb) / (np.linalg.norm(ab) * np.linalg.norm(cb) + 1e-6)
        return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))

    def get_points(self, landmarks):
        """Wyznacz kluczowe średnie punkty: ucho, bark, biodro."""
        ears = []
        shoulders = []
        hips = []

        for l_idx, r_idx in [
            (mp_pose.PoseLandmark.LEFT_EAR.value, mp_pose.PoseLandmark.RIGHT_EAR.value),
            (mp_pose.PoseLandmark.LEFT_SHOULDER.value, mp_pose.PoseLandmark.RIGHT_SHOULDER.value),
            (mp_pose.PoseLandmark.LEFT_HIP.value, mp_pose.PoseLandmark.RIGHT_HIP.value)
        ]:
            valid = []
            for i in [l_idx, r_idx]:
                if self._visible(landmarks, i):
                    valid.append(self._get_point(landmarks, i))
            if valid:
                if l_idx == mp_pose.PoseLandmark.LEFT_EAR.value:
                    ears.append(np.mean(valid, axis=0))
                elif l_idx == mp_pose.PoseLandmark.LEFT_SHOULDER.value:
                    shoulders.append(np.mean(valid, axis=0))
                elif l_idx == mp_pose.PoseLandmark.LEFT_HIP.value:
                    hips.append(np.mean(valid, axis=0))

        if not ears or not shoulders:
            return None, None, None

        return ears[0], shoulders[0], hips[0] if hips else None

    def measure_posture(self, landmarks):
        ear, shoulder, hip = self.get_points(landmarks)
        if ear is None or shoulder is None:
            return None

        dy = ear[1] - shoulder[1]  # różnica pionowa
        dz = shoulder[2] - ear[2]  # przód-tył

        shoulder_width = abs(
            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x -
            landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x
        )
        dy /= shoulder_width
        dz /= shoulder_width

        # Kąt nachylenia tułowia (biodro-ramię-ucho)
        torso_angle = self._angle(hip, shoulder, ear) if hip is not None else 90.0

        return dy, dz, torso_angle, ear, shoulder, hip

    def check_posture(self, show_frame=False):
        ret, frame = self.cap.read()
        if not ret:
            return None

        self.h, self.w, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)

        if results.pose_landmarks:
            values = self.measure_posture(results.pose_landmarks.landmark)
            if not values:
                return None
            dy, dz, torso_angle, ear, shoulder, hip = values

            self.history.append((dy, dz, torso_angle))
            dy_s, dz_s, torso_s = np.mean(self.history, axis=0)

            # Kalibracja
            if not self.calibrated:
                color = (255, 255, 0)
                label = "Press C to calibrate"
                is_straight = None
            else:
                diff_y = abs(dy_s - self.base_dy)
                diff_z = abs(dz_s - self.base_dz)
                diff_t = abs(torso_s - self.base_torso_angle)
                is_straight = (
                    diff_y < self.threshold_y and
                    diff_z < self.threshold_z and
                    diff_t < self.threshold_torso
                )
                color = (0, 255, 0) if is_straight else (0, 0, 255)
                label = f"{'OK' if is_straight else 'SLOUCH'} dy={diff_y:.3f} dz={diff_z:.3f} t={diff_t:.1f}°"

            if show_frame:
                def draw_point(p):
                    if p is not None:
                        cv2.circle(frame, (int(p[0]*self.w), int(p[1]*self.h)), 6, color, -1)

                draw_point(ear)
                draw_point(shoulder)
                draw_point(hip)
                if shoulder is not None and ear is not None:
                    cv2.line(frame, (int(ear[0]*self.w), int(ear[1]*self.h)),
                             (int(shoulder[0]*self.w), int(shoulder[1]*self.h)), color, 2)
                if hip is not None and shoulder is not None:
                    cv2.line(frame, (int(hip[0]*self.w), int(hip[1]*self.h)),
                             (int(shoulder[0]*self.w), int(shoulder[1]*self.h)), color, 2)
                cv2.putText(frame, label, (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                cv2.imshow("Posture Tracker", frame)

            return is_straight, dy_s, dz_s, torso_s

        return None

    def calibrate(self):
        if len(self.history) < 3:
            print("Zbyt mało danych do kalibracji – usiądź prosto i chwilę poczekaj.")
            return
        self.base_dy, self.base_dz, self.base_torso_angle = np.mean(self.history, axis=0)
        self.calibrated = True
        print(f"[KALIBRACJA] dy={self.base_dy:.3f}, dz={self.base_dz:.3f}, torso={self.base_torso_angle:.1f}°")

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    tracker = PostureTracker(smooth_window=10)
    print("Uruchomiono PostureTracker PRO. Naciśnij 'C' aby skalibrować, ESC aby wyjść.")

    try:
        while True:
            result = tracker.check_posture(show_frame=True)
            key = cv2.waitKey(1) & 0xFF

            if key == 27:  # ESC
                break
            elif key == ord('c'):
                tracker.calibrate()

            if result and tracker.calibrated:
                straight, dy, dz, torso = result
                print(f"Prosto: {straight}, dy={dy:.3f}, dz={dz:.3f}, torso={torso:.1f}°")

            time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    finally:
        tracker.release()
