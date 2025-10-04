# main.py

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QCoreApplication

# Importuj moduły, które stworzymy
from ui.tray_icon import BreakReminderTrayIcon


# from core.timer import BreakTimer  # Docelowo odkomentujesz
# from ui.main_window import SettingsWindow # Docelowo odkomentujesz

class ApplicationController:
    """
    Główny kontroler łączący logikę (Timer) z UI (TrayIcon).
    """

    def __init__(self):
        # Używamy QCoreApplication.instance() lub tworzymy nową, jeśli nie istnieje
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # Aplikacja nie zamyka się po zamknięciu okna

        # UWAGA: Użyj ścieżki do swojej ikony (np. resources/icons/tray_icon.png)
        # Zastąp poniższy string poprawną ścieżką do PNG/ICO
        self.ICON_PATH = "resources/icons/flower-2.svg"

        # 1. Inicjalizacja komponentów
        self._initialize_components()

        # 2. Uruchomienie Timera
        self._start_timer()

    def _initialize_components(self):
        """Tworzy instancje UI i Logiki."""

        # UI: Applet w zasobniku
        self.tray_icon = BreakReminderTrayIcon(self.ICON_PATH)

        # LOGIKA: Timer (NA RAZIE UŻYJEMY QTimer DO DEMONSTRACJI)
        self.timer = QTimer()
        self.timer.setInterval(30000)  # 30 sekund na potrzeby testu (docelowo: 1200000ms = 20 min)

        # WINDOWS: Okno Ustawień (Docelowo)
        # self.settings_window = SettingsWindow()

        # 3. Łączenie sygnałów
        self._connect_signals()

    def _connect_signals(self):
        """Łączy sygnały pomiędzy komponentami."""

        # Połączenie sygnału z Appletu do logiki wyjścia
        self.tray_icon.exit_app_signal.connect(self.exit_application)

        # Połączenie sygnału z Appletu do pokazania ustawień/statystyk
        # self.tray_icon.show_settings_signal.connect(self.settings_window.show) # Docelowo
        self.tray_icon.show_settings_signal.connect(lambda: print("Otwórz okno ustawień/statystyk!"))

        # Połączenie Timera do metody w Applet'cie, która wyświetli powiadomienie
        self.timer.timeout.connect(self.tray_icon.show_break_reminder)

    def _start_timer(self):
        """Uruchamia timer."""
        self.timer.start()
        print(f"Aplikacja uruchomiona. Przerwa za {self.timer.interval() / 1000} sekund (TESTOWO).")

    def exit_application(self):
        """Bezpiecznie zamyka aplikację."""
        print("Zamykanie aplikacji...")
        # Ukryj ikonę przed zamknięciem
        self.tray_icon.hide()
        QCoreApplication.quit()
        # sys.exit(0) # Alternatywna metoda

    def run(self):
        """Uruchamia pętlę zdarzeń aplikacji."""
        # Wymagane, aby aplikacja działała
        return self.app.exec_()


if __name__ == '__main__':
    # Ważne: Stwórz katalog 'resources/icons' i umieść tam 'tray_icon.png' przed uruchomieniem
    try:
        controller = ApplicationController()
        sys.exit(controller.run())
    except FileNotFoundError as e:
        print(f"BŁĄD: Upewnij się, że plik ikony istnieje pod ścieżką: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")
        sys.exit(1)