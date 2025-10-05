# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QCoreApplication, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# Importujemy moduły UI
from ui.tray_icon import BreakReminderTrayIcon
from ui.enhanced_wellness_window import EnhancedWellnessWindow
from vision.eye_monitor import EyeMonitorWorker, EyeTracker

import cv2
import mediapipe as mp
import numpy as np
import time
import math


def create_linux_eye_tracker(rest_threshold=10):
    """Tworzy EyeTracker naprawiony dla Linuxa."""
    # Monkey patch - zastępujemy tylko problematyczną linię
    original_init = EyeTracker.__init__
    
    def linux_init(self, rest_threshold=10):
        # Wywołaj oryginalny __init__ ale z poprawką dla Linuxa
        self.cap = cv2.VideoCapture(0)  # Bez CAP_DSHOW
        if not self.cap.isOpened():
            raise RuntimeError("Camera not accessible")

        import mediapipe as mp
        mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
        self.last_focus_time = time.time()
        self.rest_threshold = rest_threshold
        self.h = 0
        self.w = 0
    
    # Tymczasowo zastąp __init__
    EyeTracker.__init__ = linux_init
    tracker = EyeTracker(rest_threshold)
    # Przywróć oryginalny __init__
    EyeTracker.__init__ = original_init
    
    return tracker

