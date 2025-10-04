# main.py

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QCoreApplication

# Importujemy moduły UI
from ui.tray_icon import BreakReminderTrayIcon
from ui.main_window import SettingsStatsWindow


class ApplicationController:
    """
    Główny kontroler łączący logikę (Timer) z UI (TrayIcon, Windows).
    """

    def __init__(self):
        # 0. Ustawienie aplikacji
        self.app = QApplication(sys.argv)
        # Zapobiega zamknięciu aplikacji, gdy okno jest ukryte
        self.app.setQuitOnLastWindowClosed(False)

        # 1. Bezpieczne określenie ścieżki do Ikony (Klucz do rozwiązania problemu z wyświetlaniem)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.ICON_PATH = os.path.join(base_dir, "resources", "icons", "flower-2.svg")

        # Sprawdzenie, czy plik istnieje
        if not os.path.exists(self.ICON_PATH):
            raise FileNotFoundError(f"BŁĄD: Plik ikony nie został znaleziony! Oczekiwana ścieżka: {self.ICON_PATH}")

        # 2. Inicjalizacja komponentów
        self._initialize_components()

        # 3. Uruchomienie Timera
        self._start_timer()

    def _initialize_components(self):
        """Tworzy instancje UI i Logiki."""

        # UI: Okno Ustawień/Statystyk
        self.settings_window = SettingsStatsWindow()

        # UI: Applet w zasobniku
        self.tray_icon = BreakReminderTrayIcon(self.ICON_PATH)

        # LOGIKA: Timer
        self.timer = QTimer()
        self.timer.setInterval(15000)  # 15 sekund na potrzeby testu

        # 4. Łączenie sygnałów
        self._connect_signals()

    def _connect_signals(self):
        """Łączy sygnały pomiędzy komponentami."""

        # ... (Istniejące połączenia bez zmian) ...
        self.tray_icon.show_settings_signal.connect(self.settings_window.show)
        self.timer.timeout.connect(self.tray_icon.show_break_reminder)
        self.tray_icon.exit_app_signal.connect(self.exit_application)

        # --- KLUCZOWE NOWE POŁĄCZENIA ---
        # 1. Zatrzymanie timera, gdy okno ustawień jest otwierane
        self.settings_window.window_opened_signal.connect(self.pause_main_timer)

        # 2. Wznowienie timera, gdy okno ustawień jest zamykane (ukrywane)
        self.settings_window.window_closed_signal.connect(self.resume_main_timer)

    # --- NOWE METODY KONTROLUJĄCE TIMER ---
    def pause_main_timer(self):
        """Zatrzymuje główny timer odliczający czas pracy."""
        if self.timer.isActive():
            self.timer.stop()
            print("TIMER: Zatrzymany (otwarto okno ustawień).")

    def resume_main_timer(self):
        """Wznawia główny timer odliczający czas pracy."""
        if not self.timer.isActive():
            self.timer.start()
            print("TIMER: Wznowiony (zamknięto okno ustawień).")

    def _start_timer(self):
        """Uruchamia timer."""
        # Używamy resume_main_timer, aby uruchomić timer na starcie aplikacji
        self.resume_main_timer()

    def exit_application(self):
        """Bezpiecznie zamyka aplikację."""
        print("Zamykanie aplikacji...")
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