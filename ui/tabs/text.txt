# ui/enhanced_wellness_window.py
import logging
import os
LOG_PATH = os.path.join(os.path.dirname(__file__), "camera_debug.log")
logging.basicConfig(filename=LOG_PATH, level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger().addHandler(logging.StreamHandler())
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QStackedWidget, QFrame, QGridLayout,
                             QScrollArea, QProgressBar, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor
import sqlite3
import os
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import cv2
from screeninfo import get_monitors
# Import matplotlib for charts
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtGui import QImage, QPixmap, QFont
try:
    import mediapipe as mp
    MP_AVAILABLE = True
    mp_face_mesh = mp.solutions.face_mesh
except Exception:
    MP_AVAILABLE = False

class EnhancedWellnessWindow(QMainWindow):
    """Enhanced wellness window with integrated charts."""

    def __init__(self, user_id=1):
        super().__init__()
        self.user_id = user_id
        self.db_path = "user_data.db"
        self.current_section = "main"
        self.current_stats_period = "daily"

        self.setWindowTitle("Rest&Blink - Menu Główne")
        self.setGeometry(100, 100, 1600, 1000)


        self.setWindowTitle("Rest&Blink - Enhanced Wellness Dashboard")

        # Set responsive window size based on screen
        from PyQt5.QtWidgets import QDesktopWidget
        desktop = QDesktopWidget()
        screen_rect = desktop.screenGeometry()

        # Use 85% of screen width and 80% of screen height
        window_width = int(screen_rect.width() * 0.85)
        window_height = int(screen_rect.height() * 0.80)

        # Minimum and maximum sizes
        window_width = max(1200, min(2400, window_width))
        window_height = max(800, min(1600, window_height))

        self.setGeometry(100, 100, window_width, window_height)
        self.setMinimumSize(1000, 700)  # Minimum usable size

        # Apply dark wellness theme
        self.apply_wellness_theme()

        # Get user data
        self.user_data = self.get_user_data()

        # Setup UI
        self.setup_ui()

    def resizeEvent(self, event):
        """Handle window resize to update responsive layouts."""
        super().resizeEvent(event)
        # Rebuild achievements grid when window is resized
        if hasattr(self, 'achievements_layout') and self.current_section == "achievements":
            self.rebuild_achievements_grid()
        # Stats section now uses fixed layout - no rebuild needed

    def rebuild_achievements_grid(self):
        """Rebuild achievements grid with new column count."""
        # Clear existing grid
        while self.achievements_layout.count():
            child = self.achievements_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Recreate grid with new dimensions
        self.create_responsive_achievements_grid()

    def apply_wellness_theme(self):
        """Apply dark bio-hacking wellness theme."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1d1f;
                color: #e8e9ea;
            }
            
            QLabel {
                color: #e8e9ea;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QPushButton {
                background-color: #2c3034;
                border: 1px solid #404448;
                color: #e8e9ea;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #363940;
                border-color: #5a6269;
            }
            
            QPushButton:pressed {
                background-color: #404448;
            }
            
            QPushButton.active {
                background-color: #3d5a80;
                border-color: #5d7ca3;
                color: #ffffff;
            }
            
            QFrame {
                background-color: #262a2d;
                border: 1px solid #404448;
                border-radius: 10px;
            }
            
            QFrame.stats-card {
                background-color: #232629;
                border: 1px solid #3a3f44;
                border-radius: 12px;
                padding: 16px;
            }
            
            QScrollArea {
                background-color: #1a1d1f;
                border: none;
            }
            
            QScrollArea QWidget {
                background-color: #1a1d1f;
            }
        """)
    
    def get_user_data(self):
        """Get user data from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT first_name, last_name, level, total_points, total_sessions
                FROM Users WHERE id = ?
            """, (self.user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'first_name': result[0],
                    'last_name': result[1],
                    'level': result[2],
                    'total_points': result[3],
                    'total_sessions': result[4]
                }
            else:
                return {
                    'first_name': 'User',
                    'last_name': '',
                    'level': 1,
                    'total_points': 0,
                    'total_sessions': 0
                }
        except Exception as e:
            print(f"Error getting user data: {e}")
            return {
                'first_name': 'User',
                'last_name': '',
                'level': 1,
                'total_points': 0,
                'total_sessions': 0
            }
    
    def setup_ui(self):
        """Setup the main UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top header section
        self.create_header(main_layout)
        
        # Navigation section
        self.create_fixed_navigation(main_layout)
        
        # Separator line (20% from top)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #404448; border: none; height: 2px;")
        main_layout.addWidget(separator)
        
        # Content area
        self.create_content_area(main_layout)
    
    def create_header(self, parent_layout):
        """Create the top header with logo and user info."""
        header_widget = QWidget()
        header_widget.setFixedHeight(80)
        header_widget.setStyleSheet("background-color: #1a1d1f; border-bottom: 1px solid #404448;")
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(30, 20, 30, 20)
        
        # Left side - Logo
        logo_label = QLabel("Rest&Blink")
        logo_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        logo_label.setStyleSheet("color: #7cb9e8; border: none;")
        header_layout.addWidget(logo_label)
        
        # Left spacer to center the stats
        header_layout.addStretch(1)

        # Middle - Centered Quick stats cards
        quick_stats_widget = QWidget()
        quick_stats_layout = QHBoxLayout(quick_stats_widget)
        quick_stats_layout.setContentsMargins(0, 0, 0, 0)
        quick_stats_layout.setSpacing(15)

        # Today's sessions card
        today_card = self.create_quick_stat_card("Today's Sessions", "8", "#7cb9e8")
        current_streak_card = self.create_quick_stat_card("Current Streak", f"{self.user_data.get('level', 1)} days", "#90e0ef")
        total_time_card = self.create_quick_stat_card("Total Time", "12h 15m", "#a8dadc")

        quick_stats_layout.addWidget(today_card)
        quick_stats_layout.addWidget(current_streak_card)
        quick_stats_layout.addWidget(total_time_card)

        header_layout.addWidget(quick_stats_widget)

        # Right spacer to center the stats
        header_layout.addStretch(1)
        
        # Right side - User info
        user_info_widget = QWidget()
        user_info_layout = QVBoxLayout(user_info_widget)
        user_info_layout.setContentsMargins(0, 0, 0, 0)
        user_info_layout.setSpacing(2)
        
        # User greeting
        greeting = f"Hi, {self.user_data['first_name']} {self.user_data['last_name']}"
        user_label = QLabel(greeting)
        user_label.setFont(QFont("Segoe UI", 14, QFont.Medium))
        user_label.setStyleSheet("color: #e8e9ea; border: none;")
        user_label.setAlignment(Qt.AlignRight)
        
        # Level info
        level_label = QLabel(f"lv. {self.user_data['level']}")
        level_label.setFont(QFont("Segoe UI", 12))
        level_label.setStyleSheet("color: #a8b5c1; border: none;")
        level_label.setAlignment(Qt.AlignRight)
        
        user_info_layout.addWidget(user_label)
        user_info_layout.addWidget(level_label)
        
        header_layout.addWidget(user_info_widget)
        parent_layout.addWidget(header_widget)
    
    def create_fixed_navigation(self, parent_layout):
        """Create fixed navigation tiles that are always visible."""
        nav_widget = QWidget()
        nav_widget.setFixedHeight(70)
        nav_widget.setStyleSheet("background-color: #1a1d1f;")
        
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(30, 15, 30, 15)
        nav_layout.setSpacing(20)
        
        # Add spacer
        nav_layout.addStretch()

        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("main", "Main"),
            ("stats", "Stats"),
            ("configure", "Configure"),
            ("achievements", "Achievements")
        ]

        for nav_id, nav_text in nav_items:
            btn = QPushButton(nav_text)
            btn.setMinimumSize(120, 40)
            btn.clicked.connect(lambda checked, nav_id=nav_id: self.switch_section(nav_id))

            self.nav_buttons[nav_id] = btn
            nav_layout.addWidget(btn)
        
        # Add spacer
        nav_layout.addStretch()

        parent_layout.addWidget(nav_widget)

    def create_navigation_separator(self, parent_layout):
        """Create a separator line under navigation."""
        # Small spacing
        spacer_top = QWidget()
        spacer_top.setFixedHeight(10)
        spacer_top.setStyleSheet("background-color: #1a1d1f;")
        parent_layout.addWidget(spacer_top)

        # Separator line
        separator = QFrame()
        separator.setFixedHeight(2)
        separator.setStyleSheet("background-color: #404448; border: none;")
        parent_layout.addWidget(separator)

        # Small spacing after
        spacer_bottom = QWidget()
        spacer_bottom.setFixedHeight(10)
        spacer_bottom.setStyleSheet("background-color: #1a1d1f;")
        parent_layout.addWidget(spacer_bottom)

    def create_content_area(self, parent_layout):
        """Create the main content area."""
        self.content_stack = QStackedWidget()

        # Main page
        main_page = self.create_main_page()

        # Stats page
        stats_page = self.create_stats_page()

        # Configure page (placeholder)
        configure_page = self.create_config_page("Konfiguracja Kamery", "Panel umożliwiający konfigurację kamery. Prawidłowo skonfigurowana kamera umożliwa detekcję aktywności na wielu monitorach.")

        # Achievements page (placeholder)
        achievements_page = self.create_placeholder_page("Osiągnięcia", "Osiągnięcia")

        # Add pages to stack
        self.content_stack.addWidget(main_page)        # index 0
        self.content_stack.addWidget(stats_page)       # index 1
        self.content_stack.addWidget(configure_page)   # index 2
        self.content_stack.addWidget(achievements_page) # index 3

        parent_layout.addWidget(self.content_stack)

        # Start with stats section
        self.switch_section("stats")

    def create_config_page(self, title, description, cursor=None, conn=None):
        """
        Ekran konfiguracji kamery z zapisem pozycji oczu + orientacji głowy (yaw,pitch,roll)
        dla każdego monitora. Działa wewnątrz jednego taba (bez cv2.imshow()).
        """

        page = QWidget()
        page.setStyleSheet("background-color: #1a1d1f;")
        layout = QVBoxLayout(page)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 24))
        title_label.setStyleSheet("color: #e8e9ea; margin: 50px;")
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(QFont("Segoe UI", 14))
        desc_label.setStyleSheet("color: #a8b5c1; margin-bottom: 30px;")
        layout.addWidget(title_label)
        layout.addWidget(desc_label)

        camera_label = QLabel()
        camera_label.setAlignment(Qt.AlignCenter)
        camera_label.setFixedSize(640, 480)
        camera_label.setStyleSheet("border: 2px solid #2c3e50; border-radius: 10px; background: black;")
        layout.addWidget(camera_label, alignment=Qt.AlignCenter)

        status_label = QLabel("Kliknij przycisk, aby rozpocząć konfigurację kamery.")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet("color: #f0f0f0; font-size: 16px; margin: 1px;")
        layout.addWidget(status_label)

        eyes_list = QListWidget()
        eyes_list.setStyleSheet("color: #e8e9ea; background: #111214; border: 1px solid #2c3e50;")
        eyes_list.setFixedHeight(160)
        layout.addWidget(eyes_list)

        progress = QProgressBar()
        progress.setValue(0)
        progress.setStyleSheet(
            "QProgressBar{background:#2c3e50;color:white;border-radius:5px;}QProgressBar::chunk{background:#1abc9c;}")
        layout.addWidget(progress)

        calibrate_btn = QPushButton("Rozpocznij konfigurację kamery")
        calibrate_btn.setStyleSheet("background-color:#1abc9c;color:white;padding:10px;border-radius:5px;")
        layout.addWidget(calibrate_btn, alignment=Qt.AlignCenter)
        layout.addStretch()

        # stan i zmienne pomocnicze
        cap = {"obj": None}
        timer = QTimer()
        try:
            monitors = get_monitors()
        except Exception:
            logging.exception("get_monitors failed")
            monitors = []
        num_monitors = max(1, len(monitors))
        current_index = {"i": 0}
        timer_connected = {"v": False}
        calibration_active = {"v": False}

        calibration_templates = []

        # przygotowanie Haar fallback jeśli brak MediaPipe
        eye_cascade = None
        try:
            eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
            if eye_cascade.empty():
                eye_cascade = None
        except Exception:
            eye_cascade = None

        MP_AVAILABLE = False
        face_mesh = None
        try:
            import mediapipe as mp
            MP_AVAILABLE = True
            mp_face_mesh = mp.solutions.face_mesh
            face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1,
                                              refine_landmarks=True, min_detection_confidence=0.5,
                                              min_tracking_confidence=0.5)
        except Exception:
            MP_AVAILABLE = False
            face_mesh = None
            logging.info("MediaPipe FaceMesh not available; using Haar fallback if possible.")

        # --- helper: estymacja head pose ---
        def estimate_head_pose(landmarks, image_shape):
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
                pitch = np.degrees(x)
                yaw = np.degrees(y)
                roll = np.degrees(z)
                return True, (yaw, pitch, roll)
            except Exception:
                logging.exception("estimate_head_pose failed")
                return False, (0.0, 0.0, 0.0)

        # --- detekcja oczu ---
        def detect_eyes_in_frame(frame):
            try:
                h, w = frame.shape[:2]
                if MP_AVAILABLE and face_mesh is not None:
                    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = face_mesh.process(img_rgb)
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
                if eye_cascade is not None:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    eyes = eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))
                    eyes = sorted(eyes, key=lambda e: e[0])
                    if len(eyes) >= 2:
                        l = eyes[0]
                        r = eyes[1]
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

        # --- update_frame ---
        def update_frame():
            try:
                if cap["obj"] is None:
                    return
                ret, frame = cap["obj"].read()
                if not ret or frame is None:
                    return

                left, right, lm = detect_eyes_in_frame(frame)
                head = None
                if MP_AVAILABLE and lm is not None:
                    ok, head = estimate_head_pose(lm, frame.shape)
                    if ok:
                        camera_label._last_head = head
                    else:
                        camera_label._last_head = None
                else:
                    camera_label._last_head = None

                vis = frame.copy()
                if left:
                    cv2.circle(vis, left, 4, (0, 255, 0), -1)
                if right:
                    cv2.circle(vis, right, 4, (0, 255, 0), -1)
                if getattr(camera_label, "_last_head", None):
                    yv, pv, rv = camera_label._last_head
                    text = f"yaw:{yv:.1f} pitch:{pv:.1f}"
                    cv2.putText(vis, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 50), 2)

                frame_rgb = cv2.cvtColor(vis, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pix = QPixmap.fromImage(qimg).scaled(camera_label.width(), camera_label.height(),
                                                     Qt.KeepAspectRatio, Qt.SmoothTransformation)
                camera_label.setPixmap(pix)

                camera_label._last_left = left
                camera_label._last_right = right

            except Exception:
                logging.exception("Exception in update_frame")
                safe_release()
                status_label.setText("❌ Błąd przetwarzania kamery. Sprawdź logi.")
                calibrate_btn.setEnabled(True)
                calibration_active["v"] = False

        import datetime

        # --- record + zapis do bazy ---
        def record_current_monitor_and_continue():
            try:
                left = getattr(camera_label, "_last_left", None)
                right = getattr(camera_label, "_last_right", None)
                head = getattr(camera_label, "_last_head", None)
                mi = current_index['i'] + 1

                logging.info(f"Recorded monitor {mi}: left={left}, right={right}, head={head}")
                calibration_templates.append({"monitor": mi, "left": left, "right": right, "head": head})

                item_text = f"Ekran {mi}: head={head}, left={left}, right={right}"
                eyes_list.addItem(QListWidgetItem(item_text))
                status_label.setText(f"Zarejestrowano pozycję oczu dla ekranu {mi}.")

                # zapis do bazy danych
                if cursor is not None and conn is not None:
                    head_yaw, head_pitch, head_roll = head if head else (None, None, None)
                    left_x, left_y = left if left else (None, None)
                    right_x, right_y = right if right else (None, None)
                    created_at = datetime.datetime.now().isoformat(timespec='seconds')

                    cursor.execute('''
                        INSERT INTO calibration_templates 
                        (monitor, head_yaw, head_pitch, head_roll, left_x, left_y, right_x, right_y, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (mi, head_yaw, head_pitch, head_roll, left_x, left_y, right_x, right_y, created_at))
                    conn.commit()

            except Exception:
                logging.exception("Error saving eye data")
                status_label.setText("❌ Błąd zapisu pozycji oczu.")

            current_index['i'] += 1
            progress.setValue(int(current_index['i'] / num_monitors * 100))
            QTimer.singleShot(800, next_monitor_step)

        def next_monitor_step():
            try:
                total = num_monitors
                if current_index['i'] >= total:
                    safe_release()
                    status_label.setText("✅ Konfiguracja zakończona.")
                    progress.setValue(100)
                    calibrate_btn.setEnabled(True)
                    calibration_active['v'] = False
                    return
                mon = monitors[current_index['i']] if monitors else None
                if mon:
                    status_label.setText(
                        f"📺 Ekran {current_index['i'] + 1}/{total} — ({mon.width}x{mon.height}). Popatrz teraz.")
                else:
                    status_label.setText(f"Ekran {current_index['i'] + 1}/{total}. Popatrz teraz.")
                QTimer.singleShot(2000, record_current_monitor_and_continue)
            except Exception:
                logging.exception("next_monitor_step error")
                safe_release()
                status_label.setText("❌ Błąd w procesie konfiguracji.")
                calibrate_btn.setEnabled(True)
                calibration_active['v'] = False

        def start_calibration():
            if calibration_active['v']:
                return
            calibration_active['v'] = True
            calibrate_btn.setEnabled(False)
            current_index['i'] = 0
            progress.setValue(0)
            eyes_list.clear()
            calibration_templates.clear()
            status_label.setText("Inicjalizuję kamerę...")
            logging.info("Start calibration")
            try:
                cap["obj"] = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                if not (cap["obj"] and cap["obj"].isOpened()):
                    status_label.setText("❌ Nie udało się otworzyć kamery.")
                    logging.error("camera open failed")
                    cap["obj"] = None
                    calibrate_btn.setEnabled(True)
                    calibration_active['v'] = False
                    return
                if not timer_connected["v"]:
                    timer.timeout.connect(update_frame)
                    timer_connected["v"] = True
                timer.start(30)
                QTimer.singleShot(800, next_monitor_step)
            except Exception:
                logging.exception("start_calibration failed")
                status_label.setText("❌ Błąd inicjalizacji kamery.")
                safe_release()
                calibrate_btn.setEnabled(True)
                calibration_active['v'] = False

        def stop_calibration_clean():
            safe_release()
            status_label.setText("Kalibracja przerwana.")
            calibrate_btn.setEnabled(True)
            calibration_active['v'] = False

        def safe_release():
            try:
                if cap["obj"] is not None:
                    try:
                        cap["obj"].release()
                    except Exception:
                        logging.exception("release failed")
                    cap["obj"] = None
                if timer.isActive():
                    timer.stop()
                if timer_connected["v"]:
                    try:
                        timer.timeout.disconnect(update_frame)
                    except Exception:
                        pass
                    timer_connected["v"] = False
            except Exception:
                logging.exception("safe_release exception")
            try:
                if face_mesh is not None:
                    try:
                        face_mesh.close()
                    except Exception:
                        pass
            except Exception:
                pass

        calibrate_btn.clicked.connect(start_calibration)
        return page

    def create_main_page(self):
        """Create empty main page (content moved to header)."""
        main_page = QWidget()
        main_page.setStyleSheet("background-color: #1a1d1f;")
        main_layout = QVBoxLayout(main_page)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Empty main page - all content moved to header
        main_layout.addStretch()
        
        return main_page
    
    def create_placeholder_page(self, title, description):
        """Create a placeholder page."""
        page = QWidget()
        page.setStyleSheet("background-color: #1a1d1f;")
        layout = QVBoxLayout(page)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 24, QFont.Medium))
        title_label.setStyleSheet("color: #e8e9ea; margin: 50px;")
        
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(QFont("Segoe UI", 14))
        desc_label.setStyleSheet("color: #a8b5c1; margin-bottom: 100px;")
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addStretch()
        
        return page
    
    def create_quick_stat_card(self, title, value, color):
        """Create a quick stat card without borders."""
        card = QFrame()
        card.setFrameStyle(QFrame.NoFrame)  # Remove frame

        # Smaller, more reasonable size
        card.setFixedSize(180, 70)
        card.setMinimumSize(180, 70)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(2)
        
        # Title label - small and compact
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 9, QFont.Medium))
        title_label.setStyleSheet(f"color: {color}; background: transparent; margin: 0px; padding: 0px;")
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setMaximumHeight(18)
        
        # Value label - smaller to fit
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        value_label.setStyleSheet("color: #e8e9ea; background: transparent; margin: 0px; padding: 0px;")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setMinimumHeight(25)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()  # Push content to top
        
        return card
    
    def create_stats_page(self):
        """Create the stats page with period selection."""
        stats_page = QWidget()
        stats_page.setStyleSheet("background-color: #1a1d1f;")
        
        stats_layout = QVBoxLayout(stats_page)
        stats_layout.setContentsMargins(30, 20, 30, 20)
        stats_layout.setSpacing(20)
        
        # Stats header - wrapped in container for centering
        header_container = QWidget()
        header_container.setStyleSheet("border: none; background: transparent;")
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 10)

        # Add stretchers to center the header
        header_layout.addStretch()

        stats_header = QLabel("Stats: Health & Wellness Analytics")
        stats_header.setFont(QFont("Segoe UI", 20, QFont.Medium))
        stats_header.setStyleSheet("color: #e8e9ea; border: none; background: transparent;")
        header_layout.addWidget(stats_header)

        header_layout.addStretch()

        stats_layout.addWidget(header_container)
        
        # Period selection buttons
        period_widget = QWidget()
        period_layout = QHBoxLayout(period_widget)
        period_layout.setContentsMargins(0, 0, 0, 0)
        period_layout.setSpacing(15)
        
        self.period_buttons = {}
        periods = [
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("alltime", "All Time")
        ]
        
        for period_id, period_text in periods:
            btn = QPushButton(period_text)
            btn.setMinimumSize(120, 45)
            btn.clicked.connect(lambda checked, period_id=period_id: self.switch_stats_period(period_id))
            self.period_buttons[period_id] = btn
            period_layout.addWidget(btn)
        
        # Add stretch to left-align buttons
        period_layout.addStretch()
        
        stats_layout.addWidget(period_widget)
        
        # Stats content area
        self.stats_content_area = QWidget()
        self.stats_content_layout = QVBoxLayout(self.stats_content_area)
        self.stats_content_layout.setContentsMargins(0, 0, 0, 0)
        
        stats_layout.addWidget(self.stats_content_area)
        
        # Set initial period to daily
        self.switch_stats_period("daily")
        
        return stats_page
    
    def create_enhanced_period_content(self, period):
        """Create enhanced content with real charts for a specific period."""
        # Clear existing content
        for i in reversed(range(self.stats_content_layout.count())):
            child = self.stats_content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Get data for this period
        period_data = self.get_enhanced_period_data(period)
        
        # Create main dashboard
        dashboard_widget = QWidget()
        dashboard_layout = QGridLayout(dashboard_widget)
        dashboard_layout.setSpacing(20)
        dashboard_layout.setContentsMargins(0, 20, 0, 0)
        
        # Left side - Charts
        charts_widget = self.create_charts_widget(period_data, period)
        
        # Middle - Average stats
        avg_stats_widget = self.create_avg_stats_widget(period_data)
        
        # Right side - Time & Score
        right_stats_widget = self.create_right_stats_widget(period_data, period)
        
        # Simple fixed layout - no responsive changes
        dashboard_layout.addWidget(charts_widget, 0, 0, 2, 1)  # Charts on left, span 2 rows
        dashboard_layout.addWidget(avg_stats_widget, 0, 1, 1, 1)  # Top right
        dashboard_layout.addWidget(right_stats_widget, 1, 1, 1, 1)  # Bottom right
        
        # Set column stretch
        dashboard_layout.setColumnStretch(0, 3)  # Charts take more space
        dashboard_layout.setColumnStretch(1, 1)  # Right column
        
        self.stats_content_layout.addWidget(dashboard_widget)
        self.stats_content_layout.addStretch()
    
    def create_charts_widget(self, data, period):
        """Create the charts widget with real heartbeat and stress data."""
        charts_widget = QFrame()
        charts_widget.setProperty("class", "stats-card")
        charts_widget.setMinimumHeight(500)
        charts_layout = QVBoxLayout(charts_widget)
        charts_layout.setContentsMargins(20, 20, 20, 20)
        
        if data and len(data) > 0:
            # Create matplotlib figure
            fig = Figure(figsize=(8, 6), facecolor='#232629')
            
            # Heartbeat chart
            ax1 = fig.add_subplot(2, 1, 1)
            
            if 'heartbeat' in data[0]:
                timestamps = list(range(len(data)))
                heartbeats = [d['heartbeat'] for d in data]
                
                ax1.plot(timestamps, heartbeats, color='#7cb9e8', linewidth=2)
                ax1.set_title('Heartbeat', color='#e8e9ea', fontsize=14, pad=20)
                ax1.set_ylabel('BPM', color='#a8b5c1')
                ax1.tick_params(colors='#a8b5c1')
                ax1.grid(True, alpha=0.3, color='#404448')
                ax1.set_facecolor('#1a1d1f')
            
            # Stress chart
            ax2 = fig.add_subplot(2, 1, 2)
            
            if 'stress' in data[0]:
                stress_levels = [d['stress'] for d in data]
                
                ax2.plot(timestamps, stress_levels, color='#f4a261', linewidth=2)
                ax2.set_title('Stress Level', color='#e8e9ea', fontsize=14, pad=20)
                ax2.set_ylabel('Level', color='#a8b5c1')
                ax2.set_xlabel('Time', color='#a8b5c1')
                ax2.tick_params(colors='#a8b5c1')
                ax2.grid(True, alpha=0.3, color='#404448')
                ax2.set_facecolor('#1a1d1f')
            
            fig.tight_layout()
            
            # Create canvas and add to layout
            canvas = FigureCanvas(fig)
            canvas.setStyleSheet("background-color: #232629;")
            charts_layout.addWidget(canvas)
        
        else:
            # Placeholder for no data
            no_data_label = QLabel("No data available for this period")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("color: #a8b5c1; font-size: 16px; margin: 100px;")
            charts_layout.addWidget(no_data_label)
        
        return charts_widget
    
    def create_avg_stats_widget(self, data):
        """Create the average stats widget."""
        avg_stats_widget = QFrame()
        avg_stats_widget.setProperty("class", "stats-card")
        avg_stats_widget.setMaximumWidth(250)
        avg_stats_layout = QVBoxLayout(avg_stats_widget)
        avg_stats_layout.setContentsMargins(20, 20, 20, 20)
        avg_stats_layout.setSpacing(30)
        
        # Calculate averages from data
        if data and len(data) > 0:
            heartbeats = [d.get('heartbeat', 0) for d in data if d.get('heartbeat', 0) > 0]
            stress_levels = [d.get('stress', 0) for d in data if d.get('stress', 0) > 0]
            
            avg_heartbeat = sum(heartbeats) / len(heartbeats) if heartbeats else 0
            min_heartbeat = min(heartbeats) if heartbeats else 0
            max_heartbeat = max(heartbeats) if heartbeats else 0
            
            avg_stress = sum(stress_levels) / len(stress_levels) if stress_levels else 0
            min_stress = min(stress_levels) if stress_levels else 0
            max_stress = max(stress_levels) if stress_levels else 0
        else:
            avg_heartbeat = min_heartbeat = max_heartbeat = 0
            avg_stress = min_stress = max_stress = 0
        
        # Average heartbeat section
        avg_hb_widget = self.create_metric_widget(
            "Average Heartbeat", 
            f"{avg_heartbeat:.1f} BPM", 
            f"{min_heartbeat:.0f}/{max_heartbeat:.0f}",
            "#7cb9e8"
        )
        
        # Average stress section
        avg_stress_widget = self.create_metric_widget(
            "Average Stress",
            f"{avg_stress:.3f}",
            f"{min_stress:.2f}/{max_stress:.2f}",
            "#f4a261"
        )
        
        avg_stats_layout.addWidget(avg_hb_widget)
        avg_stats_layout.addWidget(avg_stress_widget)
        avg_stats_layout.addStretch()
        
        return avg_stats_widget
    
    def create_right_stats_widget(self, data, period):
        """Create the right stats widget with time and score."""
        right_stats_widget = QFrame()
        right_stats_widget.setProperty("class", "stats-card")
        right_stats_widget.setMaximumWidth(250)
        right_stats_layout = QVBoxLayout(right_stats_widget)
        right_stats_layout.setContentsMargins(20, 20, 20, 20)
        right_stats_layout.setSpacing(30)
        
        # Calculate totals from data
        total_time = sum([d.get('duration', 0) for d in data]) if data else 0
        total_score = sum([d.get('score', 0) for d in data]) if data else 0
        
        # Get period-specific data from database
        db_stats = self.get_period_stats(period)
        if db_stats:
            total_time = db_stats['total_time']
            total_score = db_stats['total_score']
        
        # Rest time section
        rest_minutes = total_time / 60
        rest_time_widget = self.create_metric_widget(
            "Rest in min",
            f"{rest_minutes:.0f} min",
            "",
            "#90e0ef"
        )
        
        # Score section
        period_names = {
            'daily': 'Today Score',
            'weekly': 'Weekly Score', 
            'monthly': 'Monthly Score',
            'alltime': 'All Time Score'
        }
        
        score_widget = self.create_metric_widget(
            period_names.get(period, 'Score'),
            f"{total_score:.0f}",
            "",
            "#a8dadc"
        )
        
        # Improve note
        improve_note = QLabel("Improve note")
        improve_note.setFont(QFont("Segoe UI", 12))
        improve_note.setStyleSheet("color: #a8b5c1;")
        improve_note.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        
        right_stats_layout.addWidget(rest_time_widget)
        right_stats_layout.addWidget(score_widget)
        right_stats_layout.addStretch()
        right_stats_layout.addWidget(improve_note)
        
        return right_stats_widget
    
    def create_metric_widget(self, title, value, range_text, color):
        """Create a metric widget with title, value, and optional range."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Medium))
        title_label.setStyleSheet(f"color: {color};")
        
        # Value
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        value_label.setStyleSheet("color: #e8e9ea;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()
        
        # Range (if provided)
        if range_text:
            range_label = QLabel(range_text)
            range_label.setFont(QFont("Segoe UI", 12))
            range_label.setStyleSheet("color: #a8b5c1;")
            range_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
            layout.addWidget(range_label)
        
        return widget
    
    def get_enhanced_period_data(self, period):
        """Get enhanced data for charts."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Define date ranges
            today = datetime.now()
            
            if period == "daily":
                start_date = today.strftime('%Y-%m-%d')
                end_date = start_date
            elif period == "weekly":
                start_of_week = today - timedelta(days=today.weekday())
                start_date = start_of_week.strftime('%Y-%m-%d')
                end_date = (start_of_week + timedelta(days=6)).strftime('%Y-%m-%d')
            elif period == "monthly":
                start_date = today.replace(day=1).strftime('%Y-%m-%d')
                end_date = today.strftime('%Y-%m-%d')
            else:  # alltime
                start_date = "2000-01-01"
                end_date = today.strftime('%Y-%m-%d')
            
            # Get sessions with heartbeat data
            cursor.execute("""
                SELECT heartbeat_data, total_time_seconds, score, timestamp
                FROM Sessions 
                WHERE user_id = ? AND DATE(timestamp) BETWEEN ? AND ?
                AND heartbeat_data IS NOT NULL AND heartbeat_data != ''
                ORDER BY timestamp
            """, (self.user_id, start_date, end_date))
            
            sessions = cursor.fetchall()
            conn.close()
            
            if not sessions:
                return []
            
            chart_data = []
            
            for session in sessions[:20]:  # Limit to first 20 sessions for performance
                try:
                    heartbeat_json = json.loads(session[0])
                    heartbeats = heartbeat_json.get('heartbeats', [])
                    stress_levels = heartbeat_json.get('stress_levels', [])
                    
                    if heartbeats and stress_levels:
                        # Take average values for this session
                        avg_heartbeat = sum(heartbeats) / len(heartbeats)
                        avg_stress = sum(stress_levels) / len(stress_levels)
                        
                        chart_data.append({
                            'heartbeat': avg_heartbeat,
                            'stress': avg_stress,
                            'duration': session[1],
                            'score': session[2],
                            'timestamp': session[3]
                        })
                        
                except (json.JSONDecodeError, TypeError):
                    continue
            
            return chart_data
            
        except Exception as e:
            print(f"Error getting enhanced period data: {e}")
            return []
    
    def get_period_stats(self, period):
        """Get basic statistics for a period."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Define date ranges
            today = datetime.now()
            
            if period == "daily":
                start_date = today.strftime('%Y-%m-%d')
                end_date = start_date
            elif period == "weekly":
                start_of_week = today - timedelta(days=today.weekday())
                start_date = start_of_week.strftime('%Y-%m-%d')
                end_date = (start_of_week + timedelta(days=6)).strftime('%Y-%m-%d')
            elif period == "monthly":
                start_date = today.replace(day=1).strftime('%Y-%m-%d')
                end_date = today.strftime('%Y-%m-%d')
            else:  # alltime
                start_date = "2000-01-01"
                end_date = today.strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT SUM(total_time_seconds), SUM(score), COUNT(*)
                FROM Sessions 
                WHERE user_id = ? AND DATE(timestamp) BETWEEN ? AND ?
            """, (self.user_id, start_date, end_date))
            
            result = cursor.fetchone()
            conn.close()
            
            return {
                'total_time': result[0] or 0,
                'total_score': result[1] or 0,
                'total_sessions': result[2] or 0
            }
            
        except Exception as e:
            print(f"Error getting period stats: {e}")
            return {'total_time': 0, 'total_score': 0, 'total_sessions': 0}
    
    def switch_section(self, section):
        """Switch between main sections."""
        self.current_section = section
        
        # Update button styles
        for nav_id, btn in self.nav_buttons.items():
            if nav_id == section:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3d5a80;
                        border-color: #5d7ca3;
                        color: #ffffff;
                        padding: 12px 24px;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: 500;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2c3034;
                        border: 1px solid #404448;
                        color: #e8e9ea;
                        padding: 12px 24px;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background-color: #363940;
                        border-color: #5a6269;
                    }
                """)
        
        # Switch content
        section_map = {
            "main": 0,
            "stats": 1,
            "configure": 2,
            "achievements": 3
        }
        
        if section in section_map:
            self.content_stack.setCurrentIndex(section_map[section])
    
    def switch_stats_period(self, period):
        """Switch between stats periods."""
        self.current_stats_period = period
        
        # Update button styles
        for period_id, btn in self.period_buttons.items():
            if period_id == period:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3d5a80;
                        border-color: #5d7ca3;
                        color: #ffffff;
                        padding: 12px 24px;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: 500;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2c3034;
                        border: 1px solid #404448;
                        color: #e8e9ea;
                        padding: 12px 24px;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background-color: #363940;
                        border-color: #5a6269;
                    }
                """)
        
        # Update content for the new period
        self.create_enhanced_period_content(period)


# Test the enhanced interface
def main():
    """Test the enhanced wellness interface."""
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    window = EnhancedWellnessWindow()
    window.show()
    
    # Start with stats section
    window.switch_section("stats")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()