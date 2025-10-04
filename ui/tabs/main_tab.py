# ui/tabs/main_timer_tab.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QMovie
import os


class MainTab(QWidget):
    """Zakładka główna z automatycznym timerem i animowanym GIF-em."""

    timer_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.total_time_seconds = 5 * 60  # 5 minut w sekundach
        self.current_seconds_left = self.total_time_seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_countdown)

        self.is_paused = False

        self.setLayout(self._setup_layout())
        self._setup_gif_player()

        # Automatyczne uruchomienie timera i GIF-a po inicjalizacji
        self._start_initial_countdown()
        self.gif_movie.start()

    def pause_break_timer(self, x_angle, y_angle):
        """
        Pauzuje timer przerwy gdy użytkownik patrzy w ekran.
        """
        if not self.is_paused and self.timer.isActive():
            self.timer.stop()
            self.is_paused = True
            self.status_label.setText(f"PAUZA! Patrzysz w ekran! (X:{x_angle:.1f}°)")
            self.status_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #ff6b6b;")

            # Opcjonalnie: zatrzymaj GIF
            if self.gif_movie.state() == QMovie.Running:
                self.gif_movie.setPaused(True)

    def resume_break_timer(self):
        """
        Wznawia timer przerwy gdy użytkownik przestaje patrzeć w ekran.
        """
        if self.is_paused:
            self.timer.start(1000)
            self.is_paused = False
            self.status_label.setText("WZNOWIONO! Kontynuuj przerwę")
            self.status_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #51cf66;")

            # Opcjonalnie: wznów GIF
            if self.gif_movie.state() == QMovie.Paused:
                self.gif_movie.setPaused(False)

    def _setup_layout(self):
        main_layout = QHBoxLayout()

        # --- Lewa sekcja: Timer ---
        timer_section_layout = QVBoxLayout()
        timer_section_layout.setAlignment(Qt.AlignCenter)

        self.status_label = QLabel("CZAS DO KOŃCA PRZERWY")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #555;")

        self.current_time_label = QLabel("05:00")
        self.current_time_label.setAlignment(Qt.AlignCenter)
        self.current_time_label.setStyleSheet("font-size: 60px; font-weight: bold; color: #333;")

        timer_section_layout.addStretch(1)
        timer_section_layout.addWidget(self.status_label)
        timer_section_layout.addWidget(self.current_time_label)
        timer_section_layout.addStretch(1)

        main_layout.addLayout(timer_section_layout, 1)

        # --- Prawa sekcja: Odtwarzacz GIF ---
        gif_section_layout = QVBoxLayout()
        gif_section_layout.setAlignment(Qt.AlignCenter)

        gif_label_title = QLabel("ANIMACJA GIF")
        gif_label_title.setAlignment(Qt.AlignCenter)
        gif_label_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #555;")

        self.gif_display_label = QLabel()
        self.gif_display_label.setAlignment(Qt.AlignCenter)
        self.gif_display_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gif_display_label.setMinimumSize(400, 300)
        self.gif_display_label.setStyleSheet("background-color: black;")

        gif_section_layout.addWidget(gif_label_title)
        gif_section_layout.addWidget(self.gif_display_label)
        gif_section_layout.addStretch(1)

        main_layout.addLayout(gif_section_layout, 3)

        return main_layout

    def _setup_gif_player(self):
        gif_file = os.path.join("resources", "movies", "Zakrywanie powiek dłońmi.gif")

        self.gif_movie = QMovie(gif_file)

        if not self.gif_movie.isValid():
            print(f"Błąd: Plik GIF '{gif_file}' nie jest prawidłowym plikiem GIF lub nie został znaleziony.")
            self.gif_display_label.setText("BŁĄD: Nie znaleziono GIF-a lub jest uszkodzony.")
            self.gif_display_label.setStyleSheet("background-color: darkred; color: white; font-size: 16px;")
        else:
            self.gif_display_label.setMovie(self.gif_movie)
            self.gif_movie.setCacheMode(QMovie.CacheAll)
            self.gif_movie.setSpeed(100)

    def _start_initial_countdown(self):
        self._update_display(self.current_seconds_left)
        self.timer.start(1000)

    def _update_countdown(self):
        self.current_seconds_left -= 1

        if self.current_seconds_left <= 0:
            self.current_seconds_left = 0
            self.timer.stop()
            self.is_paused = False
            self.timer_finished.emit()
            print("Timer zakończył odliczanie!")
            self.gif_movie.stop()
            self.status_label.setText("KONIEC PRZERWY!")
            self.status_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #4c6ef5;")

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