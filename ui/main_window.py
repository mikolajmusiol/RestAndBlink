# ui/main_window.py (Zaktualizowany)

from PyQt5.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal
import os

# Importujemy poszczególne zakładki
from ui.tabs.main_tab import MainTab
from ui.tabs.stats_tab import StatsTab
from ui.tabs.daily_stats_tab import DailyStatsTab
from ui.tabs.weekly_stats_tab import WeeklyStatsTab
from ui.tabs.monthly_stats_tab import MonthlyStatsTab
from ui.tabs.alltime_stats_tab import AlltimeStatsTab


# Tutaj możesz łatwo importować nowe zakładki!

class SettingsStatsWindow(QMainWindow):
    """
    Główne okno aplikacji oparte na QTabWidget.
    """
    window_opened_signal = pyqtSignal()
    window_closed_signal = pyqtSignal()

    def __init__(self, icon_path):
        super().__init__()
        self.setWindowTitle("Break Reminder")
        self.setGeometry(500, 500, 800, 500)

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)  # Zakładki na górze

        self._load_tabs()  # Metoda odpowiedzialna za ładowanie wszystkich zakładek

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.tab_widget)
        self.setCentralWidget(central_widget)

    def _load_tabs(self):
        """Dynamicznie ładuje wszystkie zakładki do QTabWidget."""

        # 1. Zakładka Głównego Timera i Kontroli
        self.main_timer_tab = MainTab()
        self.tab_widget.addTab(self.main_timer_tab, "Główny Timer")

        # 2. Zakładka Statystyk i Gamifikacji (podstawowa)
        self.stats_tab = StatsTab()
        self.tab_widget.addTab(self.stats_tab, "Statystyki i Punkty")

        # 3. Szczegółowe statystyki dzienne
        self.daily_stats_tab = DailyStatsTab()
        self.tab_widget.addTab(self.daily_stats_tab, "Dzisiaj")

        # 4. Szczegółowe statystyki tygodniowe
        self.weekly_stats_tab = WeeklyStatsTab()
        self.tab_widget.addTab(self.weekly_stats_tab, "Tydzień")

        # 5. Szczegółowe statystyki miesięczne
        self.monthly_stats_tab = MonthlyStatsTab()
        self.tab_widget.addTab(self.monthly_stats_tab, "Miesiąc")

        # 6. Szczegółowe statystyki za wszystkie czasy
        self.alltime_stats_tab = AlltimeStatsTab()
        self.tab_widget.addTab(self.alltime_stats_tab, "Wszystkie czasy")

        # 7. Przyszłe zakładki (np. Ustawienia, Ćwiczenia)
        # self.tab_widget.addTab(NowaZakladka(), "Nowa Nazwa")

        # W tym miejscu możesz również połączyć sygnały z zakładek do kontrolera
        # self.main_timer_tab.start_timer_request.connect(...)

    def showEvent(self, event):
        """Emituje sygnał po otwarciu okna."""
        super().showEvent(event)
        self.window_opened_signal.emit()

    def closeEvent(self, event):
        """Ukrywa okno i emituje sygnał zamknięcia."""
        self.hide()
        event.ignore()
        self.window_closed_signal.emit()