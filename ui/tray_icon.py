# ui/tray_icon.py

from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal


class BreakReminderTrayIcon(QSystemTrayIcon):
    """
    Główna klasa dla ikony w zasobniku systemowym (applet).
    """

    # Sygnały emitowane do ApplicationController
    show_settings_signal = pyqtSignal()
    exit_app_signal = pyqtSignal()

    def __init__(self, icon_path, parent=None):
        super().__init__(QIcon(icon_path), parent)

        self.menu = QMenu()
        self.setContextMenu(self.menu)

        self._setup_actions()

        # Upewniamy się, że slot messageClicked jest połączony, aby reagować na kliknięcia powiadomień
        self.messageClicked.connect(self._on_message_clicked)
        self.activated.connect(self._handle_tray_activation)

        self.show()

    def _setup_actions(self):
        """Tworzy akcje menu kontekstowego appletu."""

        settings_action = QAction("BreakTimer", self)
        settings_action.triggered.connect(self._emit_show_settings)
        self.menu.addAction(settings_action)

        self.menu.addSeparator()

        exit_action = QAction("Zamknij", self)
        exit_action.triggered.connect(self._emit_exit_application)
        self.menu.addAction(exit_action)

    # --- KLUCZOWE METODY DO OTWIERANIA OKNA ---
    def _handle_tray_activation(self, reason):
        """Obsługuje kliknięcia w ikonę (lewy lub podwójny klik)."""
        if reason == QSystemTrayIcon.Trigger:
            self._emit_show_settings()

    def _on_message_clicked(self):
        """Wywoływane po kliknięciu w dymek powiadomienia (Toast)."""
        print("Kliknięto w powiadomienie. Otwieram okno...")
        self._emit_show_settings()

    # ---------------------------------------------

    def show_notification(self, title, message):
        """Wyświetla powiadomienie dymkowe z zasobnika."""
        self.showMessage(title, message, QSystemTrayIcon.Information, 5000)

    def show_break_reminder(self):
        """Wywoływane przez Timer. Pokazuje powiadomienie Toast."""
        self.show_notification("CZAS NA PRZERWĘ!", "Proszę oderwij się od ekranu!")

    def _emit_show_settings(self):
        self.show_settings_signal.emit()

    def _emit_exit_application(self):
        self.exit_app_signal.emit()