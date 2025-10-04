# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QCoreApplication

# Importujemy moduły UI
from ui.tray_icon import BreakReminderTrayIcon
from ui.main_window import SettingsStatsWindow
from vision.eye_monitor import EyeMonitorWorker, EyeTracker


class ApplicationController:
    """
    Główny kontroler łączący logikę (Timer, Vision) z UI (TrayIcon, Windows).
    """

    def __init__(self):
        # 0. Ustawienie aplikacji
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # 1. Bezpieczne określenie ścieżek do Ikon
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.ICON_PATH = os.path.join(base_dir, "resources", "icons", "flower-2.svg")
        self.APP_ICON_PATH = os.path.join(base_dir, "resources", "icons", "app-icon.svg")

        if not os.path.exists(self.ICON_PATH):
            raise FileNotFoundError(f"BŁĄD: Plik ikony nie został znaleziony! Oczekiwana ścieżka: {self.ICON_PATH}")

        # Inicjalizacja komponentów
        self._initialize_components()

        # Uruchomienie Timera i Monitora
        self._start_timer()

    def _initialize_components(self):
        """Tworzy instancje UI, Timera i Logiki Wizji."""

        # LOGIKA: Timer (główny odliczający czas pracy)
        self.timer = QTimer()
        self.timer.setInterval(15000)  # 15 sekund na potrzeby testu

        self.gaze_tracker_instance = None
        self.eye_monitor_worker = None

        try:
            self.gaze_tracker_instance = EyeTracker()
            self.eye_monitor_worker = EyeMonitorWorker(
                self.gaze_tracker_instance,
                debounce_time=0.3  # Czas w sekundach przed zatwierdzeniem zmiany stanu
            )
        except RuntimeError as e:
            print(f"BŁĄD KAMERY: {e}. Monitorowanie wzroku będzie wyłączone.")

        # UI: Okno Ustawień/Statystyk
        self.settings_window = SettingsStatsWindow(self.APP_ICON_PATH)

        # UI: Applet w zasobniku
        self.tray_icon = BreakReminderTrayIcon(self.ICON_PATH)

        self._connect_signals()

    def _connect_signals(self):
        """Łączy sygnały pomiędzy komponentami."""

        # 1. Połączenia UI / Timer:
        self.tray_icon.show_settings_signal.connect(self.settings_window.show)
        self.tray_icon.exit_app_signal.connect(self.exit_application)
        self.timer.timeout.connect(self.tray_icon.show_break_reminder)

        # 2. Połączenie Timer / Okno Główne (Wstrzymywanie podczas interakcji):
        self.settings_window.window_opened_signal.connect(self.pause_main_timer)
        self.settings_window.window_closed_signal.connect(self.resume_main_timer)

        # 3. Połączenie Vision / UI (Pauza/Wznowienie Timera przerwy):
        if self.eye_monitor_worker:
            self.eye_monitor_worker.gaze_detected_signal.connect(self.handle_gaze_change)

    def handle_gaze_change(self, looking_at_screen, x_angle, y_angle):
        """
        Obsługuje zmianę stanu patrzenia użytkownika.

        Args:
            looking_at_screen (bool): True jeśli patrzy w ekran, False jeśli nie
            x_angle (float): Kąt w osi X
            y_angle (float): Kąt w osi Y
        """
        if looking_at_screen:
            # Użytkownik zaczął patrzeć w ekran - zapauzuj timer
            self.settings_window.main_timer_tab.pause_break_timer(x_angle, y_angle)
        else:
            # Użytkownik przestał patrzeć w ekran - wznów timer
            self.settings_window.main_timer_tab.resume_break_timer()

    def pause_main_timer(self):
        """Zatrzymuje główny timer odliczający czas pracy."""
        if self.timer.isActive():
            self.timer.stop()

    def resume_main_timer(self):
        """Wznawia główny timer odliczający czas pracy."""
        if not self.timer.isActive():
            self.timer.start()

    def _start_timer(self):
        """Uruchamia timer i wątek monitorujący wzrok."""
        self.resume_main_timer()
        if self.eye_monitor_worker:
            self.eye_monitor_worker.start()
            print("Eye Monitor: Wątek uruchomiony.")
        else:
            print("Eye Monitor: Wątek nie uruchomiony (brak kamery).")

    def exit_application(self):
        """Bezpiecznie zamyka aplikację, wątek i zwalnia zasoby kamery."""
        print("Zamykanie aplikacji...")

        # 1. Zatrzymanie wątku Vision
        if self.eye_monitor_worker:
            self.eye_monitor_worker.stop()

        # 2. Zwolnienie zasobów EyeTracker
        if self.gaze_tracker_instance:
            self.gaze_tracker_instance.release()
            print("Zwolniono zasoby EyeTracker.")

        self.tray_icon.hide()
        QCoreApplication.quit()

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