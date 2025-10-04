# ui/main_wellness_window.py

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QStackedWidget, QFrame, QGridLayout,
                            QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
import sqlite3
import os

# Import stat tabs
from ui.tabs.daily_stats_tab import DailyStatsTab
from ui.tabs.weekly_stats_tab import WeeklyStatsTab
from ui.tabs.monthly_stats_tab import MonthlyStatsTab
from ui.tabs.alltime_stats_tab import AlltimeStatsTab


class WellnessMainWindow(QMainWindow):
    """Main wellness application window with bio-hacking aesthetic."""
    
    def __init__(self, user_id=1):
        super().__init__()
        self.user_id = user_id
        self.db_path = "user_data.db"
        self.current_section = "main"
        
        self.setWindowTitle("Rest&Blink - Wellness Dashboard")
        self.setGeometry(100, 100, 1400, 900)
        
        # Apply dark wellness theme
        self.apply_wellness_theme()
        
        # Get user data
        self.user_data = self.get_user_data()
        
        # Setup UI
        self.setup_ui()
        
    def apply_wellness_theme(self):
        """Apply dark bio-hacking wellness theme."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1d1f;
                color: #e8e9ea;
            }
            
            QLabel {
                color: #e8e9ea;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QPushButton {
                background-color: #2c3034;
                border: 1px solid #404448;
                color: #e8e9ea;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #363940;
                border-color: #5a6269;
            }
            
            QPushButton:pressed {
                background-color: #404448;
            }
            
            QPushButton.active {
                background-color: #3d5a80;
                border-color: #5d7ca3;
                color: #ffffff;
            }
            
            QFrame {
                background-color: #262a2d;
                border: 1px solid #404448;
                border-radius: 10px;
            }
            
            QFrame.stats-card {
                background-color: #232629;
                border: 1px solid #3a3f44;
                border-radius: 12px;
                padding: 16px;
            }
            
            QScrollArea {
                background-color: #1a1d1f;
                border: none;
            }
            
            QScrollArea QWidget {
                background-color: #1a1d1f;
            }
        """)
    
    def get_user_data(self):
        """Get user data from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT first_name, last_name, level, total_points, total_sessions
                FROM Users WHERE id = ?
            """, (self.user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'first_name': result[0],
                    'last_name': result[1],
                    'level': result[2],
                    'total_points': result[3],
                    'total_sessions': result[4]
                }
            else:
                return {
                    'first_name': 'User',
                    'last_name': '',
                    'level': 1,
                    'total_points': 0,
                    'total_sessions': 0
                }
        except Exception as e:
            print(f"Error getting user data: {e}")
            return {
                'first_name': 'User',
                'last_name': '',
                'level': 1,
                'total_points': 0,
                'total_sessions': 0
            }
    
    def setup_ui(self):
        """Setup the main UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
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
        header_widget.setFixedHeight(80)
        header_widget.setStyleSheet("background-color: #1a1d1f; border-bottom: 1px solid #404448;")
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(30, 20, 30, 20)
        
        # Left side - Logo
        logo_label = QLabel("Rest&Blink")
        logo_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        logo_label.setStyleSheet("color: #7cb9e8; border: none;")
        header_layout.addWidget(logo_label)
        
        # Spacer
        header_layout.addStretch()
        
        # Right side - User info
        user_info_widget = QWidget()
        user_info_layout = QVBoxLayout(user_info_widget)
        user_info_layout.setContentsMargins(0, 0, 0, 0)
        user_info_layout.setSpacing(2)
        
        # User greeting
        greeting = f"Hi, {self.user_data['first_name']} {self.user_data['last_name']}"
        user_label = QLabel(greeting)
        user_label.setFont(QFont("Segoe UI", 14, QFont.Medium))
        user_label.setStyleSheet("color: #e8e9ea; border: none;")
        user_label.setAlignment(Qt.AlignRight)
        
        # Level info
        level_label = QLabel(f"lv. {self.user_data['level']}")
        level_label.setFont(QFont("Segoe UI", 12))
        level_label.setStyleSheet("color: #a8b5c1; border: none;")
        level_label.setAlignment(Qt.AlignRight)
        
        user_info_layout.addWidget(user_label)
        user_info_layout.addWidget(level_label)
        
        header_layout.addWidget(user_info_widget)
        parent_layout.addWidget(header_widget)
    
    def create_navigation(self, parent_layout):
        """Create navigation tiles."""
        nav_widget = QWidget()
        nav_widget.setFixedHeight(70)
        nav_widget.setStyleSheet("background-color: #1a1d1f;")
        
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(30, 15, 30, 15)
        nav_layout.setSpacing(20)
        
        # Add spacer
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
            btn.setMinimumSize(120, 40)
            btn.clicked.connect(lambda checked, nav_id=nav_id: self.switch_section(nav_id))
            
            if nav_id == self.current_section:
                btn.setProperty("class", "active")
                btn.setStyleSheet(btn.styleSheet() + "QPushButton { background-color: #3d5a80; border-color: #5d7ca3; }")
            
            self.nav_buttons[nav_id] = btn
            nav_layout.addWidget(btn)
        
        # Add spacer
        nav_layout.addStretch()
        
        parent_layout.addWidget(nav_widget)
    
    def create_content_area(self, parent_layout):
        """Create the main content area."""
        self.content_stack = QStackedWidget()
        
        # Main page
        main_page = QWidget()
        main_page.setStyleSheet("background-color: #1a1d1f;")
        main_layout = QVBoxLayout(main_page)
        main_label = QLabel("Main Dashboard - Coming Soon")
        main_label.setAlignment(Qt.AlignCenter)
        main_label.setFont(QFont("Segoe UI", 18))
        main_label.setStyleSheet("color: #a8b5c1; margin: 100px;")
        main_layout.addWidget(main_label)
        
        # Stats page
        stats_page = self.create_stats_page()
        
        # Configure page (placeholder)
        configure_page = QWidget()
        configure_page.setStyleSheet("background-color: #1a1d1f;")
        configure_layout = QVBoxLayout(configure_page)
        configure_label = QLabel("Configuration - Coming Soon")
        configure_label.setAlignment(Qt.AlignCenter)
        configure_label.setFont(QFont("Segoe UI", 18))
        configure_label.setStyleSheet("color: #a8b5c1; margin: 100px;")
        configure_layout.addWidget(configure_label)
        
        # Achievements page (placeholder)
        achievements_page = QWidget()
        achievements_page.setStyleSheet("background-color: #1a1d1f;")
        achievements_layout = QVBoxLayout(achievements_page)
        achievements_label = QLabel("Achievements - Coming Soon")
        achievements_label.setAlignment(Qt.AlignCenter)
        achievements_label.setFont(QFont("Segoe UI", 18))
        achievements_label.setStyleSheet("color: #a8b5c1; margin: 100px;")
        achievements_layout.addWidget(achievements_label)
        
        # Add pages to stack
        self.content_stack.addWidget(main_page)        # index 0
        self.content_stack.addWidget(stats_page)       # index 1
        self.content_stack.addWidget(configure_page)   # index 2
        self.content_stack.addWidget(achievements_page) # index 3
        
        parent_layout.addWidget(self.content_stack)
    
    def create_stats_page(self):
        """Create the stats page with period selection."""
        stats_page = QWidget()
        stats_page.setStyleSheet("background-color: #1a1d1f;")
        
        stats_layout = QVBoxLayout(stats_page)
        stats_layout.setContentsMargins(30, 20, 30, 20)
        stats_layout.setSpacing(20)
        
        # Stats header
        stats_header = QLabel("Stats: Health & Wellness Analytics")
        stats_header.setFont(QFont("Segoe UI", 20, QFont.Medium))
        stats_header.setStyleSheet("color: #e8e9ea; margin-bottom: 10px;")
        stats_layout.addWidget(stats_header)
        
        # Period selection buttons
        period_widget = QWidget()
        period_layout = QHBoxLayout(period_widget)
        period_layout.setContentsMargins(0, 0, 0, 0)
        period_layout.setSpacing(15)
        
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
        self.stats_content_stack = QStackedWidget()
        
        # Create period-specific content
        daily_content = self.create_period_content("daily")
        weekly_content = self.create_period_content("weekly")
        monthly_content = self.create_period_content("monthly")
        alltime_content = self.create_period_content("alltime")
        
        self.stats_content_stack.addWidget(daily_content)   # index 0
        self.stats_content_stack.addWidget(weekly_content)  # index 1
        self.stats_content_stack.addWidget(monthly_content) # index 2
        self.stats_content_stack.addWidget(alltime_content) # index 3
        
        stats_layout.addWidget(self.stats_content_stack)
        
        # Set initial period to daily
        self.current_stats_period = "daily"
        self.switch_stats_period("daily")
        
        return stats_page
    
    def create_period_content(self, period):
        """Create content for a specific period (daily, weekly, monthly, alltime)."""
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #1a1d1f;")
        
        # Main content layout
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 20, 0, 0)
        content_layout.setSpacing(20)
        
        # Create the stats dashboard layout
        dashboard_widget = QWidget()
        dashboard_layout = QGridLayout(dashboard_widget)
        dashboard_layout.setSpacing(20)
        dashboard_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left side - Charts (2 rows)
        charts_widget = QFrame()
        charts_widget.setProperty("class", "stats-card")
        charts_widget.setMinimumHeight(500)
        charts_layout = QVBoxLayout(charts_widget)
        charts_layout.setContentsMargins(20, 20, 20, 20)
        
        # Heartbeat chart placeholder
        heartbeat_label = QLabel("Heartbeat Chart")
        heartbeat_label.setFont(QFont("Segoe UI", 14, QFont.Medium))
        heartbeat_label.setStyleSheet("color: #7cb9e8; margin-bottom: 10px;")
        
        heartbeat_chart = QFrame()
        heartbeat_chart.setMinimumHeight(200)
        heartbeat_chart.setStyleSheet("background-color: #1a1d1f; border: 1px solid #404448; border-radius: 8px;")
        heartbeat_chart_layout = QVBoxLayout(heartbeat_chart)
        heartbeat_placeholder = QLabel("Heartbeat visualization will be here")
        heartbeat_placeholder.setAlignment(Qt.AlignCenter)
        heartbeat_placeholder.setStyleSheet("color: #a8b5c1; font-size: 12px;")
        heartbeat_chart_layout.addWidget(heartbeat_placeholder)
        
        # Stress chart placeholder
        stress_label = QLabel("Stress Level Chart")
        stress_label.setFont(QFont("Segoe UI", 14, QFont.Medium))
        stress_label.setStyleSheet("color: #f4a261; margin-bottom: 10px; margin-top: 20px;")
        
        stress_chart = QFrame()
        stress_chart.setMinimumHeight(200)
        stress_chart.setStyleSheet("background-color: #1a1d1f; border: 1px solid #404448; border-radius: 8px;")
        stress_chart_layout = QVBoxLayout(stress_chart)
        stress_placeholder = QLabel("Stress level visualization will be here")
        stress_placeholder.setAlignment(Qt.AlignCenter)
        stress_placeholder.setStyleSheet("color: #a8b5c1; font-size: 12px;")
        stress_chart_layout.addWidget(stress_placeholder)
        
        charts_layout.addWidget(heartbeat_label)
        charts_layout.addWidget(heartbeat_chart)
        charts_layout.addWidget(stress_label)
        charts_layout.addWidget(stress_chart)
        
        # Middle - Average stats
        avg_stats_widget = QFrame()
        avg_stats_widget.setProperty("class", "stats-card")
        avg_stats_widget.setMaximumWidth(250)
        avg_stats_layout = QVBoxLayout(avg_stats_widget)
        avg_stats_layout.setContentsMargins(20, 20, 20, 20)
        avg_stats_layout.setSpacing(30)
        
        # Average heartbeat
        avg_hb_widget = QWidget()
        avg_hb_layout = QVBoxLayout(avg_hb_widget)
        avg_hb_layout.setContentsMargins(0, 0, 0, 0)
        avg_hb_layout.setSpacing(10)
        
        avg_hb_label = QLabel("Average Heartbeat")
        avg_hb_label.setFont(QFont("Segoe UI", 14, QFont.Medium))
        avg_hb_label.setStyleSheet("color: #7cb9e8;")
        
        # Get actual data for this period
        stats_data = self.get_period_stats(period)
        
        avg_hb_value = QLabel(f"{stats_data['avg_heartbeat']:.1f} BPM")
        avg_hb_value.setFont(QFont("Segoe UI", 24, QFont.Bold))
        avg_hb_value.setStyleSheet("color: #e8e9ea;")
        
        avg_hb_range = QLabel(f"{stats_data['min_heartbeat']:.0f}/{stats_data['max_heartbeat']:.0f}")
        avg_hb_range.setFont(QFont("Segoe UI", 12))
        avg_hb_range.setStyleSheet("color: #a8b5c1;")
        avg_hb_range.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        
        avg_hb_layout.addWidget(avg_hb_label)
        avg_hb_layout.addWidget(avg_hb_value)
        avg_hb_layout.addStretch()
        avg_hb_layout.addWidget(avg_hb_range)
        
        # Average stress
        avg_stress_widget = QWidget()
        avg_stress_layout = QVBoxLayout(avg_stress_widget)
        avg_stress_layout.setContentsMargins(0, 0, 0, 0)
        avg_stress_layout.setSpacing(10)
        
        avg_stress_label = QLabel("Average Stress")
        avg_stress_label.setFont(QFont("Segoe UI", 14, QFont.Medium))
        avg_stress_label.setStyleSheet("color: #f4a261;")
        
        avg_stress_value = QLabel(f"{stats_data['avg_stress']:.3f}")
        avg_stress_value.setFont(QFont("Segoe UI", 24, QFont.Bold))
        avg_stress_value.setStyleSheet("color: #e8e9ea;")
        
        avg_stress_range = QLabel(f"{stats_data['min_stress']:.2f}/{stats_data['max_stress']:.2f}")
        avg_stress_range.setFont(QFont("Segoe UI", 12))
        avg_stress_range.setStyleSheet("color: #a8b5c1;")
        avg_stress_range.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        
        avg_stress_layout.addWidget(avg_stress_label)
        avg_stress_layout.addWidget(avg_stress_value)
        avg_stress_layout.addStretch()
        avg_stress_layout.addWidget(avg_stress_range)
        
        avg_stats_layout.addWidget(avg_hb_widget)
        avg_stats_layout.addWidget(avg_stress_widget)
        avg_stats_layout.addStretch()
        
        # Right side - Time & Score
        right_stats_widget = QFrame()
        right_stats_widget.setProperty("class", "stats-card")
        right_stats_widget.setMaximumWidth(250)
        right_stats_layout = QVBoxLayout(right_stats_widget)
        right_stats_layout.setContentsMargins(20, 20, 20, 20)
        right_stats_layout.setSpacing(30)
        
        # Rest time
        rest_time_widget = QWidget()
        rest_time_layout = QVBoxLayout(rest_time_widget)
        rest_time_layout.setContentsMargins(0, 0, 0, 0)
        rest_time_layout.setSpacing(10)
        
        rest_time_label = QLabel("Rest in min")
        rest_time_label.setFont(QFont("Segoe UI", 14, QFont.Medium))
        rest_time_label.setStyleSheet("color: #90e0ef;")
        
        rest_minutes = stats_data['total_time'] / 60
        rest_time_value = QLabel(f"{rest_minutes:.0f} min")
        rest_time_value.setFont(QFont("Segoe UI", 24, QFont.Bold))
        rest_time_value.setStyleSheet("color: #e8e9ea;")
        
        rest_time_layout.addWidget(rest_time_label)
        rest_time_layout.addWidget(rest_time_value)
        rest_time_layout.addStretch()
        
        # Score
        score_widget = QWidget()
        score_layout = QVBoxLayout(score_widget)
        score_layout.setContentsMargins(0, 0, 0, 0)
        score_layout.setSpacing(10)
        
        period_names = {
            'daily': 'Today Score',
            'weekly': 'Weekly Score', 
            'monthly': 'Monthly Score',
            'alltime': 'All Time Score'
        }
        
        score_label = QLabel(period_names.get(period, 'Score'))
        score_label.setFont(QFont("Segoe UI", 14, QFont.Medium))
        score_label.setStyleSheet("color: #a8dadc;")
        
        score_value = QLabel(f"{stats_data['total_score']:.0f}")
        score_value.setFont(QFont("Segoe UI", 24, QFont.Bold))
        score_value.setStyleSheet("color: #e8e9ea;")
        
        score_layout.addWidget(score_label)
        score_layout.addWidget(score_value)
        score_layout.addStretch()
        
        # Improve note placeholder
        improve_note = QLabel("Improve note")
        improve_note.setFont(QFont("Segoe UI", 12))
        improve_note.setStyleSheet("color: #a8b5c1;")
        improve_note.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        
        right_stats_layout.addWidget(rest_time_widget)
        right_stats_layout.addWidget(score_widget)
        right_stats_layout.addStretch()
        right_stats_layout.addWidget(improve_note)
        
        # Add to grid layout
        dashboard_layout.addWidget(charts_widget, 0, 0, 2, 1)  # Charts span 2 rows, 1 column
        dashboard_layout.addWidget(avg_stats_widget, 0, 1, 1, 1)  # Top middle
        dashboard_layout.addWidget(right_stats_widget, 0, 2, 1, 1)  # Top right
        
        # Set column stretch
        dashboard_layout.setColumnStretch(0, 3)  # Charts take more space
        dashboard_layout.setColumnStretch(1, 1)  # Average stats
        dashboard_layout.setColumnStretch(2, 1)  # Right stats
        
        content_layout.addWidget(dashboard_widget)
        content_layout.addStretch()
        
        return content_widget
    
    def get_period_stats(self, period):
        """Get statistics for a specific period."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Define date ranges
            from datetime import datetime, timedelta
            today = datetime.now()
            
            if period == "daily":
                start_date = today.strftime('%Y-%m-%d')
                end_date = start_date
            elif period == "weekly":
                start_of_week = today - timedelta(days=today.weekday())
                start_date = start_of_week.strftime('%Y-%m-%d')
                end_date = (start_of_week + timedelta(days=6)).strftime('%Y-%m-%d')
            elif period == "monthly":
                start_date = today.replace(day=1).strftime('%Y-%m-%d')
                end_date = today.strftime('%Y-%m-%d')
            else:  # alltime
                start_date = "2000-01-01"
                end_date = today.strftime('%Y-%m-%d')
            
            # Get stats for period
            cursor.execute("""
                SELECT AVG(avg_heartbeat), MIN(avg_heartbeat), MAX(avg_heartbeat),
                       AVG(stress_level), MIN(stress_level), MAX(stress_level),
                       SUM(total_time_seconds), SUM(score)
                FROM Sessions 
                WHERE user_id = ? AND DATE(timestamp) BETWEEN ? AND ?
                AND avg_heartbeat > 0
            """, (self.user_id, start_date, end_date))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return {
                    'avg_heartbeat': result[0],
                    'min_heartbeat': result[1],
                    'max_heartbeat': result[2], 
                    'avg_stress': result[3],
                    'min_stress': result[4],
                    'max_stress': result[5],
                    'total_time': result[6] or 0,
                    'total_score': result[7] or 0
                }
            else:
                return {
                    'avg_heartbeat': 0,
                    'min_heartbeat': 0,
                    'max_heartbeat': 0,
                    'avg_stress': 0,
                    'min_stress': 0,
                    'max_stress': 0,
                    'total_time': 0,
                    'total_score': 0
                }
        except Exception as e:
            print(f"Error getting period stats: {e}")
            return {
                'avg_heartbeat': 0,
                'min_heartbeat': 0,
                'max_heartbeat': 0,
                'avg_stress': 0,
                'min_stress': 0,
                'max_stress': 0,
                'total_time': 0,
                'total_score': 0
            }
    
    def switch_section(self, section):
        """Switch between main sections."""
        self.current_section = section
        
        # Update button styles
        for nav_id, btn in self.nav_buttons.items():
            if nav_id == section:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3d5a80;
                        border-color: #5d7ca3;
                        color: #ffffff;
                        padding: 12px 24px;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: 500;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2c3034;
                        border: 1px solid #404448;
                        color: #e8e9ea;
                        padding: 12px 24px;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background-color: #363940;
                        border-color: #5a6269;
                    }
                """)
        
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
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3d5a80;
                        border-color: #5d7ca3;
                        color: #ffffff;
                        padding: 12px 24px;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: 500;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2c3034;
                        border: 1px solid #404448;
                        color: #e8e9ea;
                        padding: 12px 24px;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background-color: #363940;
                        border-color: #5a6269;
                    }
                """)
        
        # Switch stats content
        period_map = {
            "daily": 0,
            "weekly": 1,
            "monthly": 2,
            "alltime": 3
        }
        
        if period in period_map:
            self.stats_content_stack.setCurrentIndex(period_map[period])


# Test the new interface
def main():
    """Test the new wellness interface."""
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    window = WellnessMainWindow()
    window.show()
    
    # Start with stats section
    window.switch_section("stats")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()