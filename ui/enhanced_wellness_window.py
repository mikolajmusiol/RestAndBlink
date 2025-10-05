# ui/enhanced_wellness_window_new.py
"""Reorganized enhanced wellness window with modular components."""

import logging
import os
from datetime import datetime, timedelta

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QStackedWidget, QFrame, QGridLayout,
                            QScrollArea, QDesktopWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Import our modular components
from ui.components.ui_scaling import UIScaling
from ui.components.theme_manager import ThemeManager
from ui.components.database_manager import DatabaseManager
from ui.components.chart_widgets import ChartWidgets
from ui.components.stats_widgets import StatsWidgets
from ui.components.achievements_widgets import AchievementsWidgets
from ui.components.camera_calibration import CameraCalibration

# Import existing tabs
from ui.tabs.configure_tab import ConfigureTab

# Setup logging
LOG_PATH = os.path.join(os.path.dirname(__file__), "camera_debug.log")
logging.basicConfig(filename=LOG_PATH, level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger().addHandler(logging.StreamHandler())


class EnhancedWellnessWindow(QMainWindow):
    """Enhanced wellness window with modular architecture."""

    def __init__(self, user_id=1):
        super().__init__()
        self.user_id = user_id
        self.current_section = "main"
        self.current_stats_period = "daily"

        # Initialize components
        self.ui_scaling = UIScaling()
        self.theme_manager = ThemeManager(self.ui_scaling)
        self.database_manager = DatabaseManager()
        self.chart_widgets = ChartWidgets(self.ui_scaling)
        self.stats_widgets = StatsWidgets(self.ui_scaling)
        self.achievements_widgets = AchievementsWidgets(self.ui_scaling)
        self.camera_calibration = CameraCalibration(self.ui_scaling, self.database_manager)

        self.setWindowTitle("Rest&Blink - Enhanced Wellness Dashboard")
        self.setup_window_geometry()
        self.apply_theme()
        
        # Get user data
        self.user_data = self.database_manager.get_user_data(self.user_id)
        
        # Setup UI
        self.setup_ui()

    def setup_window_geometry(self):
        """Setup responsive window geometry."""
        desktop = QDesktopWidget()
        screen_rect = desktop.screenGeometry()

        # Use 85% of screen width and 80% of screen height
        window_width = int(screen_rect.width() * 0.85)
        window_height = int(screen_rect.height() * 0.80)

        # Minimum and maximum sizes with scaling
        min_width = int(1000 * self.ui_scaling.ui_scale)
        min_height = int(700 * self.ui_scaling.ui_scale)
        window_width = max(min_width, min(int(2400 * self.ui_scaling.ui_scale), window_width))
        window_height = max(min_height, min(int(1600 * self.ui_scaling.ui_scale), window_height))

        self.setGeometry(100, 100, window_width, window_height)
        self.setMinimumSize(min_width, min_height)

    def apply_theme(self):
        """Apply the wellness theme."""
        self.setStyleSheet(self.theme_manager.get_wellness_theme_style())

    def setup_ui(self):
        """Setup the main UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, self.ui_scaling.scaled_size(25), 0, 0)
        main_layout.setSpacing(0)
        
        # Top header section
        self.create_header(main_layout)
        
        # Navigation section
        self.create_navigation(main_layout)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #404448; border: none; height: 2px;")
        main_layout.addWidget(separator)
        
        # Content area
        self.create_content_area(main_layout)

    def create_header(self, parent_layout):
        """Create the top header with logo and user info."""
        header_widget = QWidget()
        header_widget.setFixedHeight(self.ui_scaling.scaled_size(110))
        header_widget.setStyleSheet("background-color: #1a1d1f; border-bottom: 1px solid #404448;")
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(
            self.ui_scaling.scaled_size(30), self.ui_scaling.scaled_size(20), 
            self.ui_scaling.scaled_size(30), self.ui_scaling.scaled_size(20)
        )
        
        # Left side - Logo
        logo_label = QLabel("Rest&Blink")
        logo_label.setFont(self.ui_scaling.scaled_font("Segoe UI", 24, QFont.Bold))
        logo_label.setStyleSheet("color: #7cb9e8; border: none;")
        header_layout.addWidget(logo_label)
        
        # Left spacer to center the stats
        header_layout.addStretch(1)

        # Middle - Centered Quick stats cards
        quick_stats_widget = QWidget()
        quick_stats_layout = QHBoxLayout(quick_stats_widget)
        quick_stats_layout.setContentsMargins(0, 0, 0, 0)
        quick_stats_layout.setSpacing(self.ui_scaling.scaled_size(15))

        # Create quick stat cards
        today_card = self.stats_widgets.create_quick_stat_card("Today's Sessions", "8", "#7cb9e8")
        current_streak_card = self.stats_widgets.create_quick_stat_card(
            "Current Streak", f"{self.user_data.get('level', 1)} days", "#90e0ef"
        )
        total_time_card = self.stats_widgets.create_quick_stat_card("Total Time", "12h 15m", "#a8dadc")

        quick_stats_layout.addWidget(today_card)
        quick_stats_layout.addWidget(current_streak_card)
        quick_stats_layout.addWidget(total_time_card)

        header_layout.addWidget(quick_stats_widget)

        # Right spacer to center the stats
        header_layout.addStretch(1)

        # Right side - User info
        user_info_widget = QWidget()
        user_info_layout = QVBoxLayout(user_info_widget)
        user_info_layout.setContentsMargins(0, 0, 0, 0)
        user_info_layout.setSpacing(2)
        
        # User greeting
        greeting = f"Hi, {self.user_data['first_name']} {self.user_data['last_name']}"
        user_label = QLabel(greeting)
        user_label.setFont(self.ui_scaling.scaled_font("Segoe UI", 14, QFont.Medium))
        user_label.setStyleSheet("color: #e8e9ea; border: none;")
        user_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Level info
        level_label = QLabel(f"lv. {self.user_data['level']}")
        level_label.setFont(self.ui_scaling.scaled_font("Segoe UI", 12))
        level_label.setStyleSheet("color: #a8b5c1; border: none;")
        level_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        user_info_layout.addWidget(user_label)
        user_info_layout.addWidget(level_label)
        
        header_layout.addWidget(user_info_widget)
        parent_layout.addWidget(header_widget)

    def create_navigation(self, parent_layout):
        """Create fixed navigation tiles."""
        nav_widget = QWidget()
        nav_widget.setFixedHeight(self.ui_scaling.scaled_size(70))
        nav_widget.setStyleSheet("background-color: #1a1d1f;")
        
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(
            self.ui_scaling.scaled_size(30), self.ui_scaling.scaled_size(15), 
            self.ui_scaling.scaled_size(30), self.ui_scaling.scaled_size(15)
        )
        nav_layout.setSpacing(self.ui_scaling.scaled_size(20))
        
        # Add spacer to center navigation
        nav_layout.addStretch()

        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("main", "Main"),
            ("stats", "Stats"),
            ("configure", "Configure"),
            ("achievements", "Achievements")
        ]

        for nav_id, nav_text in nav_items:
            btn = QPushButton(nav_text)
            btn.setMinimumSize(self.ui_scaling.scaled_size(120), self.ui_scaling.scaled_size(40))
            btn.clicked.connect(lambda checked, nav_id=nav_id: self.switch_section(nav_id))

            self.nav_buttons[nav_id] = btn
            nav_layout.addWidget(btn)
        
        # Add spacer to center navigation
        nav_layout.addStretch()
        
        parent_layout.addWidget(nav_widget)

    def create_content_area(self, parent_layout):
        """Create the main content area."""
        self.content_stack = QStackedWidget()
        
        # Main page
        main_page = self.create_main_page()
        
        # Stats page
        stats_page = self.create_stats_page()
        
        # Configure page
        configure_page = ConfigureTab(parent=self)
        
        # Achievements page
        achievements_page = self.create_achievements_page()
        
        # Add pages to stack
        self.content_stack.addWidget(main_page)        # index 0
        self.content_stack.addWidget(stats_page)       # index 1
        self.content_stack.addWidget(configure_page)   # index 2
        self.content_stack.addWidget(achievements_page) # index 3

        parent_layout.addWidget(self.content_stack)

        # Start with stats section
        self.switch_section("stats")

    def create_main_page(self):
        """Create empty main page."""
        main_page = QWidget()
        main_page.setStyleSheet("background-color: #1a1d1f;")
        main_layout = QVBoxLayout(main_page)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Empty main page - all content moved to header
        main_layout.addStretch()
        
        return main_page

    def create_stats_page(self):
        """Create the stats page with period selection."""
        stats_page = QWidget()
        stats_page.setStyleSheet("background-color: #1a1d1f;")
        
        stats_layout = QVBoxLayout(stats_page)
        stats_layout.setContentsMargins(30, 20, 30, 20)
        stats_layout.setSpacing(20)
        
        # Stats header
        header_container = QWidget()
        header_container.setStyleSheet("border: none; background: transparent;")
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, self.ui_scaling.scaled_size(10))

        # Add stretchers to center the header
        header_layout.addStretch()

        stats_header = QLabel("Stats: Health & Wellness Analytics")
        stats_header.setFont(self.ui_scaling.scaled_font("Segoe UI", 20, QFont.Medium))
        stats_header.setStyleSheet("color: #e8e9ea; border: none; background: transparent;")
        header_layout.addWidget(stats_header)

        header_layout.addStretch()

        stats_layout.addWidget(header_container)
        
        # Period selection buttons
        period_widget = QWidget()
        period_widget.setStyleSheet("border: none; background: transparent;")
        period_layout = QHBoxLayout(period_widget)
        period_layout.setContentsMargins(0, 0, 0, 0)
        period_layout.setSpacing(self.ui_scaling.scaled_size(15))
        
        self.period_buttons = {}
        periods = [
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("alltime", "All Time")
        ]
        
        for period_id, period_text in periods:
            btn = QPushButton(period_text)
            btn.setMinimumSize(120, 45)
            btn.clicked.connect(lambda checked, period_id=period_id: self.switch_stats_period(period_id))
            self.period_buttons[period_id] = btn
            period_layout.addWidget(btn)
        
        # Add stretch to left-align buttons
        period_layout.addStretch()
        
        stats_layout.addWidget(period_widget)
        
        # Stats content area
        self.stats_content_area = QWidget()
        self.stats_content_layout = QVBoxLayout(self.stats_content_area)
        self.stats_content_layout.setContentsMargins(0, 0, 0, 0)
        
        stats_layout.addWidget(self.stats_content_area)
        
        # Set initial period to daily
        self.switch_stats_period("daily")
        
        return stats_page

    def create_achievements_page(self):
        """Create the achievements page with responsive scrollable grid."""
        page = QWidget()
        page.setStyleSheet("background-color: #1a1d1f;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(
            self.ui_scaling.scaled_size(30), self.ui_scaling.scaled_size(30), 
            self.ui_scaling.scaled_size(30), self.ui_scaling.scaled_size(30)
        )

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(self.theme_manager.get_scrollarea_style())

        # Create content widget for scroll area
        content_widget = QWidget()
        self.achievements_layout = QVBoxLayout(content_widget)
        self.achievements_layout.setContentsMargins(0, 0, 0, 0)

        # Create responsive achievements grid
        self.create_responsive_achievements_grid()

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        return page

    def create_responsive_achievements_grid(self):
        """Create a responsive achievements grid."""
        # Get achievements data
        earned_achievements, all_achievements = self.database_manager.get_achievements_data(self.user_id)

        # Create grid widget
        grid_widget = self.achievements_widgets.create_responsive_achievements_grid(
            earned_achievements, all_achievements, self.width()
        )

        self.achievements_layout.addWidget(grid_widget)
        self.achievements_layout.addStretch()

    def create_enhanced_period_content(self, period):
        """Create enhanced content with real charts for a specific period."""
        # Clear existing content
        for i in reversed(range(self.stats_content_layout.count())):
            child = self.stats_content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Get data for this period
        period_data = self.database_manager.get_enhanced_period_data(self.user_id, period)
        db_stats = self.database_manager.get_period_stats(self.user_id, period)
        
        # Create main dashboard
        dashboard_widget = QWidget()
        dashboard_layout = QGridLayout(dashboard_widget)
        dashboard_layout.setSpacing(20)
        dashboard_layout.setContentsMargins(0, 20, 0, 0)
        
        # Left side - Charts
        charts_widget = self.chart_widgets.create_charts_widget(period_data, period)
        
        # Middle - Average stats
        avg_stats_widget = self.stats_widgets.create_avg_stats_widget(period_data, self.ui_scaling)
        
        # Right side - Time & Score
        right_stats_widget = self.stats_widgets.create_right_stats_widget(period_data, period, db_stats)
        
        # Layout components
        dashboard_layout.addWidget(charts_widget, 0, 0, 2, 1)  # Charts on left, span 2 rows
        dashboard_layout.addWidget(avg_stats_widget, 0, 1, 1, 1)  # Top right
        dashboard_layout.addWidget(right_stats_widget, 1, 1, 1, 1)  # Bottom right
        
        # Set column stretch
        dashboard_layout.setColumnStretch(0, 3)  # Charts take more space
        dashboard_layout.setColumnStretch(1, 1)  # Right column
        
        self.stats_content_layout.addWidget(dashboard_widget)
        self.stats_content_layout.addStretch()

    def switch_section(self, section):
        """Switch between main sections."""
        self.current_section = section
        
        # Update button styles
        for nav_id, btn in self.nav_buttons.items():
            if nav_id == section:
                btn.setStyleSheet(self.theme_manager.get_button_active_style())
            else:
                btn.setStyleSheet(self.theme_manager.get_button_inactive_style())
        
        # Switch content
        section_map = {
            "main": 0,
            "stats": 1,
            "configure": 2,
            "achievements": 3
        }
        
        if section in section_map:
            self.content_stack.setCurrentIndex(section_map[section])

    def switch_stats_period(self, period):
        """Switch between stats periods."""
        self.current_stats_period = period
        
        # Update button styles
        for period_id, btn in self.period_buttons.items():
            if period_id == period:
                btn.setStyleSheet(self.theme_manager.get_button_active_style())
            else:
                btn.setStyleSheet(self.theme_manager.get_button_inactive_style())
        
        # Update content for the new period
        self.create_enhanced_period_content(period)


def main():
    """Test the enhanced wellness interface."""
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    window = EnhancedWellnessWindow()
    window.show()
    
    # Start with stats section
    window.switch_section("stats")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()