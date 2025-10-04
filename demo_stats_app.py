#!/usr/bin/env python3
# Demo script to showcase all statistics tabs

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from ui.main_window import SettingsStatsWindow


def main():
    """Run the main application with all statistics tabs."""
    app = QApplication(sys.argv)
    
    # Create main window
    icon_path = 'resources/icons/app-icon.svg'
    window = SettingsStatsWindow(icon_path)
    
    # Show the window
    window.show()
    
    print("🚀 Break Reminder aplikacja uruchomiona!")
    print("\n📊 Dostępne zakładki statystyk:")
    print("   • Statystyki i Punkty - podstawowe statystyki gamifikacji")
    print("   • Dzisiaj - szczegółowe statystyki dzienne z wykresami seaborn")
    print("   • Tydzień - analiza tygodniowa z trendami")
    print("   • Miesiąc - przegląd miesięczny z mapami wydajności")
    print("   • Wszystkie czasy - kompletna analiza historyczna")
    print("\n💡 Każda zakładka zawiera:")
    print("   • Statystyki liczbowe")
    print("   • Wykresy w seaborn (bez kolorów, gotowe na stylizację)")
    print("   • Dane z bazy user_data.db")
    print("   • Responsywny interfejs z przewijaniem")
    
    # Check database
    if os.path.exists('user_data.db'):
        print("\n✅ Baza danych user_data.db znaleziona")
    else:
        print("\n⚠️  Ostrzeżenie: user_data.db nie znaleziona - niektóre funkcje mogą nie działać")
    
    # Run the application
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()