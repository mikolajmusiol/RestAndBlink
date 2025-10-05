# ui/components/camera_calibration.py
"""Camera calibration components for wellness monitoring."""

import logging
import cv2
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QListWidget, QListWidgetItem, QProgressBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap

try:
    import mediapipe as mp
    MP_AVAILABLE = True
except ImportError:
    MP_AVAILABLE = False
    mp = None

try:
    from screeninfo import get_monitors
except ImportError:
    get_monitors = None


class CameraCalibration:
    """Handles camera calibration for eye tracking."""
    
    def __init__(self, ui_scaling, database_manager):
        self.ui_scaling = ui_scaling
        self.database_manager = database_manager
        self.setup_face_detection()
        
    def setup_face_detection(self):
        """Initialize face detection components."""
        self.face_mesh = None
        self.eye_cascade = None
        
        # Initialize MediaPipe if available
        if MP_AVAILABLE and mp is not None:
            try:
                mp_face_mesh = mp.solutions.face_mesh
                self.face_mesh = mp_face_mesh.FaceMesh(
                    static_image_mode=False, 
                    max_num_faces=1,
                    refine_landmarks=True, 
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
            except Exception as e:
                logging.error(f"Failed to initialize MediaPipe: {e}")
                self.face_mesh = None
        
        # Initialize Haar cascade fallback
        try:
            cascade_path = cv2.data.haarcascades + "haarcascade_eye.xml"
            self.eye_cascade = cv2.CascadeClassifier(cascade_path)
            if self.eye_cascade.empty():
                self.eye_cascade = None
        except Exception as e:
            logging.error(f"Failed to initialize Haar cascade: {e}")
            self.eye_cascade = None
    
    def create_calibration_page(self, title, description):
        """Create camera calibration page."""
        page = QWidget()
        page.setStyleSheet("background-color: #1a1d1f;")
        layout = QVBoxLayout(page)

        # Title and description
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(self.ui_scaling.scaled_font("Segoe UI", 24))
        title_label.setStyleSheet(f"color: #e8e9ea; margin: {self.ui_scaling.scaled_size(50)}px;")
        
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setFont(self.ui_scaling.scaled_font("Segoe UI", 14))
        desc_label.setStyleSheet("color: #a8b5c1; margin-bottom: 30px;")
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)

        # Camera preview
        camera_label = QLabel()
        camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        camera_label.setFixedSize(self.ui_scaling.scaled_size(640), self.ui_scaling.scaled_size(480))
        camera_label.setStyleSheet("border: 2px solid #2c3e50; border-radius: 10px; background: black;")
        layout.addWidget(camera_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Status label
        status_label = QLabel("Click the button to start camera calibration.")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet("color: #f0f0f0; font-size: 16px; margin: 1px;")
        layout.addWidget(status_label)

        # Eyes list
        eyes_list = QListWidget()
        eyes_list.setStyleSheet("color: #e8e9ea; background: #111214; border: 1px solid #2c3e50;")
        eyes_list.setFixedHeight(self.ui_scaling.scaled_size(160))
        layout.addWidget(eyes_list)

        # Progress bar
        progress = QProgressBar()
        progress.setValue(0)
        progress.setStyleSheet(
            "QProgressBar{background:#2c3e50;color:white;border-radius:5px;}"
            "QProgressBar::chunk{background:#1abc9c;}"
        )
        layout.addWidget(progress)

        # Calibrate button
        calibrate_btn = QPushButton("Start Camera Calibration")
        calibrate_btn.setStyleSheet("background-color:#1abc9c;color:white;padding:10px;border-radius:5px;")
        layout.addWidget(calibrate_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        # Setup calibration logic
        self.setup_calibration_logic(camera_label, status_label, eyes_list, progress, calibrate_btn)

        return page
    
    def setup_calibration_logic(self, camera_label, status_label, eyes_list, progress, calibrate_btn):
        """Setup the calibration logic."""
        # State variables
        self.cap = None
        timer = QTimer()
        current_index = {"i": 0}
        timer_connected = {"v": False}
        calibration_active = {"v": False}
        calibration_templates = []
        
        # Get monitor information
        try:
            monitors = get_monitors() if get_monitors else []
        except Exception:
            logging.exception("get_monitors failed")
            monitors = []
        num_monitors = max(1, len(monitors))

        def estimate_head_pose(landmarks, image_shape):
            """Estimate head pose from facial landmarks."""
            try:
                h, w = image_shape[0], image_shape[1]
                idx_map = {
                    "nose": 1, "l_eye": 33, "r_eye": 263, 
                    "l_mouth": 61, "r_mouth": 291, "chin": 199
                }
                
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
                camera_matrix = np.array([
                    [focal_length, 0, center[0]],
                    [0, focal_length, center[1]],
                    [0, 0, 1]
                ], dtype=np.float64)
                dist_coeffs = np.zeros((4, 1))

                success, rotation_vector, translation_vector = cv2.solvePnP(
                    model_points, image_points, camera_matrix, dist_coeffs, 
                    flags=cv2.SOLVEPNP_ITERATIVE
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

        def detect_eyes_in_frame(frame):
            """Detect eyes in the current frame."""
            try:
                h, w = frame.shape[:2]
                
                if MP_AVAILABLE and self.face_mesh is not None:
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
                
                if self.eye_cascade is not None:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    eyes = self.eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))
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

        def update_frame():
            """Update camera frame."""
            try:
                if self.cap is None:
                    return
                    
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    return

                left, right, lm = detect_eyes_in_frame(frame)
                head = None
                
                if MP_AVAILABLE and lm is not None:
                    ok, head = estimate_head_pose(lm, frame.shape)
                    if ok:
                        setattr(camera_label, "_last_head", head)
                    else:
                        setattr(camera_label, "_last_head", None)
                else:
                    setattr(camera_label, "_last_head", None)

                vis = frame.copy()
                if left:
                    cv2.circle(vis, left, 4, (0, 255, 0), -1)
                if right:
                    cv2.circle(vis, right, 4, (0, 255, 0), -1)
                    
                head_data = getattr(camera_label, "_last_head", None)
                if head_data:
                    yv, pv, rv = head_data
                    text = f"yaw:{yv:.1f} pitch:{pv:.1f}"
                    cv2.putText(vis, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 50), 2)

                frame_rgb = cv2.cvtColor(vis, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pix = QPixmap.fromImage(qimg).scaled(
                    camera_label.width(), camera_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                )
                camera_label.setPixmap(pix)

                setattr(camera_label, "_last_left", left)
                setattr(camera_label, "_last_right", right)

            except Exception:
                logging.exception("Exception in update_frame")
                safe_release()
                status_label.setText("❌ Camera processing error. Check logs.")
                calibrate_btn.setEnabled(True)
                calibration_active["v"] = False

        def record_current_monitor_and_continue():
            """Record current monitor calibration data."""
            try:
                left = getattr(camera_label, "_last_left", None)
                right = getattr(camera_label, "_last_right", None)
                head = getattr(camera_label, "_last_head", None)
                mi = current_index['i'] + 1

                logging.info(f"Recorded monitor {mi}: left={left}, right={right}, head={head}")
                calibration_templates.append({
                    "monitor": mi, 
                    "left": left, 
                    "right": right, 
                    "head": head
                })

                item_text = f"Screen {mi}: head={head}, left={left}, right={right}"
                eyes_list.addItem(QListWidgetItem(item_text))
                status_label.setText(f"Eye position recorded for screen {mi}.")

                # Save to database
                self.database_manager.save_calibration_data(mi, head, left, right)

            except Exception:
                logging.exception("Error saving eye data")
                status_label.setText("❌ Error saving eye position.")

            current_index['i'] += 1
            progress.setValue(int(current_index['i'] / num_monitors * 100))
            QTimer.singleShot(800, next_monitor_step)

        def next_monitor_step():
            """Move to next monitor in calibration."""
            try:
                total = num_monitors
                if current_index['i'] >= total:
                    safe_release()
                    status_label.setText("✅ Calibration completed.")
                    progress.setValue(100)
                    calibrate_btn.setEnabled(True)
                    calibration_active['v'] = False
                    return
                    
                mon = monitors[current_index['i']] if monitors and current_index['i'] < len(monitors) else None
                if mon:
                    status_label.setText(
                        f"📺 Screen {current_index['i'] + 1}/{total} — ({mon.width}x{mon.height}). Look now."
                    )
                else:
                    status_label.setText(f"Screen {current_index['i'] + 1}/{total}. Look now.")
                    
                QTimer.singleShot(2000, record_current_monitor_and_continue)
                
            except Exception:
                logging.exception("next_monitor_step error")
                safe_release()
                status_label.setText("❌ Calibration process error.")
                calibrate_btn.setEnabled(True)
                calibration_active['v'] = False

        def start_calibration():
            """Start the calibration process."""
            if calibration_active['v']:
                return
                
            calibration_active['v'] = True
            calibrate_btn.setEnabled(False)
            current_index['i'] = 0
            progress.setValue(0)
            eyes_list.clear()
            calibration_templates.clear()
            status_label.setText("Initializing camera...")
            logging.info("Start calibration")
            
            try:
                self.cap = cv2.VideoCapture(0)
                if not (self.cap and self.cap.isOpened()):
                    status_label.setText("❌ Failed to open camera.")
                    logging.error("camera open failed")
                    self.cap = None
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
                status_label.setText("❌ Camera initialization error.")
                safe_release()
                calibrate_btn.setEnabled(True)
                calibration_active['v'] = False

        def safe_release():
            """Safely release camera resources."""
            try:
                if self.cap is not None:
                    try:
                        self.cap.release()
                    except Exception:
                        logging.exception("release failed")
                    self.cap = None
                    
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
                if self.face_mesh is not None:
                    try:
                        self.face_mesh.close()
                    except Exception:
                        pass
            except Exception:
                pass

        calibrate_btn.clicked.connect(start_calibration)