class ApplicationController:
    """
    Główny kontroler łączący logikę (Timer, Vision) z UI (TrayIcon, Windows).
    """

    # STANY APLIKACJI
    STATE_WORKING = "WORKING"
    STATE_BREAK = "BREAK"

    def __init__(self):
        # 0. Ustawienie aplikacji
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.current_state = self.STATE_WORKING  # Start w trybie pracy

        # 1. Bezpieczne określenie ścieżek do Ikon
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Sprawdzaj różne opcje ikon
        icon_options = [
            os.path.join(base_dir, "resources", "icons", "logo.png"),
            os.path.join(base_dir, "resources", "icons", "flower-2.svg"),
            os.path.join(base_dir, "resources", "icons", "app-icon.svg")
        ]
        
        self.ICON_PATH = None
        for icon_path in icon_options:
            if os.path.exists(icon_path):
                self.ICON_PATH = icon_path
                print(f"Używam ikony: {icon_path}")
                break
        
        if not self.ICON_PATH:
            # Utwórz prostą ikonę jako fallback
            self.ICON_PATH = self._create_fallback_icon(base_dir)
        
        self.APP_ICON_PATH = self.ICON_PATH

        # Inicjalizacja komponentów
        self._initialize_components()

        self._start_main_timer()

    def _initialize_components(self):
        """Tworzy instancje UI, Timera i Logiki Wizji."""

        self.main_work_timer = QTimer()
        self.main_work_timer.setInterval(10000)  # TEST: 10 sekund. Zmień na 3600000 dla 60 minut!

        self.gaze_tracker_instance = None
        self.eye_monitor_worker = None

        # Testuj kamerę prostym sposobem
        print("Testowanie dostępu do kamery...")
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                print("OpenCV: Kamera dostępna")
                cap.release()
                
                # Próbuj zainicjalizować EyeTracker z workaround dla Linuxa
                try:
                    print("Inicjalizacja EyeTracker...")
                    # Tworzymy LinuxEyeTracker - wrapper który naprawia problem CAP_DSHOW
                    self.gaze_tracker_instance = create_linux_eye_tracker()
                    print("LinuxEyeTracker zainicjalizowany pomyślnie")
                    
                    print("Inicjalizacja EyeMonitorWorker...")
                    self.eye_monitor_worker = EyeMonitorWorker(self.gaze_tracker_instance)
                    print("EyeMonitorWorker zainicjalizowany pomyślnie")
                    
                except Exception as e:
                    print(f"Błąd podczas inicjalizacji EyeTracker: {type(e).__name__}: {e}")
                    self.gaze_tracker_instance = None
                    self.eye_monitor_worker = None
            else:
                print("OpenCV: Kamera niedostępna")
                self.gaze_tracker_instance = None
                self.eye_monitor_worker = None
        except Exception as e:
            print(f"OpenCV test error: {e}")
            self.gaze_tracker_instance = None
            self.eye_monitor_worker = None

        # UI: Okno Enhanced Wellness (zamiast SettingsStatsWindow)
        self.settings_window = EnhancedWellnessWindow()
        
        # Zastąp zawartość kafelka Main po utworzeniu okna
        self._replace_main_content()

        # UI: Applet w zasobniku
        self.tray_icon = BreakReminderTrayIcon(self.ICON_PATH)
        self.tray_icon.setToolTip("Break Reminder: Pracuję...")

        self._connect_signals()
        
        # Pokaż okno od razu przy starcie aplikacji
        self.settings_window.show()
        

    def _connect_signals(self):
        """Łączy sygnały pomiędzy komponentami."""

        # 1. Połączenia UI / Timer:
        self.tray_icon.show_settings_signal.connect(self.settings_window.show)
        self.tray_icon.exit_app_signal.connect(self.exit_application)

        # Główny Timer ZAKOŃCZONY -> Pokaż przypomnienie
        self.main_work_timer.timeout.connect(self.start_break_prompt)

        # Kliknięcie na powiadomienie w trayu -> Rozpocznij przerwę (otwórz okno)
        self.tray_icon.break_activated_signal.connect(self.start_break_session)

        # Koniec przerwy w MainTab -> Wznów pracę
        self.settings_window.main_timer_tab.timer_finished.connect(self.start_work_session)

        # 2. Połączenie Timer / Okno Główne (Wstrzymywanie podczas interakcji):
        # EnhancedWellnessWindow nie ma tych sygnałów, więc je pomijamy
        # Wstrzymujemy/Wznawiamy tylko główny timer pracy, gdy okno ustawień jest otwarte/zamknięte.
        self.settings_window.window_opened_signal.connect(self.pause_main_timer)
        self.settings_window.window_closed_signal.connect(self.resume_main_timer)

        # 3. Połączenie Vision / UI (Pauza/Wznowienie Timera przerwy):
        if self.eye_monitor_worker:
            self.eye_monitor_worker.gaze_detected_signal.connect(self.handle_gaze_change)

    def start_break_prompt(self):
        """Timer pracy zakończony. Zatrzymuje timer, pokazuje powiadomienie."""
        if self.current_state == self.STATE_WORKING:
            self.main_work_timer.stop()
            self.tray_icon.show_break_reminder()  # Pokazuje systemowe powiadomienie, które po kliknięciu wywoła `start_break_session`

    def start_break_session(self):
        """
        Rozpoczyna sesję przerwy.
        Aktywuje: Tryb Przerwy, Okno Ustawień, Timer Przerwy, WŁĄCZA ŚLEDZENIE WZROKU W WĄTKU.
        """
        print("Rozpoczynanie sesji przerwy...")
        self.current_state = self.STATE_BREAK
        self.tray_icon.setToolTip("Break Reminder: Jesteś na PRZERWIE!")

        # 1. Zmień stan w wątku Vision, aby zaczął przetwarzać
        if self.eye_monitor_worker:
            self.eye_monitor_worker.set_tracking_enabled(True)  # NOWOŚĆ!
            print("Eye Monitor: Wątek AKTYWOWANY do śledzenia przerwy.")

        # 2. Otwórz i aktywuj okno z timerem przerwy
        self.settings_window.show()
        self.settings_window.main_timer_tab.start_session()

    def start_work_session(self):
        """
        Rozpoczyna sesję pracy.
        Aktywuje: Tryb Pracy, Główny Timer, WYŁĄCZA ŚLEDZENIE WZROKU W WĄTKU.
        """
        print("Wznawianie sesji pracy...")
        self.current_state = self.STATE_WORKING
        self.tray_icon.setToolTip("Break Reminder: Pracuję...")

        # 1. Zmień stan w wątku Vision, aby przestał przetwarzać (lub ignorował wyniki)
        if self.eye_monitor_worker and self.eye_monitor_worker.isRunning():
            self.eye_monitor_worker.set_tracking_enabled(False)  # NOWOŚĆ!
            print("Eye Monitor: Wątek ZAWIESZONY/WYŁĄCZONY (czeka).")

        # 2. Wznów główny timer pracy
        self._start_main_timer()

    def handle_gaze_change(self, looking_at_screen, x_angle, y_angle):
        """
        Obsługuje zmianę stanu patrzenia użytkownika. Aktywna tylko w trakcie przerwy.
        """
        if self.current_state != self.STATE_BREAK:
            return  # Ignoruj śledzenie wzroku w trybie pracy

        if looking_at_screen:
            # Użytkownik zaczął patrzeć w ekran - zapauzuj timer
            self.pause_main_break_timer(x_angle, y_angle)
        else:
            # Użytkownik przestał patrzeć w ekran - wznów timer
            self.resume_main_break_timer()

    def pause_main_timer(self):
        """Zatrzymuje główny timer odliczający czas pracy (np. gdy otwarte ustawienia)."""
        if self.current_state == self.STATE_WORKING and self.main_work_timer.isActive():
            self.main_work_timer.stop()

    def resume_main_timer(self):
        """Wznawia główny timer odliczający czas pracy (np. gdy zamknięte ustawienia)."""
        if self.current_state == self.STATE_WORKING and not self.main_work_timer.isActive():
            self.main_work_timer.start()

    def _start_main_timer(self):
        """Uruchamia główny timer pracy."""
        self.resume_main_timer()

        # Uruchamiamy wątek monitora tylko raz na starcie aplikacji.
        if self.eye_monitor_worker:
            self.eye_monitor_worker.start()
            self.eye_monitor_worker.set_tracking_enabled(False)  # Początkowo wyłączony
            print("Eye Monitor: Wątek uruchomiony (w tle, wyłączony).")
        else:
            print("Eye Monitor: Wątek nie uruchomiony (brak kamery).")

    def exit_application(self):
        """Bezpiecznie zamyka aplikację, wątek i zwalnia zasoby kamery."""
        print("Zamykanie aplikacji...")

        # 1. Zatrzymanie wątku Vision (tutaj musi być stop, by zamknąć wątek)
        if self.eye_monitor_worker and self.eye_monitor_worker.isRunning():
            self.eye_monitor_worker.stop()

        # 2. Zwolnienie zasobów EyeTracker
        if self.gaze_tracker_instance:
            self.gaze_tracker_instance.release()
            print("Zwolniono zasoby EyeTracker.")

        self.tray_icon.hide()
        QCoreApplication.quit()

    def _create_enhanced_main_page(self):
        """Tworzy stronę Main z pełną funkcjonalnością MainTab."""
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
        from PyQt5.QtCore import QTimer, Qt
        from PyQt5.QtGui import QMovie, QFont
        from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
        from PyQt5.QtCore import QUrl
        import os
        
        main_page = QWidget()
        main_page.setStyleSheet("background-color: #1a1d1f;")
        
        # Odtwarzacz dla instrukcji audio
        self.media_player = QMediaPlayer(main_page)
        self.audio_file_path = os.path.join("resources", "music", "palming_instruction.mp3")

        # Odtwarzacz dla muzyki w tle
        self.background_music_player = QMediaPlayer(main_page)
        self.background_music_path = os.path.join("resources", "music", "music.mp3")

        # Przygotuj playlistę dla muzyki w tle
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
            self.background_playlist.addMedia(QMediaContent(QUrl.fromLocalFile(self.background_music_path)))
            self.background_playlist.setPlaybackMode(QMediaPlaylist.Loop)
            self.background_music_player.setPlaylist(self.background_playlist)
            print(f"Muzyka w tle przygotowana: {self.background_music_path}")
        else:
            print(f"Błąd: Plik muzyki '{self.background_music_path}' nie został znaleziony.")

        self.total_time_seconds = 5 * 60
        self.current_seconds_left = self.total_time_seconds
        self.main_page_timer = QTimer(main_page)
        self.main_page_timer.timeout.connect(self._update_countdown)

        self.is_main_paused = False

        # Setup layout dokładnie jak w MainTab
        main_layout = QHBoxLayout(main_page)

        # Lewa sekcja: Timer i status wzroku
        timer_section_layout = QVBoxLayout()
        timer_section_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # BPM label placed above the timer display - make it prominent
        self.bpm_label = QLabel("BPM: --")
        self.bpm_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bpm_label.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #00ff88; 
            background-color: rgba(0, 255, 136, 0.1);
            border: 2px solid #00ff88;
            border-radius: 8px;
            padding: 8px;
            margin: 5px;
        """)

        self.status_label = QLabel("CZAS DO KOŃCA PRZERWY")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #e8e9ea;")


        self.current_time_label = QLabel("05:00")
        self.current_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_time_label.setStyleSheet("font-size: 60px; font-weight: bold; color: #e8e9ea;")

        # Status wzroku
        self.gaze_status_label = QLabel("Status wzroku: Sprawdzanie...")
        self.gaze_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gaze_status_label.setStyleSheet("font-size: 16px; color: #ffd700; margin: 10px;")

        timer_section_layout.addStretch(1)
        timer_section_layout.addWidget(self.bpm_label)
        timer_section_layout.addWidget(self.status_label)
        timer_section_layout.addWidget(self.current_time_label)
        timer_section_layout.addWidget(self.gaze_status_label)
        timer_section_layout.addStretch(1)

        main_layout.addLayout(timer_section_layout, 1)

        # Prawa sekcja: GIF
        gif_section_layout = QVBoxLayout()
        gif_section_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gif_display_label = QLabel()
        self.gif_display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gif_display_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gif_display_label.setMinimumSize(400, 300)
        self.gif_display_label.setStyleSheet("background-color: black;")

        gif_section_layout.addWidget(self.gif_display_label)
        gif_section_layout.addStretch(1)

        main_layout.addLayout(gif_section_layout, 3)

        # Setup GIF player
        self._setup_main_gif_player()
        
        # Start timer i audio
        self._start_main_session()
        
        return main_page

    def _setup_main_gif_player(self):
        """Konfiguruje odtwarzacz GIF dla strony Main."""
        from PyQt5.QtGui import QMovie
        gif_file = os.path.join("resources","gifs","palming.gif")

        self.gif_movie = QMovie(gif_file)

        if not self.gif_movie.isValid():
            print(f"Błąd: Plik GIF '{gif_file}' nie jest prawidłowym plikiem GIF lub nie został znaleziony.")
            self.gif_display_label.setText("BŁĄD: Nie znaleziono GIF-a lub jest uszkodzony.")
            self.gif_display_label.setStyleSheet("background-color: darkred; color: white; font-size: 16px;")
        else:
            self.gif_display_label.setMovie(self.gif_movie)
            self.gif_display_label.setScaledContents(True)
            self.gif_movie.setCacheMode(QMovie.CacheMode.CacheAll)
            self.gif_movie.setSpeed(100)

    def _start_main_session(self):
        """Uruchamia sesję na stronie Main."""
        # Uruchom audio jeśli dostępne
        if os.path.exists(self.audio_file_path):
            self.media_player.play()
            print("Instrukcja audio rozpoczęta.")
        else:
            # Jeśli nie ma instrukcji, od razu uruchom muzykę w tle
            print("Brak instrukcji, uruchamiam muzykę w tle...")
            self._start_background_music()

        # Uruchom timer
        self._update_main_display(self.current_seconds_left)
        self.main_page_timer.start(1000)

        # Uruchom GIF
        if self.gif_movie.isValid():
            self.gif_movie.start()
            print("GIF rozpoczęty.")

    def _update_countdown(self):
        """Aktualizuje odliczanie na stronie Main."""
        self.current_seconds_left -= 1

        if self.current_seconds_left <= 0:
            self.current_seconds_left = 0
            self.main_page_timer.stop()
            self.is_main_paused = False
            print("Timer Main zakończył odliczanie!")
            if self.gif_movie.isValid():
                self.gif_movie.stop()
            self.status_label.setText("KONIEC PRZERWY!")
            self.status_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #4c6ef5;")

        self._update_main_display(self.current_seconds_left)

    def _update_main_display(self, seconds_left):
        """Aktualizuje wyświetlanie czasu na stronie Main."""
        minutes = seconds_left // 60
        seconds = seconds_left % 60
        time_str = f"{minutes:02}:{seconds:02}"
        self.current_time_label.setText(time_str)

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

    def _start_background_music(self):
        """Uruchamia muzykę w tle w pętli."""
        if os.path.exists(self.background_music_path):
            self.background_music_player.play()
            print("Muzyka w tle rozpoczęta (pętla).")
        else:
            print("Nie można uruchomić muzyki w tle - brak pliku.")

    def pause_main_break_timer(self, x_angle, y_angle):
        """Pauzuje timer przerwy gdy użytkownik patrzy w ekran."""
        if hasattr(self, 'gaze_status_label'):
            if not self.is_main_paused and self.main_page_timer.isActive():
                self.main_page_timer.stop()
                self.is_main_paused = True
                self.status_label.setText(f"PAUZA! Patrzysz w ekran!")
                self.status_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #ff6b6b;")
                self.gaze_status_label.setText(f"👁️ PATRZYSZ W EKRAN (X:{x_angle:.1f}°, Y:{y_angle:.1f}°)")
                self.gaze_status_label.setStyleSheet("font-size: 16px; color: #ff6b6b; margin: 10px;")

    def resume_main_break_timer(self):
        """Wznawia timer przerwy gdy użytkownik przestaje patrzeć w ekran."""
        if hasattr(self, 'gaze_status_label'):
            if self.is_main_paused:
                self.main_page_timer.start(1000)
                self.is_main_paused = False
                self.status_label.setText("WZNOWIONO! Kontynuuj przerwę")
                self.status_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #51cf66;")
                self.gaze_status_label.setText("✅ NIE PATRZYSZ W EKRAN - Dobra robota!")
                self.gaze_status_label.setStyleSheet("font-size: 16px; color: #51cf66; margin: 10px;")

    def _create_fallback_icon(self, base_dir):
        """Tworzy prostą ikonę jako fallback."""
        from PyQt5.QtGui import QPixmap, QPainter, QBrush, QColor
        from PyQt5.QtCore import Qt
        
        # Utwórz prosty pixmap jako ikonę
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))  # Przezroczyste tło
        
        painter = QPainter(pixmap)
        painter.setBrush(QBrush(QColor(61, 90, 128)))  # Niebieski kolor
        painter.drawEllipse(4, 4, 24, 24)
        painter.end()
        
        # Zapisz jako plik tymczasowy
        fallback_path = os.path.join(base_dir, "fallback_icon.png")
        pixmap.save(fallback_path)
        print(f"Utworzono fallback ikonę: {fallback_path}")
        
        return fallback_path

    def _replace_main_content(self):
        """Zastępuje zawartość kafelka Main w Enhanced Wellness Window."""
        # Znajdź content_stack w Enhanced Wellness Window
        if hasattr(self.settings_window, 'content_stack'):
            # Usuń starą stronę Main (index 0)
            old_main_page = self.settings_window.content_stack.widget(0)
            if old_main_page:
                self.settings_window.content_stack.removeWidget(old_main_page)
                old_main_page.deleteLater()
            
            # Dodaj nową stronę Main z pełną funkcjonalnością
            new_main_page = self._create_enhanced_main_page()
            self.settings_window.content_stack.insertWidget(0, new_main_page)
            print("Zawartość kafelka Main została zastąpiona")
        else:
            print("BŁĄD: Nie można znaleźć content_stack w Enhanced Wellness Window")

    def set_bpm(self, bpm):
        """Ustawia wartość BPM widoczną nad timerem.
        
        Przekazanie None ustawi tekst na '--'.
        """
        try:
            if hasattr(self, 'bpm_label') and self.bpm_label is not None:
                if bpm is None:
                    text = "BPM: --"
                else:
                    try:
                        text = f"BPM: {int(bpm)}"
                    except Exception:
                        text = "BPM: --"
                self.bpm_label.setText(text)
        except Exception as e:
            print(f"Failed to set BPM label: {e}")

    def run(self):
        """Uruchamia pętlę zdarzeń aplikacji."""
        return self.app.exec_()


if __name__ == '__main__':
    try:
        controller = ApplicationController()
        sys.exit(controller.run())
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")
        sys.exit(1)
