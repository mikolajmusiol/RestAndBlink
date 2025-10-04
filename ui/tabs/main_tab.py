# ui/tabs/main_timer_tab.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import pyqtSignal, Qt, QTimer, QUrl
from PyQt5.QtGui import QMovie
import os

class MainTab(QWidget):
    """Zakładka główna z automatycznym timerem i animowanym GIF-em."""

    timer_finished = pyqtSignal() # Sygnał, gdy timer skończy odliczanie

    def __init__(self, parent=None):
        super().__init__(parent)
        self.total_time_seconds = 5 * 60  # 5 minut w sekundach
        self.current_seconds_left = self.total_time_seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_countdown)

        self.setLayout(self._setup_layout())
        self._setup_gif_player() # Zmieniona nazwa metody

        # Automatyczne uruchomienie timera i GIF-a po inicjalizacji
        self._start_initial_countdown()
        self.gif_movie.start() # Start animacji GIF-a

    def _setup_layout(self):
        main_layout = QHBoxLayout() # Główny layout poziomy

        # --- Lewa sekcja: Timer ---
        timer_section_layout = QVBoxLayout()
        timer_section_layout.setAlignment(Qt.AlignCenter) # Wyśrodkowanie elementów timera

        status_label = QLabel("CZAS DO KOŃCA PRACY")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #555;") # Styl dla etykiety statusu

        self.current_time_label = QLabel("05:00") # Początkowy czas
        self.current_time_label.setAlignment(Qt.AlignCenter)
        self.current_time_label.setStyleSheet("font-size: 60px; font-weight: bold; color: #333;") # Większa czcionka

        timer_section_layout.addStretch(1) # Wypchnij do środka
        timer_section_layout.addWidget(status_label)
        timer_section_layout.addWidget(self.current_time_label)
        timer_section_layout.addStretch(1) # Wypchnij do środka

        main_layout.addLayout(timer_section_layout, 1) # 1/3 szerokości dla timera

        # --- Prawa sekcja: Odtwarzacz GIF ---
        gif_section_layout = QVBoxLayout() # Zmieniona nazwa zmiennej
        gif_section_layout.setAlignment(Qt.AlignCenter)

        gif_label_title = QLabel("ANIMACJA GIF") # Możesz usunąć tę etykietę, jeśli nie chcesz jej
        gif_label_title.setAlignment(Qt.AlignCenter)
        gif_label_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #555;")

        # Używamy QLabel do wyświetlania animowanego GIF-a
        self.gif_display_label = QLabel()
        self.gif_display_label.setAlignment(Qt.AlignCenter)
        self.gif_display_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gif_display_label.setMinimumSize(400, 300)
        self.gif_display_label.setStyleSheet("background-color: black;") # Opcjonalne tło

        gif_section_layout.addWidget(gif_label_title) # Możesz usunąć tę linię, jeśli nie chcesz etykiety
        gif_section_layout.addWidget(self.gif_display_label)
        gif_section_layout.addStretch(1) # Rozciągnij, aby GIF zajął dostępną przestrzeń

        main_layout.addLayout(gif_section_layout, 3) # 2/3 szerokości dla GIF-a

        return main_layout

    def _setup_gif_player(self): # Zmieniona nazwa metody
        # movies_folder = "resources" # Ścieżka do folderu z GIF-em
        gif_file = os.path.join("resources","movies","Zakrywanie powiek dłońmi.gif") # ZMIEŃ NA NAZWĘ SWOJEGO PLIKU GIF!

        self.gif_movie = QMovie(gif_file)

        if not self.gif_movie.isValid():
            print(f"Błąd: Plik GIF '{gif_file}' nie jest prawidłowym plikiem GIF lub nie został znaleziony.")
            print("Upewnij się, że masz plik GIF w folderze 'resources/movies' i zmieniono jego nazwę w kodzie.")
            # Wyświetl pusty obraz lub komunikat o błędzie, jeśli GIF jest nieprawidłowy
            self.gif_display_label.setText("BŁĄD: Nie znaleziono GIF-a lub jest uszkodzony.")
            self.gif_display_label.setStyleSheet("background-color: darkred; color: white; font-size: 16px;")
        else:
            self.gif_display_label.setMovie(self.gif_movie)
            self.gif_movie.setCacheMode(QMovie.CacheAll) # Buforowanie wszystkich klatek dla płynności
            self.gif_movie.setSpeed(100) # 100% prędkości (normalna). Możesz dostosować
            # self.gif_movie.start() # Zostanie uruchomione w __init__

    def _start_initial_countdown(self):
        self._update_display(self.current_seconds_left)
        self.timer.start(1000)

    def _update_countdown(self):
        self.current_seconds_left -= 1
        if self.current_seconds_left <= 0:
            self.current_seconds_left = 0
            self.timer.stop()
            self.timer_finished.emit()
            print("Timer zakończył odliczanie!")
            # Tutaj możesz zatrzymać GIF-a, jeśli chcesz
            # self.gif_movie.stop()

        self._update_display(self.current_seconds_left)

    def _update_display(self, seconds_left):
        minutes = seconds_left // 60
        seconds = seconds_left % 60
        time_str = f"{minutes:02}:{seconds:02}"
        self.current_time_label.setText(time_str)

    def closeEvent(self, event):
        """Zatrzymuje animację GIF-a przy zamykaniu okna."""
        if self.gif_movie.state() == QMovie.Running:
            self.gif_movie.stop()
        super().closeEvent(event)