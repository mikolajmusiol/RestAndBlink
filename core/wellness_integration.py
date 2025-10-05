# core/wellness_integration.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from core.application_controller import ApplicationController


class MainTimerWidget(QWidget):
    """Widget integrujący funkcjonalność timera z main_old.py do karty Main w Enhanced Wellness Window."""
    
    # Sygnały do komunikacji z kontrolerem aplikacji
    start_timer_signal = pyqtSignal()
    stop_timer_signal = pyqtSignal()
    pause_timer_signal = pyqtSignal()
    resume_timer_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.application_controller = None
        self.is_timer_running = False
        self.is_timer_paused = False
        self.work_time_minutes = 25  # Domyślnie 25 minut pracy
        self.break_time_minutes = 5  # Domyślnie 5 minut przerwy
        
        self.setup_ui()
    
    def setup_ui(self):
        """Konfiguruje interfejs użytkownika dla karty Main."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Tytuł sekcji
        title = QLabel("System Monitorowania Pracy")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setStyleSheet("""
            color: #e8e9ea;
            margin-bottom: 20px;
        """)
        layout.addWidget(title)
        
        # Status timera
        self.status_label = QLabel("Timer zatrzymany")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 18, QFont.Medium))
        self.status_label.setStyleSheet("""
            color: #a8b5c1;
            background-color: #2c3034;
            padding: 20px;
            border-radius: 12px;
            margin: 10px;
        """)
        layout.addWidget(self.status_label)
        
        # Informacje o kamerze i monitorowaniu wzroku
        self.camera_status_label = QLabel("Status kamery: Sprawdzanie...")
        self.camera_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_status_label.setFont(QFont("Segoe UI", 14))
        self.camera_status_label.setStyleSheet("""
            color: #ffd700;
            background-color: #2c2c1a;
            padding: 15px;
            border-radius: 8px;
            margin: 5px;
        """)
        layout.addWidget(self.camera_status_label)
        
        # Panel kontroli timera
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                background-color: #25282b;
                border-radius: 16px;
                padding: 20px;
            }
        """)
        control_layout = QVBoxLayout(control_frame)
        control_layout.setSpacing(20)
        
        # Przyciski sterowania
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.start_button = QPushButton("▶ Rozpocznij sesję pracy")
        self.pause_button = QPushButton("⏸ Zatrzymaj")
        self.stop_button = QPushButton("⏹ Zakończ")
        
        # Stylizacja przycisków
        button_style = """
            QPushButton {
                background-color: #3d5a80;
                border: 2px solid #5d7ca3;
                color: #ffffff;
                padding: 15px 25px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #4a6b94;
                border-color: #6d8cb3;
            }
            QPushButton:pressed {
                background-color: #2f4a6b;
            }
            QPushButton:disabled {
                background-color: #404448;
                border-color: #5a6269;
                color: #8a9199;
            }
        """
        
        self.start_button.setStyleSheet(button_style)
        self.pause_button.setStyleSheet(button_style.replace("#3d5a80", "#d4860a").replace("#5d7ca3", "#f4a00a"))
        self.stop_button.setStyleSheet(button_style.replace("#3d5a80", "#c73e1d").replace("#5d7ca3", "#e74c3c"))
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.stop_button)
        
        control_layout.addLayout(button_layout)
        
        # Informacje o ustawieniach
        settings_info_label = QLabel(f"Czas pracy: {self.work_time_minutes} min | Czas przerwy: {self.break_time_minutes} min")
        settings_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_info_label.setFont(QFont("Segoe UI", 12))
        settings_info_label.setStyleSheet("color: #a8b5c1; margin-top: 10px;")
        control_layout.addWidget(settings_info_label)
        
        layout.addWidget(control_frame)
        
        # Informacje o funkcjonalności
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #1e3a24;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        info_title = QLabel("Funkcje systemu:")
        info_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        info_title.setStyleSheet("color: #4ade80; margin-bottom: 10px;")
        info_layout.addWidget(info_title)
        
        features = [
            "• Automatyczne przypomnienia o przerwach co 25 minut",
            "• Monitorowanie wzroku w czasie rzeczywistym (jeśli kamera dostępna)",
            "• Inteligentne pauzowanie timerów podczas odwracania wzroku",
            "• Śledzenie statystyk pracy i przerw",
            "• Ikonka w zasobniku systemowym dla łatwego dostępu"
        ]
        
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setFont(QFont("Segoe UI", 12))
            feature_label.setStyleSheet("color: #a8b5c1; margin: 2px 0;")
            info_layout.addWidget(feature_label)
        
        layout.addWidget(info_frame)
        
        # Połączenie sygnałów
        self.connect_signals()
        
        # Początkowy stan przycisków
        self.update_button_states()
    
    def connect_signals(self):
        """Łączy sygnały z przyciskami."""
        self.start_button.clicked.connect(self.start_timer)
        self.pause_button.clicked.connect(self.toggle_pause_timer)
        self.stop_button.clicked.connect(self.stop_timer)
    
    def set_application_controller(self, controller):
        """Ustawia referencję do kontrolera aplikacji."""
        self.application_controller = controller
        if controller:
            # Sprawdź status kamery
            if controller.eye_monitor_worker:
                self.camera_status_label.setText("Status kamery: ✓ Aktywna - Monitorowanie wzroku włączone")
                self.camera_status_label.setStyleSheet("""
                    color: #4ade80;
                    background-color: #1e3a24;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 5px;
                """)
            else:
                self.camera_status_label.setText("Status kamery: ✗ Niedostępna - Tylko timer będzie aktywny")
                self.camera_status_label.setStyleSheet("""
                    color: #f87171;
                    background-color: #3a1e1e;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 5px;
                """)
    
    def start_timer(self):
        """Rozpoczyna sesję pracy."""
        if self.application_controller:
            self.is_timer_running = True
            self.is_timer_paused = False
            self.application_controller.resume_main_timer()
            self.status_label.setText("Timer aktywny - Sesja pracy w toku")
            self.status_label.setStyleSheet("""
                color: #4ade80;
                background-color: #1e3a24;
                padding: 20px;
                border-radius: 12px;
                margin: 10px;
            """)
            self.update_button_states()
            print("Sesja pracy rozpoczęta!")
    
    def toggle_pause_timer(self):
        """Pauzuje/wznawia timer."""
        if not self.application_controller:
            return
            
        if not self.is_timer_paused:
            self.application_controller.pause_main_timer()
            self.is_timer_paused = True
            self.pause_button.setText("▶ Wznów")
            self.status_label.setText("Timer wstrzymany")
            self.status_label.setStyleSheet("""
                color: #ffd700;
                background-color: #2c2c1a;
                padding: 20px;
                border-radius: 12px;
                margin: 10px;
            """)
            print("Timer wstrzymany.")
        else:
            self.application_controller.resume_main_timer()
            self.is_timer_paused = False
            self.pause_button.setText("⏸ Zatrzymaj")
            self.status_label.setText("Timer aktywny - Sesja pracy w toku")
            self.status_label.setStyleSheet("""
                color: #4ade80;
                background-color: #1e3a24;
                padding: 20px;
                border-radius: 12px;
                margin: 10px;
            """)
            print("Timer wznowiony.")
    
    def stop_timer(self):
        """Zatrzymuje sesję pracy."""
        if self.application_controller:
            self.application_controller.pause_main_timer()
            self.is_timer_running = False
            self.is_timer_paused = False
            self.pause_button.setText("⏸ Zatrzymaj")
            self.status_label.setText("Timer zatrzymany")
            self.status_label.setStyleSheet("""
                color: #a8b5c1;
                background-color: #2c3034;
                padding: 20px;
                border-radius: 12px;
                margin: 10px;
            """)
            self.update_button_states()
            print("Sesja pracy zakończona.")
    
    def update_button_states(self):
        """Aktualizuje stan przycisków w zależności od stanu timera."""
        self.start_button.setEnabled(not self.is_timer_running)
        self.pause_button.setEnabled(self.is_timer_running)
        self.stop_button.setEnabled(self.is_timer_running)