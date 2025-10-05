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
    # NOWY SYGNAŁ: Aktywacja przerwy (kluczem jest kliknięcie w powiadomienie)
    break_activated_signal = pyqtSignal()
    exit_app_signal = pyqtSignal()

    def __init__(self, icon_path, parent=None):
        super().__init__(QIcon(icon_path), parent)

        self.menu = QMenu()
        self.setContextMenu(self.menu)

        # Flaga kontrolująca, czy kliknięcie dymka ma aktywować przerwę
        self._is_break_ready = False

        self._setup_actions()

        # messageClicked będzie wywoływane dla KAŻDEGO dymka,
        # ale teraz użyje flagi _is_break_ready
        self.messageClicked.connect(self._on_message_clicked)
        self.activated.connect(self._handle_tray_activation)

        self.show()

    def _setup_actions(self):
        """Tworzy akcje menu kontekstowego appletu."""

        settings_action = QAction("BreakTimer - Otwórz", self)
        settings_action.triggered.connect(self._emit_show_settings)
        self.menu.addAction(settings_action)

        self.menu.addSeparator()

        exit_action = QAction("Zamknij", self)
        exit_action.triggered.connect(self._emit_exit_application)
        self.menu.addAction(exit_action)

    # --- KLUCZOWE METODY DO OTWIERANIA OKNA ---
    def _handle_tray_activation(self, reason):
        """Obsługuje kliknięcia w ikonę (lewy lub podwójny klik)."""
        # Kliknięcie w ikonę zawsze otwiera okno ustawień/kontroli, nie aktywuje przerwy.
        if reason == QSystemTrayIcon.Trigger:
            self._emit_show_settings()

    def _on_message_clicked(self):
        """Wywoływane po kliknięciu w dymek powiadomienia (Toast)."""
        print("Kliknięto w powiadomienie.")

        if self._is_break_ready:
            print("Aktywuję przerwę (sygnał break_activated_signal).")
            # 1. Emitujemy sygnał, który rozpocznie przerwę w ApplicationController
            self.break_activated_signal.emit()
            # 2. Resetujemy flagę po aktywacji
            self._is_break_ready = False
        else:
            # Dymek nie był sygnałem do rozpoczęcia przerwy (np. powiadomienie o błędzie)
            print("To nie było powiadomienie o przerwie, otwieram okno ustawień.")
            self._emit_show_settings()

    # ---------------------------------------------

    def show_notification(self, title, message):
        """Wyświetla powiadomienie dymkowe z zasobnika (ogólne)."""
        # Używamy tej metody tylko do ogólnych komunikatów, bez aktywacji przerwy.
        self._is_break_ready = False
        self.showMessage(title, message, QSystemTrayIcon.Information, 5000)

    def show_break_reminder(self):
        """
        Wywoływane przez Timer w ApplicationController. Pokazuje powiadomienie Toast
        i USTAWIAMY FLAGĘ, że kliknięcie ma aktywować przerwę.
        """
        # 1. Ustawiamy flagę
        self._is_break_ready = True

        # 2. Pokazujemy powiadomienie
        self.showMessage(
            "CZAS NA PRZERWĘ!",
            "Proszę oderwij się od ekranu! Kliknij, aby rozpocząć 5-minutową przerwę.",
            QSystemTrayIcon.Information,
            15000  # Powiadomienie widoczne przez 15 sekund
        )

    def _emit_show_settings(self):
        self.show_settings_signal.emit()

    def _emit_exit_application(self):
        self.exit_app_signal.emit()