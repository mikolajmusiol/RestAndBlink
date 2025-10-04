# ui/tray_icon.py

from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QAction, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QCoreApplication


class BreakReminderTrayIcon(QSystemTrayIcon):
    """
    Główna klasa dla ikony w zasobniku systemowym (applet).
    """

    # Sygnały do komunikacji z główną aplikacją
    show_settings_signal = pyqtSignal()
    exit_app_signal = pyqtSignal()

    def __init__(self, icon_path, parent=None):
        super().__init__(QIcon(icon_path), parent)

        self.menu = QMenu()
        self.setContextMenu(self.menu)

        self._setup_actions()

        # Domyślnie pokaż ikonę po stworzeniu
        self.show()

    def _setup_actions(self):
        """Tworzy akcje menu kontekstowego appletu."""

        # 1. Akcja Ustawienia/Statystyki (Gamifikacja)
        settings_action = QAction("Statystyki & Ustawienia", self)
        settings_action.triggered.connect(self._show_settings)
        self.menu.addAction(settings_action)

        self.menu.addSeparator()

        # 2. Akcja Zamknij Aplikację
        exit_action = QAction("Zamknij", self)
        exit_action.triggered.connect(self._exit_application)
        self.menu.addAction(exit_action)

        # Reakcja na kliknięcie ikony (np. otwórz okno statystyk)
        self.activated.connect(self.handle_tray_activation)

    def handle_tray_activation(self, reason):
        """Obsługuje kliknięcia/aktywacje ikony w zasobniku."""
        # QSystemTrayIcon.Trigger oznacza kliknięcie lewym lub prawym przyciskiem
        if reason == QSystemTrayIcon.Trigger:
            # Możemy tu np. pokazać okno statystyk
            self.show_settings_signal.emit()

    def show_notification(self, title, message):
        """Wyświetla powiadomienie dymkowe z zasobnika."""
        self.showMessage(title, message, QSystemTrayIcon.Information, 5000)

    # Slot reagujący na sygnał od timera (NASTĄPI W MODUŁACH CORE!)
    def show_break_reminder(self):
        """Metoda, która powinna wywołać 'break_dialog.py'"""
        self.show_notification("CZAS NA PRZERWĘ!", "Proszę oderwij się od ekranu i wstań na chwilę.")

    # Emitery sygnałów
    def _show_settings(self):
        self.show_settings_signal.emit()

    def _exit_application(self):
        # Wysyła sygnał do main.py, aby zamknąć całą aplikację
        self.exit_app_signal.emit()

# --- PRZYKŁADOWY KOD TESTUJĄCY ---
# If you uncomment the below block and run this file directly,
# it will test the Tray Icon functionality.
# if __name__ == '__main__':
#     app = QApplication([])
#
#     # Uwaga: Musisz podać ścieżkę do istniejącego pliku ikony!
#     # Poniżej używamy ścieżki do domyślnej ikony (może nie działać na wszystkich systemach)
#     # LUB użyj 'resources/icons/tray_icon.png' jeśli go stworzysz
#     try:
#         tray_icon = BreakReminderTrayIcon(':/qt-project.org/qmessagebox/images/information.png')
#     except Exception:
#         print("Błąd: Użyj własnej ikony, np. 'app_icon.png'.")
#
#     tray_icon.show_notification("Test", "Applet działa!")
#     app.exec_()