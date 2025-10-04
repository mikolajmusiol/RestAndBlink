# ui/main_window.py (Zmodyfikowany)

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt, pyqtSignal  # Dodaj import pyqtSignal


class SettingsStatsWindow(QMainWindow):
    """
    Główne okno aplikacji do wyświetlania ustawień i statystyk gamifikacji.
    """
    # Nowe sygnały emitowane przy otwieraniu/zamykaniu okna
    window_opened_signal = pyqtSignal()
    window_closed_signal = pyqtSignal()

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

    def showEvent(self, event):
        """Emituje sygnał po otwarciu okna (pokazaniu)."""
        super().showEvent(event)
        self.window_opened_signal.emit()  # INFORMUJEMY: Okno się Otworzyło

    def closeEvent(self, event):
        """Ukrywa okno i emituje sygnał zamknięcia."""
        self.hide()
        event.ignore()
        self.window_closed_signal.emit()  # INFORMUJEMY: Okno się Zamknęło