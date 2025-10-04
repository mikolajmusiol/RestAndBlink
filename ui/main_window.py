# ui/main_window.py

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt


class SettingsStatsWindow(QMainWindow):
    """
    Główne okno aplikacji do wyświetlania ustawień i statystyk gamifikacji.
    Docelowo będzie zawierać logikę do konfiguracji i wyświetlania punktów.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Break Reminder - Statystyki i Ustawienia")
        self.setGeometry(300, 300, 400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        title = QLabel("Witaj w aplikacji Break Reminder!")
        title.setAlignment(Qt.AlignCenter)
        description = QLabel("Tutaj znajdą się Twoje punkty, osiągnięcia i ustawienia przerw.")

        layout.addWidget(title)
        layout.addWidget(description)

    def closeEvent(self, event):
        """
        Ukrywa okno zamiast je zamykać, aby aplikacja działała w tle (w zasobniku).
        """
        self.hide()
        event.ignore()