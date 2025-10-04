#!/usr/bin/env python3
# Test script for statistics tabs

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from PyQt5.QtWidgets import QApplication, QTabWidget, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

# Import the new statistics tabs
from ui.tabs.daily_stats_tab import DailyStatsTab
from ui.tabs.weekly_stats_tab import WeeklyStatsTab
from ui.tabs.monthly_stats_tab import MonthlyStatsTab
from ui.tabs.alltime_stats_tab import AlltimeStatsTab


class StatsTabsTestApp(QWidget):
    """Test application for statistics tabs."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Test Statystyk')
        self.setGeometry(100, 100, 1200, 800)
        
        layout = QVBoxLayout()
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Add statistics tabs
        try:
            daily_tab = DailyStatsTab()
            tab_widget.addTab(daily_tab, "Dzisiaj")
            print("✓ Daily stats tab loaded successfully")
        except Exception as e:
            print(f"✗ Error loading daily stats tab: {e}")
        
        try:
            weekly_tab = WeeklyStatsTab()
            tab_widget.addTab(weekly_tab, "Tydzień")
            print("✓ Weekly stats tab loaded successfully")
        except Exception as e:
            print(f"✗ Error loading weekly stats tab: {e}")
        
        try:
            monthly_tab = MonthlyStatsTab()
            tab_widget.addTab(monthly_tab, "Miesiąc")
            print("✓ Monthly stats tab loaded successfully")
        except Exception as e:
            print(f"✗ Error loading monthly stats tab: {e}")
        
        try:
            alltime_tab = AlltimeStatsTab()
            tab_widget.addTab(alltime_tab, "Wszystkie czasy")
            print("✓ All-time stats tab loaded successfully")
        except Exception as e:
            print(f"✗ Error loading all-time stats tab: {e}")
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Check if database exists
    if not os.path.exists('user_data.db'):
        print("⚠️  Warning: user_data.db not found. Some features may not work properly.")
    
    window = StatsTabsTestApp()
    window.show()
    
    print("\n🚀 Statistics tabs test application started")
    print("   Check each tab to verify the statistics are displayed correctly")
    
    sys.exit(app.exec_())