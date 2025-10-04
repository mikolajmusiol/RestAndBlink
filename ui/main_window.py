import os

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt, pyqtSignal  # Dodaj import pyqtSignal
from PyQt5.QtGui import QIcon # NOWY IMPORT


class SettingsStatsWindow(QMainWindow):
    """
    Główne okno aplikacji do wyświetlania ustawień i statystyk gamifikacji.
    """
    # Nowe sygnały emitowane przy otwieraniu/zamykaniu okna
    window_opened_signal = pyqtSignal()
    window_closed_signal = pyqtSignal()

    def __init__(self, icon_path):
        super().__init__()
        self.setWindowTitle("Break Reminder")
        self.setGeometry(300, 300, 400, 300)

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        title = QLabel("Witaj w aplikacji Break Reminder!")
        title.setAlignment(Qt.AlignCenter)
        description = QLabel("Tutaj znajdą się Twoje punkty, osiągnięcia i ustawienia przerw.")

        layout.addWidget(title)
        layout.addWidget(description)

    def showEvent(self, event):
        """Emituje sygnał po otwarciu okna (pokazaniu)."""
        super().showEvent(event)
        self.window_opened_signal.emit()  # INFORMUJEMY: Okno się Otworzyło

    def closeEvent(self, event):
        """Ukrywa okno i emituje sygnał zamknięcia."""
        self.hide()
        event.ignore()
        self.window_closed_signal.emit()  # INFORMUJEMY: Okno się Zamknęło