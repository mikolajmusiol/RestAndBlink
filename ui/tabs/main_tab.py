# ui/tabs/main_timer_tab.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import pyqtSignal, Qt


class MainTab(QWidget):
    """Zakładka główna do kontroli Timera i podstawowych ustawień."""

    # Sygnały do komunikacji z ApplicationController
    start_timer_request = pyqtSignal()
    stop_timer_request = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(self._setup_layout())

    def _setup_layout(self):
        main_layout = QVBoxLayout()

        # Sekcja wyświetlania statusu/czasu
        status_label = QLabel("STATUS: Czas na pracę")
        status_label.setAlignment(Qt.AlignCenter)
        self.current_time_label = QLabel("00:00:00")
        self.current_time_label.setAlignment(Qt.AlignCenter)
        self.current_time_label.setStyleSheet("font-size: 32px; font-weight: bold;")

        main_layout.addWidget(status_label)
        main_layout.addWidget(self.current_time_label)
        main_layout.addSpacing(20)

        # Sekcja kontroli (Start/Stop)
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("START PRACY")
        self.stop_button = QPushButton("PAUZA")

        self.start_button.clicked.connect(lambda: self.start_timer_request.emit())
        self.stop_button.clicked.connect(lambda: self.stop_timer_request.emit())

        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        main_layout.addLayout(control_layout)

        main_layout.addStretch(1)

        return main_layout

    # Metoda do aktualizacji wyświetlanego czasu (będzie wywoływana z Timera)
    def update_display(self, time_str):
        self.current_time_label.setText(time_str)