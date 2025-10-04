# ui/tabs/stats_tab.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from PyQt5.QtCore import Qt


class StatsTab(QWidget):
    """Zakładka do wyświetlania punktów, osiągnięć i statystyk gamifikacji."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(self._setup_layout())

    def _setup_layout(self):
        main_layout = QVBoxLayout()

        # Sekcja Wyników
        main_layout.addWidget(QLabel("<h2>Twój Postęp w Gamifikacji</h2>"))

        grid = QGridLayout()

        # Punkty
        grid.addWidget(QLabel("<b>Punkty:</b>"), 0, 0)
        self.points_label = QLabel("0")
        grid.addWidget(self.points_label, 0, 1)

        # Osiągnięcia
        grid.addWidget(QLabel("<b>Osiągnięcia odblokowane:</b>"), 1, 0)
        self.achievements_label = QLabel("0/10")
        grid.addWidget(self.achievements_label, 1, 1)

        # Czas przerw
        grid.addWidget(QLabel("<b>Łączny czas przerw:</b>"), 2, 0)
        self.total_break_time_label = QLabel("0h 0m")
        grid.addWidget(self.total_break_time_label, 2, 1)

        main_layout.addLayout(grid)
        main_layout.addStretch(1)  # Wypełnienie reszty przestrzeni

        return main_layout

    # Metoda do aktualizacji statystyk (będzie wywoływana z ScoreManager)
    def update_stats(self, points, achievements, total_break_time):
        self.points_label.setText(str(points))
        self.achievements_label.setText(f"{achievements[0]}/{achievements[1]}")
        self.total_break_time_label.setText(total_break_time)