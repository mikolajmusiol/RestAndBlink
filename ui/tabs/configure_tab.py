"""
camera_config_demo.py
Demo: ConfigureTab - Camera preview + calibration saving
- DPI-aware UIScaling
- Stable camera preview (no growth loop)
- SQLite saving of calibration entries
"""
import sys
import os
import logging
import sqlite3
import datetime
import cv2
import numpy as np

# --- Qt imports ---
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QProgressBar, QPushButton, QFrame, QScrollArea,
    QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QImage, QPixmap, QGuiApplication

# Optional: screeninfo and mediapipe
try:
    from screeninfo import get_monitors
except Exception:
    def get_monitors():
        return []

try:
    import mediapipe as mp
    MP_AVAILABLE_GLOBAL = True
    mp_face_mesh = mp.solutions.face_mesh
except Exception:
    MP_AVAILABLE_GLOBAL = False
    mp_face_mesh = None

# --- Logging ---
LOG_PATH = os.path.join(os.path.dirname(__file__), "camera_debug.log")
logging.basicConfig(filename=LOG_PATH, level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger().addHandler(logging.StreamHandler())


# --- Windows DPI awareness: do this BEFORE creating QApplication ---
if sys.platform == "win32":
    try:
        from ctypes import windll
        try:
            # Windows 10+ per-monitor v2
            windll.user32.SetProcessDpiAwarenessContext(-4)
        except Exception:
            try:
                windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
            except Exception:
                pass
    except Exception:
        pass


# === UIScaling class ===
class UIScaling:
    """Handles UI scaling calculations and font management, DPI-aware."""

    def __init__(self):
        self.ui_scale = 1.0
        self.font_scale = 1.0
        self.calculate_ui_scaling()

    def calculate_ui_scaling(self):
        """Calculate UI scaling factor based on screen DPI and resolution."""
        try:
            app = QGuiApplication.instance()
            if app is None:
                # If called before app exists, leave defaults
                self.ui_scale = 1.0
                self.font_scale = 1.0
                return

            screen = app.primaryScreen()
            if not screen:
                self.ui_scale = 1.0
                self.font_scale = 1.0
                return

            dpi_x = screen.logicalDotsPerInchX()
            dpi_y = screen.logicalDotsPerInchY()
            dpi = (dpi_x + dpi_y) / 2.0

            base_dpi = 96.0
            dpi_scale = dpi / base_dpi

            geom = screen.geometry()
            screen_w, screen_h = geom.width(), geom.height()
            base_w, base_h = 1920.0, 1080.0
            res_scale = min(screen_w / base_w, screen_h / base_h)

            combined = max(dpi_scale, res_scale)

            # Snap to common steps for predictability
            steps = [0.8, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5]
            closest = min(steps, key=lambda s: abs(s - combined))

            self.ui_scale = max(0.8, min(2.5, closest))
            self.font_scale = max(0.9, min(2.0, self.ui_scale * 0.95))

            logging.info(f"[UIScaling] Screen {screen_w}x{screen_h}, dpi={dpi:.1f} -> ui_scale={self.ui_scale}")
        except Exception as e:
            logging.exception("Error calculating UI scaling")
            self.ui_scale = 1.0
            self.font_scale = 1.0

    def scaled_font(self, family: str, size: int, weight=QFont.Normal) -> QFont:
        scaled_size = max(1, int(size * self.font_scale))
        return QFont(family, scaled_size, weight)

    def scaled_size(self, size: int) -> int:
        return max(1, int(size * self.ui_scale))

    def get_responsive_margins(self, window_width: int) -> int:
        if window_width < 1200:
            return self.scaled_size(12)
        elif window_width < 1600:
            return self.scaled_size(18)
        else:
            return self.scaled_size(24)


# === ConfigureTab class ===
class ConfigureTab(QWidget):
    """Tab for camera and monitor configuration with calibration saving."""
    configuration_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        # provide ui_scaling either from parent or create local
        if parent and hasattr(parent, "ui_scaling"):
            self.ui_scaling = parent.ui_scaling
        else:
            self.ui_scaling = UIScaling()

        self._setup_ui()
        self._init_calibration_system()

    def _setup_ui(self):
        """Setup the configuration interface (responsive)."""
        scaler = self.ui_scaling

        # Root widget inside scroll area
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(scaler.scaled_size(20), scaler.scaled_size(12),
                                       scaler.scaled_size(20), scaler.scaled_size(12))
        root_layout.setSpacing(scaler.scaled_size(12))

        # Title
        title_label = QLabel("Konfiguracja Kamery")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(scaler.scaled_font("Segoe UI", 22))
        title_label.setStyleSheet("color: #e8e9ea; margin-top: 10px; margin-bottom: 6px;")
        root_layout.addWidget(title_label)

        # Description
        desc_label = QLabel(
            "Panel umożliwiający konfigurację kamery. Prawidłowo skonfigurowana kamera umożliwia detekcję aktywności na wielu monitorach."
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(scaler.scaled_font("Segoe UI", 12))
        desc_label.setStyleSheet("color: #a8b5c1; margin-bottom: 6px;")
        root_layout.addWidget(desc_label)

        # Camera preview container
        cam_frame = QFrame()
        cam_layout = QVBoxLayout(cam_frame)
        cam_layout.setContentsMargins(0, 0, 0, 0)
        cam_layout.setSpacing(6)

        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)

        # Important: do NOT let label control vertical growth; fix height, allow width to expand
        min_w = scaler.scaled_size(320)
        min_h = scaler.scaled_size(240)
        self.camera_label.setMinimumSize(min_w, min_h)
        self.camera_label.setMaximumHeight(scaler.scaled_size(480))
        self.camera_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # Set an initial fixed height to stabilize layout (height controlled by layout, not pixmap)
        self.camera_label.setFixedHeight(scaler.scaled_size(360))
        # We will scale pixmap ourselves; avoid QLabel changing its hint based on pixmap
        self.camera_label.setScaledContents(False)
        self.camera_label.setStyleSheet("border: 2px solid #2c3e50; border-radius: 10px; background: black;")
        cam_layout.addWidget(self.camera_label)

        root_layout.addWidget(cam_frame)

        # Status label
        self.status_label = QLabel("Kliknij przycisk, aby rozpocząć konfigurację kamery.")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(scaler.scaled_font("Segoe UI", 11))
        self.status_label.setStyleSheet("color: #f0f0f0; margin: 6px;")
        root_layout.addWidget(self.status_label)

        # History list
        #self.eyes_list = QListWidget()
        #self.eyes_list.setStyleSheet("""
        #    QListWidget { color: #e8e9ea; background: #111214; border: 1px solid #2c3e50; border-radius: 5px; padding: 6px;}
        #    QListWidget::item { padding: 6px; margin: 2px; }
        #    QListWidget::item:selected { background: #2c3e50; }
        #""")
        #self.eyes_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        #self.eyes_list.setMinimumHeight(scaler.scaled_size(120))
        #self.eyes_list.setMaximumHeight(scaler.scaled_size(260))
        #root_layout.addWidget(self.eyes_list)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFixedHeight(scaler.scaled_size(22))
        self.progress.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.progress.setStyleSheet("""
            QProgressBar { background: #2c3e50; color: white; border-radius: 5px; padding: 2px; }
            QProgressBar::chunk { background: #1abc9c; border-radius: 3px; }
        """)
        root_layout.addWidget(self.progress)

        # Button
        self.calibrate_btn = QPushButton("Rozpocznij konfigurację kamery")
        self.calibrate_btn.setFont(scaler.scaled_font("Segoe UI", 12, weight=QFont.Bold))
        self.calibrate_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.calibrate_btn.setMinimumSize(scaler.scaled_size(160), scaler.scaled_size(44))
        self.calibrate_btn.setStyleSheet("""
            QPushButton { background-color: #1abc9c; color: white; padding: 8px 16px; border-radius: 6px; }
            QPushButton:hover { background-color: #16a085; } QPushButton:pressed { background-color: #138d75; }
        """)
        self.calibrate_btn.clicked.connect(self.start_calibration)
        root_layout.addWidget(self.calibrate_btn, alignment=Qt.AlignCenter)

        root_layout.addStretch()

        # Put root inside scroll area
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameStyle(QFrame.NoFrame)
        scroll.setWidget(root)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    # --- Calibration system initialization ---
    def _init_calibration_system(self):
        self.cap = {"obj": None}
        self.timer = QTimer()
        try:
            self.monitors = get_monitors()
        except Exception:
            logging.exception("get_monitors failed")
            self.monitors = []
        self.num_monitors = max(1, len(self.monitors))
        self.current_index = {"i": 0}
        self.timer_connected = {"v": False}
        self.calibration_active = {"v": False}
        self.calibration_templates = []

        # detection init
        self._init_eye_detection()

    def _init_eye_detection(self):
        """Initialize MediaPipe (if available) and Haar fallback."""
        self.MP_AVAILABLE = False
        self.face_mesh = None
        global MP_AVAILABLE_GLOBAL, mp_face_mesh
        try:
            if MP_AVAILABLE_GLOBAL and mp_face_mesh is not None:
                self.MP_AVAILABLE = True
                self.face_mesh = mp_face_mesh.FaceMesh(
                    static_image_mode=False, max_num_faces=1, refine_landmarks=True,
                    min_detection_confidence=0.5, min_tracking_confidence=0.5
                )
                logging.info("MediaPipe initialized")
        except Exception:
            logging.exception("MediaPipe init failed")
            self.MP_AVAILABLE = False
            self.face_mesh = None

        # Haar fallback
        self.eye_cascade = None
        try:
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
            if self.eye_cascade.empty():
                self.eye_cascade = None
        except Exception:
            self.eye_cascade = None
            logging.warning("Haar cascade not available")

    # --- detection & head pose (same approach as you had) ---
    def estimate_head_pose(self, landmarks, image_shape):
        try:
            h, w = image_shape[0], image_shape[1]
            idx_map = {"nose": 1, "l_eye": 33, "r_eye": 263, "l_mouth": 61, "r_mouth": 291, "chin": 199}
            image_points = np.array([
                (landmarks[idx_map["nose"]].x * w, landmarks[idx_map["nose"]].y * h),
                (landmarks[idx_map["l_eye"]].x * w, landmarks[idx_map["l_eye"]].y * h),
                (landmarks[idx_map["r_eye"]].x * w, landmarks[idx_map["r_eye"]].y * h),
                (landmarks[idx_map["l_mouth"]].x * w, landmarks[idx_map["l_mouth"]].y * h),
                (landmarks[idx_map["r_mouth"]].x * w, landmarks[idx_map["r_mouth"]].y * h),
                (landmarks[idx_map["chin"]].x * w, landmarks[idx_map["chin"]].y * h)
            ], dtype=np.float64)
            model_points = np.array([
                (0.0, 0.0, 0.0),
                (-60.0, -40.0, -30.0),
                (60.0, -40.0, -30.0),
                (-50.0, 40.0, -60.0),
                (50.0, 40.0, -60.0),
                (0.0, 110.0, -20.0)
            ], dtype=np.float64)
            focal_length = w
            center = (w / 2, h / 2)
            camera_matrix = np.array([[focal_length, 0, center[0]],
                                      [0, focal_length, center[1]],
                                      [0, 0, 1]], dtype=np.float64)
            dist_coeffs = np.zeros((4, 1))
            success, rotation_vector, translation_vector = cv2.solvePnP(
                model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
            )
            if not success:
                return False, (0.0, 0.0, 0.0)
            rmat, _ = cv2.Rodrigues(rotation_vector)
            sy = np.sqrt(rmat[0, 0] * rmat[0, 0] + rmat[1, 0] * rmat[1, 0])
            singular = sy < 1e-6
            if not singular:
                x = np.arctan2(rmat[2, 1], rmat[2, 2])
                y = np.arctan2(-rmat[2, 0], sy)
                z = np.arctan2(rmat[1, 0], rmat[0, 0])
            else:
                x = np.arctan2(-rmat[1, 2], rmat[1, 1])
                y = np.arctan2(-rmat[2, 0], sy)
                z = 0.0
            pitch = np.degrees(x)
            yaw = np.degrees(y)
            roll = np.degrees(z)
            return True, (yaw, pitch, roll)
        except Exception:
            logging.exception("estimate_head_pose failed")
            return False, (0.0, 0.0, 0.0)

    def detect_eyes_in_frame(self, frame):
        try:
            h, w = frame.shape[:2]
            if self.MP_AVAILABLE and self.face_mesh is not None:
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(img_rgb)
                if results and getattr(results, "multi_face_landmarks", None):
                    lm = results.multi_face_landmarks[0].landmark
                    left_idxs = [33, 133, 160, 159, 158, 157, 173, 246]
                    right_idxs = [362, 263, 387, 386, 385, 384, 398, 466]
                    def avg_points(idxs):
                        xs = [lm[i].x for i in idxs if i < len(lm)]
                        ys = [lm[i].y for i in idxs if i < len(lm)]
                        if not xs:
                            return None
                        return (int(sum(xs) / len(xs) * w), int(sum(ys) / len(ys) * h))
                    left = avg_points(left_idxs)
                    right = avg_points(right_idxs)
                    return left, right, lm
            if self.eye_cascade is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                eyes = self.eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))
                eyes = sorted(eyes, key=lambda e: e[0])
                if len(eyes) >= 2:
                    l, r = eyes[0], eyes[1]
                    left_center = (int(l[0] + l[2] / 2), int(l[1] + l[3] / 2))
                    right_center = (int(r[0] + r[2] / 2), int(r[1] + r[3] / 2))
                    return left_center, right_center, None
                elif len(eyes) == 1:
                    e = eyes[0]
                    center = (int(e[0] + e[2] / 2), int(e[1] + e[3] / 2))
                    return center, None, None
        except Exception:
            logging.exception("detect_eyes_in_frame exception")
        return None, None, None

    def update_frame(self):
        """Read camera, detect, and draw — scale pixmap to fit label (do not resize label)."""
        try:
            if self.cap["obj"] is None:
                return
            ret, frame = self.cap["obj"].read()
            if not ret or frame is None:
                return

            left, right, lm = self.detect_eyes_in_frame(frame)
            head = None
            if self.MP_AVAILABLE and lm is not None:
                ok, head = self.estimate_head_pose(lm, frame.shape)
                if ok:
                    self.camera_label._last_head = head
                else:
                    self.camera_label._last_head = None
            else:
                self.camera_label._last_head = None

            vis = frame.copy()
            if left:
                cv2.circle(vis, left, 4, (0, 255, 0), -1)
            if right:
                cv2.circle(vis, right, 4, (0, 255, 0), -1)
            if getattr(self.camera_label, "_last_head", None):
                yv, pv, rv = self.camera_label._last_head
                cv2.putText(vis, f"yaw:{yv:.1f} pitch:{pv:.1f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 50), 2)

            # Convert and scale pixmap to label size (without changing label size)
            frame_rgb = cv2.cvtColor(vis, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pix = QPixmap.fromImage(qimg)

            lbl_w = max(1, self.camera_label.width())
            lbl_h = max(1, self.camera_label.height())

            scaled = pix.scaled(lbl_w, lbl_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.camera_label.setPixmap(scaled)

            # store detections
            self.camera_label._last_left = left
            self.camera_label._last_right = right

        except Exception:
            logging.exception("Exception in update_frame")
            self.safe_release()
            self.status_label.setText("❌ Błąd przetwarzania kamery. Sprawdź logi.")
            self.calibrate_btn.setEnabled(True)
            self.calibration_active["v"] = False

    def record_current_monitor_and_continue(self):
        try:
            left = getattr(self.camera_label, "_last_left", None)
            right = getattr(self.camera_label, "_last_right", None)
            head = getattr(self.camera_label, "_last_head", None)
            mi = self.current_index['i'] + 1

            logging.info(f"Recorded monitor {mi}: left={left}, right={right}, head={head}")
            self.calibration_templates.append({"monitor": mi, "left": left, "right": right, "head": head})

            item_text = f"Ekran {mi}: head={head}, left={left}, right={right}"
            #self.eyes_list.addItem(QListWidgetItem(item_text))
            self.status_label.setText(f"Zarejestrowano pozycję oczu dla ekranu {mi}.")

            # save
            self._save_configuration_to_db(mi, left, right, head)
        except Exception:
            logging.exception("Error saving eye data")
            self.status_label.setText("❌ Błąd zapisu pozycji oczu.")

        self.current_index['i'] += 1
        self.progress.setValue(int(self.current_index['i'] / self.num_monitors * 100))
        QTimer.singleShot(800, self.next_monitor_step)

    def _save_configuration_to_db(self, monitor_num, left, right, head):
        try:
            db_path = os.path.join(os.path.dirname(__file__), "user_data.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            head_yaw, head_pitch, head_roll = head if head else (None, None, None)
            left_x, left_y = left if left else (None, None)
            right_x, right_y = right if right else (None, None)
            created_at = datetime.datetime.now().isoformat(timespec='seconds')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS calibration_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    monitor INTEGER,
                    head_yaw REAL,
                    head_pitch REAL,
                    head_roll REAL,
                    left_x INTEGER,
                    left_y INTEGER,
                    right_x INTEGER,
                    right_y INTEGER,
                    created_at TEXT
                )
            ''')

            cursor.execute('''
                INSERT INTO calibration_templates
                (monitor, head_yaw, head_pitch, head_roll, left_x, left_y, right_x, right_y, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (monitor_num, head_yaw, head_pitch, head_roll, left_x, left_y, right_x, right_y, created_at))

            conn.commit()
            conn.close()
            logging.info(f"Saved configuration for monitor {monitor_num}")
        except Exception:
            logging.exception("Error saving configuration to database")

    def next_monitor_step(self):
        try:
            total = self.num_monitors
            if self.current_index['i'] >= total:
                self.safe_release()
                self.status_label.setText("✅ Konfiguracja zakończona.")
                self.progress.setValue(100)
                self.calibrate_btn.setEnabled(True)
                self.calibration_active['v'] = False
                self.configuration_updated.emit()
                return

            mon = self.monitors[self.current_index['i']] if self.monitors else None
            if mon:
                self.status_label.setText(
                    f"📺 Ekran {self.current_index['i'] + 1}/{total} — ({getattr(mon,'width', '?')}x{getattr(mon,'height','?')}). Popatrz teraz."
                )
            else:
                self.status_label.setText(f"Ekran {self.current_index['i'] + 1}/{total}. Popatrz teraz.")
            QTimer.singleShot(2000, self.record_current_monitor_and_continue)
        except Exception:
            logging.exception("next_monitor_step error")
            self.safe_release()
            self.status_label.setText("❌ Błąd w procesie konfiguracji.")
            self.calibrate_btn.setEnabled(True)
            self.calibration_active['v'] = False

    def start_calibration(self):
        if self.calibration_active['v']:
            return
        self.calibration_active['v'] = True
        self.calibrate_btn.setEnabled(False)
        self.current_index['i'] = 0
        self.progress.setValue(0)
        #self.eyes_list.clear()
        self.calibration_templates.clear()

        self.status_label.setText("Inicjalizuję kamerę...")
        logging.info("Starting camera calibration")
        try:
            try:
                self.cap["obj"] = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            except Exception:
                self.cap["obj"] = cv2.VideoCapture(0)

            if not (self.cap["obj"] and self.cap["obj"].isOpened()):
                self.status_label.setText("❌ Nie udało się otworzyć kamery.")
                logging.error("Camera initialization failed")
                self.cap["obj"] = None
                self.calibrate_btn.setEnabled(True)
                self.calibration_active['v'] = False
                return

            if not self.timer_connected["v"]:
                self.timer.timeout.connect(self.update_frame)
                self.timer_connected["v"] = True
            self.timer.start(30)
            QTimer.singleShot(800, self.next_monitor_step)
        except Exception:
            logging.exception("start_calibration failed")
            self.status_label.setText("❌ Błąd inicjalizacji kamery.")
            self.safe_release()
            self.calibrate_btn.setEnabled(True)
            self.calibration_active['v'] = False

    def safe_release(self):
        try:
            if self.cap.get("obj") is not None:
                try:
                    self.cap["obj"].release()
                except Exception:
                    logging.exception("Camera release failed")
                self.cap["obj"] = None
            if self.timer.isActive():
                self.timer.stop()
            if self.timer_connected["v"]:
                try:
                    self.timer.timeout.disconnect(self.update_frame)
                except Exception:
                    pass
                self.timer_connected["v"] = False
        except Exception:
            logging.exception("safe_release exception")
        try:
            if self.face_mesh is not None:
                try:
                    self.face_mesh.close()
                except Exception:
                    pass
        except Exception:
            pass

    def closeEvent(self, event):
        self.safe_release()
        super().closeEvent(event)

