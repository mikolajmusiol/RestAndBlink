from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import pyqtSignal, Qt, QTimer, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
import os

class MainTab(QWidget):
    """Zakładka główna z automatycznym timerem i odtwarzaczem wideo."""

    timer_finished = pyqtSignal() # Sygnał, gdy timer skończy odliczanie

    def __init__(self, parent=None):
        super().__init__(parent) # POPRAWIONA LINIA TUTAJ
        self.total_time_seconds = 5 * 60  # 5 minut w sekundach
        self.current_seconds_left = self.total_time_seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_countdown)

        self.setLayout(self._setup_layout())
        self._setup_media_player()

        # Automatyczne uruchomienie timera i odtwarzacza po inicjalizacji
        self._start_initial_countdown()
        self.media_player.play() # Start wideo

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

        # --- Prawa sekcja: Odtwarzacz wideo ---
        video_section_layout = QVBoxLayout()
        video_section_layout.setAlignment(Qt.AlignCenter)

        video_label = QLabel("ODTWARZACZ WIDEO") # Możesz usunąć tę etykietę, jeśli nie chcesz jej
        video_label.setAlignment(Qt.AlignCenter)
        video_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #555;")


        self.video_widget = QVideoWidget()
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_widget.setMinimumSize(400, 300) # Minimalny rozmiar

        video_section_layout.addWidget(video_label) # Możesz usunąć tę linię, jeśli nie chcesz etykiety
        video_section_layout.addWidget(self.video_widget)
        video_section_layout.addStretch(1) # Rozciągnij, aby wideo zajęło dostępną przestrzeń

        main_layout.addLayout(video_section_layout, 3) # 2/3 szerokości dla wideo

        return main_layout

    def _setup_media_player(self):
        self.media_player = QMediaPlayer(self)
        self.media_player.setVideoOutput(self.video_widget)

        video_file = os.path.join("resources","movies","fast_blinking.mp4") # ZMIEŃ NA NAZWĘ SWOJEGO PLIKU!

        if os.path.exists(video_file):
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_file)))
        else:
            print(f"Błąd: Plik wideo '{video_file}' nie został znaleziony.")
            print("Upewnij się, że masz plik wideo w folderze 'movies' i zmieniono jego nazwę w kodzie.")
            # Jeśli plik nie istnieje, możesz wyświetlić komunikat w QVideoWidget lub ustawić pusty ekran
            # self.video_widget.setStyleSheet("background-color: black; color: white;") # Przykładowy styl


    def _start_initial_countdown(self):
        self._update_display(self.current_seconds_left) # Ustawia początkowy czas
        self.timer.start(1000)  # Odśwież co sekundę

    def _update_countdown(self):
        self.current_seconds_left -= 1
        if self.current_seconds_left <= 0:
            self.current_seconds_left = 0
            self.timer.stop()
            self.timer_finished.emit() # Wyślij sygnał, że timer skończył
            # Tutaj możesz dodać kod, który wykona się po zakończeniu timera, np. zatrzymanie wideo
            # self.media_player.stop()
            print("Timer zakończył odliczanie!")

        self._update_display(self.current_seconds_left)

    def _update_display(self, seconds_left):
        minutes = seconds_left // 60
        seconds = seconds_left % 60
        time_str = f"{minutes:02}:{seconds:02}"
        self.current_time_label.setText(time_str)