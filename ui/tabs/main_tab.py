# ui/tabs/main_timer_tab.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import pyqtSignal, Qt, QTimer, QUrl
from PyQt5.QtGui import QMovie
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
import os

class MainTab(QWidget):
    """Zakładka główna z automatycznym timerem i animowanym GIF-em."""

    timer_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Odtwarzacz dla instrukcji audio
        self.media_player = QMediaPlayer(self)
        self.audio_file_path = os.path.join("resources", "music", "palming_instruction.mp3")

        # Odtwarzacz dla muzyki w tle
        self.background_music_player = QMediaPlayer(self)
        self.background_music_path = os.path.join("resources", "music", "music.mp3")

        # Przygotuj playlistę dla muzyki w tle
        from PyQt5.QtMultimedia import QMediaPlaylist
        self.background_playlist = QMediaPlaylist()

        # Połącz sygnał zakończenia instrukcji z rozpoczęciem muzyki w tle
        self.media_player.mediaStatusChanged.connect(self._on_instruction_finished)

        # Dodaj sygnały debugowania dla background music player
        self.background_music_player.stateChanged.connect(self._debug_background_state)
        self.background_music_player.mediaStatusChanged.connect(self._debug_background_status)

        if os.path.exists(self.audio_file_path):
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.audio_file_path)))
        else:
            print(f"Błąd: Plik audio '{self.audio_file_path}' nie został znaleziony.")

        if os.path.exists(self.background_music_path):
            # Skonfiguruj playlistę dla muzyki w tle
            self.background_playlist.addMedia(QMediaContent(QUrl.fromLocalFile(self.background_music_path)))
            self.background_playlist.setPlaybackMode(QMediaPlaylist.Loop)
            self.background_music_player.setPlaylist(self.background_playlist)
            print(f"Muzyka w tle przygotowana: {self.background_music_path}")
        else:
            print(f"Błąd: Plik muzyki '{self.background_music_path}' nie został znaleziony.")

        self.total_time_seconds = 5 * 60
        self.current_seconds_left = self.total_time_seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_countdown)

        self.is_paused = False

        self.setLayout(self._setup_layout())
        self._setup_gif_player()
        self._start_initial_countdown()

    def pause_break_timer(self, x_angle, y_angle):
        """
        Pauzuje timer przerwy gdy użytkownik patrzy w ekran.
        """
        if not self.is_paused and self.timer.isActive():
            self.timer.stop()
            self.is_paused = True
            self.status_label.setText(f"PAUZA! Patrzysz w ekran! (X:{x_angle:.1f}°)")
            self.status_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #ff6b6b;")

    def resume_break_timer(self):
        """
        Wznawia timer przerwy gdy użytkownik przestaje patrzeć w ekran.
        """
        if self.is_paused:
            self.timer.start(1000)
            self.is_paused = False
            self.status_label.setText("WZNOWIONO! Kontynuuj przerwę")
            self.status_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #51cf66;")

    def _setup_layout(self):
        main_layout = QHBoxLayout()

        timer_section_layout = QVBoxLayout()
        timer_section_layout.setAlignment(Qt.AlignCenter)

        self.status_label = QLabel("CZAS DO KOŃCA PRZERWY")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #555;")

        # BPM label placed above the timer display
        self.bpm_label = QLabel("BPM: --")
        self.bpm_label.setAlignment(Qt.AlignCenter)
        self.bpm_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #777;")

        self.current_time_label = QLabel("05:00")
        self.current_time_label.setAlignment(Qt.AlignCenter)
        self.current_time_label.setStyleSheet("font-size: 60px; font-weight: bold; color: #333;")

        timer_section_layout.addStretch(1)
        timer_section_layout.addWidget(self.status_label)
        timer_section_layout.addWidget(self.bpm_label)
        timer_section_layout.addWidget(self.current_time_label)
        timer_section_layout.addStretch(1)

        main_layout.addLayout(timer_section_layout, 1)

        # --- Prawa sekcja: Odtwarzacz GIF ---
        gif_section_layout = QVBoxLayout()
        gif_section_layout.setAlignment(Qt.AlignCenter)

        self.gif_display_label = QLabel()
        self.gif_display_label.setAlignment(Qt.AlignCenter)
        self.gif_display_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gif_display_label.setMinimumSize(400, 300)
        self.gif_display_label.setStyleSheet("background-color: black;")

        gif_section_layout.addWidget(self.gif_display_label)
        gif_section_layout.addStretch(1)

        main_layout.addLayout(gif_section_layout, 3)

        return main_layout

    def _setup_gif_player(self):
        gif_file = os.path.join("resources","gifs","palming.gif")

        self.gif_movie = QMovie(gif_file)

        if not self.gif_movie.isValid():
            print(f"Błąd: Plik GIF '{gif_file}' nie jest prawidłowym plikiem GIF lub nie został znaleziony.")
            self.gif_display_label.setText("BŁĄD: Nie znaleziono GIF-a lub jest uszkodzony.")
            self.gif_display_label.setStyleSheet("background-color: darkred; color: white; font-size: 16px;")
        else:
            self.gif_display_label.setMovie(self.gif_movie)
            self.gif_display_label.setScaledContents(True)
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

    def set_bpm(self, bpm):
        """Ustawia wartość BPM widoczną nad timerem.
        
        Przekazanie None ustawi tekst na '--'.
        """
        if bpm is None:
            text = "BPM: --"
        else:
            try:
                text = f"BPM: {int(bpm)}"
            except Exception:
                text = "BPM: --"
        
        self.bpm_label.setText(text)

    def _on_instruction_finished(self, status):
        """Obsługuje zakończenie instrukcji i rozpoczyna muzykę w tle."""
        print(f"Instruction status changed: {status}")
        if status == QMediaPlayer.EndOfMedia:
            print("Instrukcja zakończona, uruchamiam muzykę w tle...")
            # Instrukcja się skończyła, rozpocznij muzykę w tle
            if os.path.exists(self.background_music_path):
                print(f"Plik muzyki istnieje: {self.background_music_path}")
                print(f"Rozmiar pliku: {os.path.getsize(self.background_music_path)} bajtów")

                # Sprawdź stan odtwarzacza przed próbą odtwarzania
                print(f"Stan background player przed play(): {self.background_music_player.state()}")
                print(f"Status background player przed play(): {self.background_music_player.mediaStatus()}")

                # Próba ręcznego ustawienia media przed odtwarzaniem
                self.background_music_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.background_music_path)))
                self.background_music_player.play()
                print("Komenda play() została wywołana na background music player.")
            else:
                print("Nie można uruchomić muzyki w tle - brak pliku.")

    def _debug_background_state(self, state):
        """Debug: wyświetla zmiany stanu background music player"""
        states = {
            QMediaPlayer.StoppedState: "Stopped",
            QMediaPlayer.PlayingState: "Playing",
            QMediaPlayer.PausedState: "Paused"
        }
        print(f"Background music state: {states.get(state, 'Unknown')}")

    def _debug_background_status(self, status):
        """Debug: wyświetla zmiany statusu background music player"""
        statuses = {
            QMediaPlayer.UnknownMediaStatus: "Unknown",
            QMediaPlayer.NoMedia: "No Media",
            QMediaPlayer.LoadingMedia: "Loading",
            QMediaPlayer.LoadedMedia: "Loaded",
            QMediaPlayer.StalledMedia: "Stalled",
            QMediaPlayer.BufferingMedia: "Buffering",
            QMediaPlayer.BufferedMedia: "Buffered",
            QMediaPlayer.EndOfMedia: "End of Media",
            QMediaPlayer.InvalidMedia: "Invalid Media"
        }
        print(f"Background music status: {statuses.get(status, 'Unknown')}")

    def closeEvent(self, event):
        """Zatrzymuje animację GIF-a przy zamykaniu okna."""
        if self.gif_movie.state() == QMovie.Running:
            self.gif_movie.stop()
        super().closeEvent(event)

    def showEvent(self, event):
        """Metoda wywoływana, gdy zakładka staje się widoczna."""
        super().showEvent(event)

        # Uruchom instrukcję audio (muzyka w tle rozpocznie się automatycznie po zakończeniu)
        if os.path.exists(self.audio_file_path) and self.media_player.state() != QMediaPlayer.PlayingState:
            self.media_player.play()
            print("Instrukcja audio rozpoczęta.")
        elif not os.path.exists(self.audio_file_path):
            # Jeśli nie ma instrukcji, od razu uruchom muzykę w tle
            self._start_background_music()

        if not self.timer.isActive():
            self._start_initial_countdown()
            print("Timer rozpoczęty.")

        if self.gif_movie.isValid() and self.gif_movie.state() != QMovie.Running:
            self.gif_movie.start()
            print("GIF rozpoczęty.")

    def hideEvent(self, event):
        """Metoda wywoływana, gdy zakładka przestaje być widoczna."""
        super().hideEvent(event)

        # Zatrzymaj oba odtwarzacze
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.stop()
            print("Instrukcja audio zatrzymana.")

        if self.background_music_player.state() == QMediaPlayer.PlayingState:
            self.background_music_player.stop()
            print("Muzyka w tle zatrzymana.")

        if self.timer.isActive():
            self.timer.stop()
            print("Timer zatrzymany.")

        if self.gif_movie.isValid() and self.gif_movie.state() == QMovie.Running:
            self.gif_movie.stop()
            print("GIF zatrzymany.")

    def start_session(self):
        """Uruchamia sesję - wywoływana z main_window.py"""
        # Uruchom instrukcję audio (muzyka w tle rozpocznie się automatycznie po zakończeniu)
        if os.path.exists(self.audio_file_path) and self.media_player.state() != QMediaPlayer.PlayingState:
            print(f"Uruchamiam instrukcję: {self.audio_file_path}")
            self.media_player.play()
            print("Instrukcja audio rozpoczęta.")
        elif not os.path.exists(self.audio_file_path):
            # Jeśli nie ma instrukcji, od razu uruchom muzykę w tle
            print("Brak instrukcji, uruchamiam muzykę w tle...")
            self._start_background_music()

        if not self.timer.isActive():
            self._start_initial_countdown()
            print("Timer rozpoczęty.")

        if self.gif_movie.isValid() and self.gif_movie.state() != QMovie.Running:
            self.gif_movie.start()
            print("GIF rozpoczęty.")

    def stop_session(self):
        """Zatrzymuje sesję - wywoływana z main_window.py"""
        # Zatrzymaj oba odtwarzacze
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.stop()
            print("Instrukcja audio zatrzymana.")

        if self.background_music_player.state() == QMediaPlayer.PlayingState:
            self.background_music_player.stop()
            print("Muzyka w tle zatrzymana.")

        if self.timer.isActive():
            self.timer.stop()
            print("Timer zatrzymany.")

        if self.gif_movie.isValid() and self.gif_movie.state() == QMovie.Running:
            self.gif_movie.stop()

        self.current_seconds_left = self.total_time_seconds
        self._update_display(self.current_seconds_left)

    def _start_background_music(self):
        """Uruchamia muzykę w tle w pętli."""
        if os.path.exists(self.background_music_path):
            self.background_music_player.play()
            print("Muzyka w tle rozpoczęta (pętla).")
        else:
            print("Nie można uruchomić muzyki w tle - brak pliku.")