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
        self.ICON_PATH = os.path.join(base_dir, "resources", "icons", "flower-2.svg")
        self.APP_ICON_PATH = os.path.join(base_dir, "resources", "icons", "app-icon.svg")

        if not os.path.exists(self.ICON_PATH):
            raise FileNotFoundError(f"BŁĄD: Plik ikony nie został znaleziony! Oczekiwana ścieżka: {self.ICON_PATH}")

        self._initialize_components()

        self._start_main_timer()

    def _initialize_components(self):
        """Tworzy instancje UI, Timera i Logiki Wizji."""

        self.main_work_timer = QTimer()
        self.main_work_timer.setInterval(10000)  # TEST: 10 sekund. Zmień na 3600000 dla 60 minut!

        self.gaze_tracker_instance = None
        self.eye_monitor_worker = None

        try:
            self.gaze_tracker_instance = EyeTracker()
            self.eye_monitor_worker = EyeMonitorWorker(self.gaze_tracker_instance)
        except RuntimeError as e:
            print(f"BŁĄD KAMERY: {e}. Monitorowanie wzroku będzie wyłączone.")

        # UI: Okno Ustawień/Statystyk
        self.settings_window = SettingsStatsWindow(self.APP_ICON_PATH)

        # UI: Applet w zasobniku
        self.tray_icon = BreakReminderTrayIcon(self.ICON_PATH)
        self.tray_icon.setToolTip("Break Reminder: Pracuję...")

        self._connect_signals()

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
        Rozpoczyna sesję przerwy. Wywoływane po kliknięciu powiadomienia.
        Aktywuje: Tryb Przerwy, Okno Ustawień, Timer Przerwy, Monitor Wzroku.
        """
        print("Rozpoczynanie sesji przerwy...")
        self.current_state = self.STATE_BREAK
        self.tray_icon.setToolTip("Break Reminder: Jesteś na PRZERWIE!")

        # 1. Uruchom monitor wzroku
        if self.eye_monitor_worker:
            self.eye_monitor_worker.start()
            print("Eye Monitor: Wątek uruchomiony do śledzenia przerwy.")

        # 2. Otwórz i aktywuj okno z timerem przerwy
        self.settings_window.show()
        self.settings_window.main_timer_tab.start_session()

    def start_work_session(self):
        """
        Rozpoczyna sesję pracy. Wywoływane po zakończeniu timera przerwy.
        Aktywuje: Tryb Pracy, Główny Timer, Zatrzymuje Monitor Wzroku.
        """
        print("Wznawianie sesji pracy...")
        self.current_state = self.STATE_WORKING
        self.tray_icon.setToolTip("Break Reminder: Pracuję...")

        # 1. Zatrzymanie wątku Vision
        if self.eye_monitor_worker and self.eye_monitor_worker.isRunning():
            self.eye_monitor_worker.stop()

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
            self.settings_window.main_timer_tab.pause_break_timer(x_angle, y_angle)
        else:
            # Użytkownik przestał patrzeć w ekran - wznów timer
            self.settings_window.main_timer_tab.resume_break_timer()

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
        self.resume_main_timer()  # Wznowienie lub rozpoczęcie

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