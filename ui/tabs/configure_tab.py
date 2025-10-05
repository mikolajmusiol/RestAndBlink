"""
Configuration Tab - Camera and Monitor Configuration
Enhanced version with logging and camera calibration functionality.
"""
import logging
import os
import sqlite3
import datetime
import cv2
import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, 
                           QListWidgetItem, QProgressBar, QPushButton, 
                           QFrame, QHBoxLayout, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QImage, QPixmap

try:
    from screeninfo import get_monitors
except ImportError:
    def get_monitors():
        # Fallback when screeninfo is not available
        return []

try:
    import mediapipe as mp
    MP_AVAILABLE = True
    mp_face_mesh = mp.solutions.face_mesh
except Exception:
    MP_AVAILABLE = False

# Configure logging
LOG_PATH = os.path.join(os.path.dirname(__file__), "camera_debug.log")
logging.basicConfig(filename=LOG_PATH, level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger().addHandler(logging.StreamHandler())

class ConfigureTab(QWidget):
    """Tab for camera and monitor configuration with full calibration system."""
    
    # Signal emitted when configuration changes
    configuration_updated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._setup_ui()
        self._init_calibration_system()

    def _setup_ui(self):
        """Setup the configuration interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 30)
        layout.setSpacing(20)

        # Tytuł
        title_label = QLabel("Konfiguracja Kamery")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title_label.setStyleSheet("color: #e8e9ea; margin-top: 20px;")
        layout.addWidget(title_label)

        # Opis
        desc_label = QLabel(
            "Skonfiguruj kamerę, aby umożliwić detekcję aktywności użytkownika na wszystkich monitorach.\n"
            "Upewnij się, że kamera jest włączona i skierowana na twarz."
        )
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(QFont("Segoe UI", 11))
        desc_label.setStyleSheet("color: #a8b5c1;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Podgląd kamery
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setFixedSize(640, 400)
        self.camera_label.setStyleSheet("""
            border: 2px solid #2c3e50;
            border-radius: 10px;
            background-color: black;
        """)
        layout.addWidget(self.camera_label, alignment=Qt.AlignCenter)

        # === DOLNY PANEL (pasek + przycisk) ===
        bottom_frame = QFrame()
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(15)

        # Pasek postępu
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFixedHeight(22)
        self.progress.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.progress.setStyleSheet("""
            QProgressBar {
                background: #2c3e50;
                color: white;
                border-radius: 5px;
                text-align: center;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background: #1abc9c;
                border-radius: 5px;
            }
        """)
        bottom_layout.addWidget(self.progress, stretch=3)

        # Przyciski obok paska
        self.calibrate_btn = QPushButton("Rozpocznij konfigurację")
        self.calibrate_btn.setFixedHeight(36)
        self.calibrate_btn.setStyleSheet("""
            QPushButton {
                background-color: #1abc9c;
                color: white;
                padding: 6px 18px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
            QPushButton:pressed {
                background-color: #138d75;
            }
            QPushButton:disabled {
                background-color: #5d6d7e;
                color: #aab7b8;
            }
        """)
        self.calibrate_btn.clicked.connect(self.start_calibration)
        bottom_layout.addWidget(self.calibrate_btn, stretch=1)

        layout.addWidget(bottom_frame)

        layout.addStretch()

    def _init_calibration_system(self):
        """Initialize the camera calibration system."""
        # Camera and timer setup
        self.cap = {"obj": None}
        self.timer = QTimer()
        
        # Get monitors
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
        
        # Initialize eye detection systems
        self._init_eye_detection()
    
    def _init_eye_detection(self):
        """Initialize eye detection systems (MediaPipe and Haar cascade fallback)."""
        # MediaPipe setup
        self.MP_AVAILABLE = False
        self.face_mesh = None
        try:
            if MP_AVAILABLE:
                self.MP_AVAILABLE = True
                self.face_mesh = mp_face_mesh.FaceMesh(
                    static_image_mode=False, 
                    max_num_faces=1,
                    refine_landmarks=True, 
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                logging.info("MediaPipe FaceMesh initialized successfully")
        except Exception:
            self.MP_AVAILABLE = False
            self.face_mesh = None
            logging.info("MediaPipe FaceMesh not available; using Haar fallback")
        
        # Haar cascade fallback
        self.eye_cascade = None
        try:
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
            if self.eye_cascade.empty():
                self.eye_cascade = None
        except Exception:
            self.eye_cascade = None
            logging.warning("Haar cascade eye detection not available")
    
    def estimate_head_pose(self, landmarks, image_shape):
        """Estimate head pose from facial landmarks."""
        try:
            h, w = image_shape[0], image_shape[1]
            idx_map = {
                "nose": 1, 
                "l_eye": 33, 
                "r_eye": 263, 
                "l_mouth": 61, 
                "r_mouth": 291, 
                "chin": 199
            }
            
            # 2D image points
            image_points = np.array([
                (landmarks[idx_map["nose"]].x * w, landmarks[idx_map["nose"]].y * h),
                (landmarks[idx_map["l_eye"]].x * w, landmarks[idx_map["l_eye"]].y * h),
                (landmarks[idx_map["r_eye"]].x * w, landmarks[idx_map["r_eye"]].y * h),
                (landmarks[idx_map["l_mouth"]].x * w, landmarks[idx_map["l_mouth"]].y * h),
                (landmarks[idx_map["r_mouth"]].x * w, landmarks[idx_map["r_mouth"]].y * h),
                (landmarks[idx_map["chin"]].x * w, landmarks[idx_map["chin"]].y * h)
            ], dtype=np.float64)
            
            # 3D model points
            model_points = np.array([
                (0.0, 0.0, 0.0),
                (-60.0, -40.0, -30.0),
                (60.0, -40.0, -30.0),
                (-50.0, 40.0, -60.0),
                (50.0, 40.0, -60.0),
                (0.0, 110.0, -20.0)
            ], dtype=np.float64)
            
            # Camera parameters
            focal_length = w
            center = (w / 2, h / 2)
            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]
            ], dtype=np.float64)
            
            dist_coeffs = np.zeros((4, 1))
            
            # Solve PnP
            success, rotation_vector, translation_vector = cv2.solvePnP(
                model_points, image_points, camera_matrix, dist_coeffs, 
                flags=cv2.SOLVEPNP_ITERATIVE
            )
            
            if not success:
                return False, (0.0, 0.0, 0.0)
            
            # Convert rotation vector to Euler angles
            rmat, _ = cv2.Rodrigues(rotation_vector)
            sy = np.sqrt(rmat[0, 0] ** 2 + rmat[1, 0] ** 2)
            singular = sy < 1e-6
            
            if not singular:
                x = np.arctan2(rmat[2, 1], rmat[2, 2])
                y = np.arctan2(-rmat[2, 0], sy)
                z = np.arctan2(rmat[1, 0], rmat[0, 0])
            else:
                x = np.arctan2(-rmat[1, 2], rmat[1, 1])
                y = np.arctan2(-rmat[2, 0], sy)
                z = 0.0
            
            # Convert to degrees
            pitch = np.degrees(x)
            yaw = np.degrees(y)
            roll = np.degrees(z)
            
            return True, (yaw, pitch, roll)
            
        except Exception:
            logging.exception("estimate_head_pose failed")
            return False, (0.0, 0.0, 0.0)
    
    def detect_eyes_in_frame(self, frame):
        """Detect eyes in the current frame."""
        try:
            h, w = frame.shape[:2]
            
            # Try MediaPipe first
            if self.MP_AVAILABLE and self.face_mesh is not None:
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(img_rgb)
                
                if results.multi_face_landmarks:
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
            
            # Fallback to Haar cascade
            if self.eye_cascade is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                eyes = self.eye_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30)
                )
                eyes = sorted(eyes, key=lambda e: e[0])  # Sort by x position
                
                if len(eyes) >= 2:
                    l = eyes[0]  # Left eye
                    r = eyes[1]  # Right eye
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
        """Update camera frame and detect eyes/head pose."""
        try:
            if self.cap["obj"] is None:
                return
                
            ret, frame = self.cap["obj"].read()
            if not ret or frame is None:
                return
            
            # Detect eyes and head pose
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
            
            # Draw visualization
            vis = frame.copy()
            if left:
                cv2.circle(vis, left, 4, (0, 255, 0), -1)
            if right:
                cv2.circle(vis, right, 4, (0, 255, 0), -1)
                
            # Draw head pose information
            if getattr(self.camera_label, "_last_head", None):
                yv, pv, rv = self.camera_label._last_head
                text = f"yaw:{yv:.1f} pitch:{pv:.1f}"
                cv2.putText(vis, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 50), 2)
            
            # Convert and display frame
            frame_rgb = cv2.cvtColor(vis, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pix = QPixmap.fromImage(qimg).scaled(
                self.camera_label.width(), self.camera_label.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.camera_label.setPixmap(pix)
            
            # Store current detection results
            self.camera_label._last_left = left
            self.camera_label._last_right = right
            
        except Exception:
            logging.exception("Exception in update_frame")
            self.safe_release()
            self.status_label.setText("❌ Błąd przetwarzania kamery. Sprawdź logi.")
            self.calibrate_btn.setEnabled(True)
            self.calibration_active["v"] = False
    
    def record_current_monitor_and_continue(self):
        """Record current monitor configuration and continue to next."""
        try:
            left = getattr(self.camera_label, "_last_left", None)
            right = getattr(self.camera_label, "_last_right", None)
            head = getattr(self.camera_label, "_last_head", None)
            mi = self.current_index['i'] + 1
            
            logging.info(f"Recorded monitor {mi}: left={left}, right={right}, head={head}")
            self.calibration_templates.append({
                "monitor": mi, 
                "left": left, 
                "right": right, 
                "head": head
            })
            
            # Add to display list
            item_text = f"Ekran {mi}: head={head}, left={left}, right={right}"
            self.eyes_list.addItem(QListWidgetItem(item_text))
            self.status_label.setText(f"Zarejestrowano pozycję oczu dla ekranu {mi}.")
            
            # Save to database
            self._save_configuration_to_db(mi, left, right, head)
            
        except Exception:
            logging.exception("Error saving eye data")
            self.status_label.setText("❌ Błąd zapisu pozycji oczu.")
        
        self.current_index['i'] += 1
        self.progress.setValue(int(self.current_index['i'] / self.num_monitors * 100))
        QTimer.singleShot(800, self.next_monitor_step)
    
    def _save_configuration_to_db(self, monitor_num, left, right, head):
        """Save configuration to database."""
        try:
            conn = sqlite3.connect('user_data.db')
            cursor = conn.cursor()
            
            head_yaw, head_pitch, head_roll = head if head else (None, None, None)
            left_x, left_y = left if left else (None, None)
            right_x, right_y = right if right else (None, None)
            created_at = datetime.datetime.now().isoformat(timespec='seconds')
            
            # Create table if it doesn't exist
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
        """Move to next monitor in calibration sequence."""
        try:
            total = self.num_monitors
            if self.current_index['i'] >= total:
                self.safe_release()
                self.status_label.setText("✅ Konfiguracja zakończona.")
                self.progress.setValue(100)
                self.calibrate_btn.setEnabled(True)
                self.calibration_active['v'] = False
                self.configuration_updated.emit()  # Emit signal
                return
            
            # Get current monitor info
            mon = self.monitors[self.current_index['i']] if self.monitors else None
            if mon:
                self.status_label.setText(
                    f"📺 Ekran {self.current_index['i'] + 1}/{total} — "
                    f"({mon.width}x{mon.height}). Popatrz teraz."
                )
            else:
                self.status_label.setText(
                    f"Ekran {self.current_index['i'] + 1}/{total}. Popatrz teraz."
                )
            
            QTimer.singleShot(2000, self.record_current_monitor_and_continue)
            
        except Exception:
            logging.exception("next_monitor_step error")
            self.safe_release()
            self.status_label.setText("❌ Błąd w procesie konfiguracji.")
            self.calibrate_btn.setEnabled(True)
            self.calibration_active['v'] = False
    
    def start_calibration(self):
        """Start the calibration process."""
        if self.calibration_active['v']:
            return
            
        self.calibration_active['v'] = True
        self.calibrate_btn.setEnabled(False)
        self.current_index['i'] = 0
        self.progress.setValue(0)
        self.eyes_list.clear()
        self.calibration_templates.clear()
        
        self.status_label.setText("Inicjalizuję kamerę...")
        logging.info("Starting camera calibration")
        
        try:
            # Initialize camera
            try:
                self.cap["obj"] = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            except:
                self.cap["obj"] = cv2.VideoCapture(0)
                
            if not (self.cap["obj"] and self.cap["obj"].isOpened()):
                self.status_label.setText("❌ Nie udało się otworzyć kamery.")
                logging.error("Camera initialization failed")
                self.cap["obj"] = None
                self.calibrate_btn.setEnabled(True)
                self.calibration_active['v'] = False
                return
            
            # Start camera timer
            if not self.timer_connected["v"]:
                self.timer.timeout.connect(self.update_frame)
                self.timer_connected["v"] = True
            
            self.timer.start(30)  # 30ms refresh rate
            QTimer.singleShot(800, self.next_monitor_step)
            
        except Exception:
            logging.exception("start_calibration failed")
            self.status_label.setText("❌ Błąd inicjalizacji kamery.")
            self.safe_release()
            self.calibrate_btn.setEnabled(True)
            self.calibration_active['v'] = False
    
    def safe_release(self):
        """Safely release camera and timer resources."""
        try:
            # Release camera
            if self.cap["obj"] is not None:
                try:
                    self.cap["obj"].release()
                except Exception:
                    logging.exception("Camera release failed")
                self.cap["obj"] = None
            
            # Stop timer
            if self.timer.isActive():
                self.timer.stop()
            
            # Disconnect timer
            if self.timer_connected["v"]:
                try:
                    self.timer.timeout.disconnect(self.update_frame)
                except Exception:
                    pass
                self.timer_connected["v"] = False
                
        except Exception:
            logging.exception("safe_release exception")
        
        try:
            # Close MediaPipe resources
            if self.face_mesh is not None:
                try:
                    self.face_mesh.close()
                except Exception:
                    pass
        except Exception:
            pass
    
    def closeEvent(self, event):
        """Handle widget close event."""
        self.safe_release()
        super().closeEvent(event)