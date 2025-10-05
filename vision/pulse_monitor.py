import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque
from scipy.signal import detrend
from numpy.fft import fft, fftfreq

# ---- MediaPipe Setup ----
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# ---- Stałe Konfiguracji ----
BUFFER_SIZE = 150
FOREHEAD_CENTER_INDEX = 10
ROI_SIZE = 25
MIN_FPS = 15
MIN_HR_BPM = 40
MAX_HR_BPM = 180
CALC_INTERVAL = 1.0

# --- NOWA STAŁA: Czas odświeżania wyświetlanego tętna (w sekundach) ---
DISPLAY_UPDATE_INTERVAL = 10.0


class HeartRateMonitor:
    """Monitor tętna oparty o analizę zmian koloru twarzy w czasie rzeczywistym."""

    def __init__(self, buffer_size=BUFFER_SIZE):
        self.cap = cv2.VideoCapture(0, cv2.CAP_MSMF)

        if not self.cap.isOpened():
            raise RuntimeError("Camera not accessible or currently in use.")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        self.drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.raw_signal = deque(maxlen=buffer_size)
        self.times = deque(maxlen=buffer_size)
        self.last_calc_time = time.time()

        # --- NOWE ZMIENNE DLA STABILIZACJI WYNIKU ---
        self.stable_hr = 0.0  # Wynik wyświetlany na ekranie (stabilny)
        self.last_display_update_time = time.time()  # Czas ostatniej aktualizacji stable_hr
        self.hr_history = deque(
            maxlen=int(DISPLAY_UPDATE_INTERVAL / CALC_INTERVAL) + 2)  # Historia ostatnich obliczonych HR
        # ---------------------------------------------

        self.estimated_hr = 0.0  # Wynik z ostatniej FFT (może skakać)
        self.w, self.h = 0, 0
        self.pulse_values = deque(maxlen=30)
        self.current_pulse_color = (0, 255, 255)

    # ... (draw_pulsating_face_mesh, get_roi_color, analyze_signal - BEZ ZMIAN) ...

    def draw_pulsating_face_mesh(self, frame, results, avg_green):
        """Rysuje siatkę twarzy, której kolor pulsuje zgodnie z sygnałem PPG."""

        self.pulse_values.append(avg_green)

        if len(self.pulse_values) > 1:
            min_val = np.min(self.pulse_values)
            max_val = np.max(self.pulse_values)

            pulse_ratio = 0.5
            if max_val > min_val:
                pulse_ratio = (avg_green - min_val) / (max_val - min_val)

            green_comp = int(255 * (1 - pulse_ratio))
            self.current_pulse_color = (0, green_comp, 255)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=self.drawing_spec,
                    connection_drawing_spec=mp_drawing.DrawingSpec(
                        color=self.current_pulse_color,
                        thickness=1,
                        circle_radius=1
                    )
                )

    def get_roi_color(self, frame, landmarks):
        """Średni kolor z fragmentu czoła."""
        p = landmarks[FOREHEAD_CENTER_INDEX]
        cx, cy = int(p.x * self.w), int(p.y * self.h)
        x1, y1 = max(0, cx - ROI_SIZE), max(0, cy - ROI_SIZE)
        x2, y2 = min(self.w, cx + ROI_SIZE), min(self.h, cy + ROI_SIZE)
        roi = frame[y1:y2, x1:x2]

        if roi.size > 0:
            avg_color = np.mean(roi, axis=(0, 1))
            avg_green = avg_color[1]

            cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)

            return avg_green
        return None

    def analyze_signal(self):
        """Analiza sygnału PPG przez FFT."""
        if len(self.raw_signal) < BUFFER_SIZE:
            return 0.0

        signal = np.array(self.raw_signal)
        times = np.array(self.times)

        fps = (len(times) - 1) / (times[-1] - times[0])
        if fps < MIN_FPS:
            return 0.0

        signal = detrend(signal)
        if np.std(signal) == 0:
            return 0.0
        signal = signal / np.std(signal)

        fft_result = fft(signal)
        fft_abs = np.abs(fft_result[:BUFFER_SIZE // 2])
        frequencies = fftfreq(BUFFER_SIZE, 1.0 / fps)
        bpm = frequencies[:BUFFER_SIZE // 2] * 60

        mask = (bpm >= MIN_HR_BPM) & (bpm <= MAX_HR_BPM)
        bpm = bpm[mask]
        fft_abs = fft_abs[mask]

        if len(fft_abs) == 0:
            return 0.0

        return bpm[np.argmax(fft_abs)]

    # --- Modyfikacja: Wyświetlamy stable_hr, a nie estimated_hr ---
    def draw_info(self, frame, current_fps):
        """Rysuje informacje o HR, FPS i statusie na ramce."""
        # Używamy stable_hr do wyświetlania
        status_text = f"HR: {int(self.stable_hr)} BPM" if self.stable_hr > 0 else "HR: Kalibracja..."
        hr_color = (0, 255, 0) if self.stable_hr > 0 else (0, 165, 255)

        cv2.putText(frame, status_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, hr_color, 2)
        cv2.putText(frame, f"FPS: {current_fps:.1f}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

        # Dodajemy informację o czasie do następnej aktualizacji
        time_to_update = DISPLAY_UPDATE_INTERVAL - (time.time() - self.last_display_update_time)
        if time_to_update < 0: time_to_update = 0
        cv2.putText(frame, f"NASTEPNY WYNIK: {time_to_update:.1f}s", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (255, 255, 255), 1)
        cv2.putText(frame, f"BUFOR: {len(self.raw_signal)}/{BUFFER_SIZE}", (20, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (255, 255, 255), 1)

    # --- KLUCZOWA ZMIANA: Logika aktualizacji HR ---
    def get_heart_rate(self, show_frame=False):
        ret, frame = self.cap.read()
        if not ret: return self.stable_hr

        self.h, self.w, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)
        current_time = time.time()

        current_fps = 1.0 / (current_time - self.last_calc_time) if current_time > self.last_calc_time else 0.0
        self.last_calc_time = current_time

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0].landmark

            avg_green = self.get_roi_color(frame, face_landmarks)

            if avg_green is not None:
                self.raw_signal.append(avg_green)
                self.times.append(current_time)

            # 1. PRZELICZANIE HR (częste, ale niewyświetlane)
            # Przeliczamy tylko, gdy bufor jest pełny (i co CALC_INTERVAL)
            if len(self.raw_signal) == BUFFER_SIZE or current_time - self.last_calc_time > CALC_INTERVAL:
                temp_hr = self.analyze_signal()
                if temp_hr > 0:
                    self.hr_history.append(temp_hr)  # Dodaj tylko sensowne wyniki

            # 2. STABILIZACJA WYNIKU (rzadkie, dla wyświetlania)
            if current_time - self.last_display_update_time >= DISPLAY_UPDATE_INTERVAL and len(self.hr_history) > 0:
                # Oblicz średnią z ostatnich sensownych wyników HR
                self.stable_hr = np.mean(self.hr_history)

                # Zresetuj czas i historię
                self.last_display_update_time = current_time
                self.hr_history.clear()

            # 3. WIZUALIZACJA
            if show_frame:
                # Wizualizacja siatki pulsującej jest stale aktualizowana
                if avg_green is not None:
                    self.draw_pulsating_face_mesh(frame, results, avg_green)

                self.draw_info(frame, current_fps)
                cv2.imshow("Heart Rate Monitor", frame)
                cv2.waitKey(1)

        return self.stable_hr

    def release(self):
        self.cap.release()
        self.face_mesh.close()
        cv2.destroyAllWindows()


def main():
    try:
        monitor = HeartRateMonitor()
        print(f"🔬 Uruchamianie pomiaru tętna. Wynik BPM będzie aktualizowany co {DISPLAY_UPDATE_INTERVAL} sekund.")

        while True:
            monitor.get_heart_rate(show_frame=True)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except RuntimeError as e:
        print(f"BŁĄD: {e}. Sprawdź, czy kamera jest podłączona i dostępna.")
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")
    finally:
        monitor.release()


if __name__ == "__main__":
    main()