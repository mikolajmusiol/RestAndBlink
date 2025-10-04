import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque
from scipy.signal import detrend
from numpy.fft import fft, fftfreq

mp_face_mesh = mp.solutions.face_mesh
BUFFER_SIZE = 150
FOREHEAD_CENTER_INDEX = 10
ROI_SIZE = 25


class HeartRateMonitor:
    """Monitor tętna oparty o analizę zmian koloru twarzy w czasie rzeczywistym."""
    def __init__(self, buffer_size=BUFFER_SIZE):
        self.cap = cv2.VideoCapture(0)
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.raw_signal = deque(maxlen=buffer_size)
        self.times = deque(maxlen=buffer_size)
        self.last_calc_time = time.time()
        self.estimated_hr = 0
        self.w, self.h = 0, 0
        self.pulse_values = deque(maxlen=30)

    def get_roi_color(self, frame, landmarks):
        """Średni kolor z fragmentu czoła."""
        p = landmarks[FOREHEAD_CENTER_INDEX]
        cx, cy = int(p.x * self.w), int(p.y * self.h)
        x1, y1 = max(0, cx - ROI_SIZE), max(0, cy - ROI_SIZE)
        x2, y2 = min(self.w, cx + ROI_SIZE), min(self.h, cy + ROI_SIZE)
        roi = frame[y1:y2, x1:x2]
        if roi.size > 0:
            avg_color = np.mean(roi, axis=(0, 1))
            self.pulse_values.append(avg_color[1])
            return avg_color[1]
        return None

    def analyze_signal(self):
        """Analiza sygnału PPG przez FFT."""
        if len(self.raw_signal) < BUFFER_SIZE:
            return self.estimated_hr
        signal = np.array(self.raw_signal)
        times = np.array(self.times)
        signal = detrend(signal)
        if np.std(signal) == 0:
            return self.estimated_hr
        signal = signal / np.std(signal)
        fps = (len(times) - 1) / (times[-1] - times[0])
        if fps < 15:
            return self.estimated_hr
        fft_result = fft(signal)
        fft_abs = np.abs(fft_result[:BUFFER_SIZE // 2])
        frequencies = fftfreq(BUFFER_SIZE, 1.0 / fps)
        bpm = frequencies[:BUFFER_SIZE // 2] * 60
        mask = (bpm >= 40) & (bpm <= 180)
        bpm = bpm[mask]
        fft_abs = fft_abs[mask]
        if len(fft_abs) == 0:
            return self.estimated_hr
        return bpm[np.argmax(fft_abs)]

    def generate_full_face_heatmap(self, frame, landmarks):
        """Generuje heatmapę z punktów twarzy."""
        face_mask = np.zeros((self.h, self.w), dtype=np.float32)
        strength = np.mean(self.pulse_values) if len(self.pulse_values) else 128
        for lm in landmarks:
            x, y = int(lm.x * self.w), int(lm.y * self.h)
            if 0 <= x < self.w and 0 <= y < self.h:
                cv2.circle(face_mask, (x, y), 3, strength, -1)
        face_mask = cv2.GaussianBlur(face_mask, (51, 51), 0)
        if face_mask.max() > face_mask.min():
            face_mask = (255 * (face_mask - face_mask.min()) / (face_mask.max() - face_mask.min())).astype(np.uint8)
        heatmap = cv2.applyColorMap(face_mask, cv2.COLORMAP_JET)
        combined = cv2.addWeighted(frame, 0.6, heatmap, 0.4, 0)
        return combined

    def run(self):
        print("Real-time Heart Rate Monitor running...")
        try:
            while self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    break

                self.h, self.w, _ = frame.shape
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(frame_rgb)
                current_time = time.time()

                if results.multi_face_landmarks:
                    face_landmarks = results.multi_face_landmarks[0].landmark
                    avg_green = self.get_roi_color(frame, face_landmarks)
                    if avg_green is not None:
                        self.raw_signal.append(avg_green)
                        self.times.append(current_time)

                    # oblicz BPM co 1.5 sekundy
                    if current_time - self.last_calc_time > 1.5:
                        self.estimated_hr = self.analyze_signal()
                        self.last_calc_time = current_time

                    frame = self.generate_full_face_heatmap(frame, face_landmarks)

                cv2.putText(frame, f"HR: {int(self.estimated_hr)} BPM", (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.imshow("Heart Rate Monitor", frame)
                print(f"HR: {int(self.estimated_hr)} BPM")

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            self.cap.release()
            self.face_mesh.close()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    HeartRateMonitor().run()
