# ui/enhanced_wellness_window.py

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QStackedWidget, QFrame, QGridLayout,
                            QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
import sqlite3
import os
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Import matplotlib for charts
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class EnhancedWellnessWindow(QMainWindow):
    """Enhanced wellness window with integrated charts."""
    
    def __init__(self, user_id=1):
        super().__init__()
        self.user_id = user_id
        self.db_path = "user_data.db"
        self.current_section = "main"
        self.current_stats_period = "daily"
        
        self.setWindowTitle("Rest&Blink - Enhanced Wellness Dashboard")
        self.setGeometry(100, 100, 1600, 1000)
        
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
        
        # Separator line (20% from top)
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
            
            self.nav_buttons[nav_id] = btn
            nav_layout.addWidget(btn)
        
        # Add spacer
        nav_layout.addStretch()
        
        parent_layout.addWidget(nav_widget)
    
    def create_content_area(self, parent_layout):
        """Create the main content area."""
        self.content_stack = QStackedWidget()
        
        # Main page
        main_page = self.create_main_page()
        
        # Stats page
        stats_page = self.create_stats_page()
        
        # Configure page (placeholder)
        configure_page = self.create_placeholder_page("Configuration", "Settings and preferences coming soon")
        
        # Achievements page (placeholder)
        achievements_page = self.create_placeholder_page("Achievements", "Achievement system coming soon")
        
        # Add pages to stack
        self.content_stack.addWidget(main_page)        # index 0
        self.content_stack.addWidget(stats_page)       # index 1
        self.content_stack.addWidget(configure_page)   # index 2
        self.content_stack.addWidget(achievements_page) # index 3
        
        parent_layout.addWidget(self.content_stack)
        
        # Start with stats section
        self.switch_section("stats")
    
    def create_main_page(self):
        """Create the main dashboard page."""
        main_page = QWidget()
        main_page.setStyleSheet("background-color: #1a1d1f;")
        main_layout = QVBoxLayout(main_page)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Main dashboard content
        dashboard_label = QLabel("Main Dashboard")
        dashboard_label.setFont(QFont("Segoe UI", 24, QFont.Medium))
        dashboard_label.setStyleSheet("color: #e8e9ea; margin-bottom: 20px;")
        main_layout.addWidget(dashboard_label)
        
        # Quick stats cards
        quick_stats_widget = QWidget()
        quick_stats_layout = QHBoxLayout(quick_stats_widget)
        quick_stats_layout.setSpacing(20)
        
        # Today's sessions card
        today_card = self.create_quick_stat_card("Today's Sessions", "8", "#7cb9e8")
        current_streak_card = self.create_quick_stat_card("Current Streak", f"{self.user_data.get('level', 1)} days", "#90e0ef")
        total_time_card = self.create_quick_stat_card("Total Time", "12h 15m", "#a8dadc")
        
        quick_stats_layout.addWidget(today_card)
        quick_stats_layout.addWidget(current_streak_card)
        quick_stats_layout.addWidget(total_time_card)
        quick_stats_layout.addStretch()
        
        main_layout.addWidget(quick_stats_widget)
        main_layout.addStretch()
        
        return main_page
    
    def create_placeholder_page(self, title, description):
        """Create a placeholder page."""
        page = QWidget()
        page.setStyleSheet("background-color: #1a1d1f;")
        layout = QVBoxLayout(page)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 24, QFont.Medium))
        title_label.setStyleSheet("color: #e8e9ea; margin: 50px;")
        
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(QFont("Segoe UI", 14))
        desc_label.setStyleSheet("color: #a8b5c1; margin-bottom: 100px;")
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addStretch()
        
        return page
    
    def create_quick_stat_card(self, title, value, color):
        """Create a quick stat card for the main page."""
        card = QFrame()
        card.setProperty("class", "stats-card")
        card.setMinimumSize(200, 120)
        card.setMaximumSize(250, 120)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Medium))  
        title_label.setStyleSheet(f"color: {color};")
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        value_label.setStyleSheet("color: #e8e9ea;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()
        
        return card
    
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
        self.stats_content_area = QWidget()
        self.stats_content_layout = QVBoxLayout(self.stats_content_area)
        self.stats_content_layout.setContentsMargins(0, 0, 0, 0)
        
        stats_layout.addWidget(self.stats_content_area)
        
        # Set initial period to daily
        self.switch_stats_period("daily")
        
        return stats_page
    
    def create_enhanced_period_content(self, period):
        """Create enhanced content with real charts for a specific period."""
        # Clear existing content
        for i in reversed(range(self.stats_content_layout.count())):
            child = self.stats_content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Get data for this period
        period_data = self.get_enhanced_period_data(period)
        
        # Create main dashboard
        dashboard_widget = QWidget()
        dashboard_layout = QGridLayout(dashboard_widget)
        dashboard_layout.setSpacing(20)
        dashboard_layout.setContentsMargins(0, 20, 0, 0)
        
        # Left side - Charts
        charts_widget = self.create_charts_widget(period_data, period)
        
        # Middle - Average stats
        avg_stats_widget = self.create_avg_stats_widget(period_data)
        
        # Right side - Time & Score
        right_stats_widget = self.create_right_stats_widget(period_data, period)
        
        # Add to grid layout
        dashboard_layout.addWidget(charts_widget, 0, 0, 2, 1)  # Charts span 2 rows, 1 column
        dashboard_layout.addWidget(avg_stats_widget, 0, 1, 1, 1)  # Top middle
        dashboard_layout.addWidget(right_stats_widget, 0, 2, 1, 1)  # Top right
        
        # Set column stretch
        dashboard_layout.setColumnStretch(0, 3)  # Charts take more space
        dashboard_layout.setColumnStretch(1, 1)  # Average stats
        dashboard_layout.setColumnStretch(2, 1)  # Right stats
        
        self.stats_content_layout.addWidget(dashboard_widget)
        self.stats_content_layout.addStretch()
    
    def create_charts_widget(self, data, period):
        """Create the charts widget with real heartbeat and stress data."""
        charts_widget = QFrame()
        charts_widget.setProperty("class", "stats-card")
        charts_widget.setMinimumHeight(500)
        charts_layout = QVBoxLayout(charts_widget)
        charts_layout.setContentsMargins(20, 20, 20, 20)
        
        if data and len(data) > 0:
            # Create matplotlib figure
            fig = Figure(figsize=(8, 6), facecolor='#232629')
            
            # Heartbeat chart
            ax1 = fig.add_subplot(2, 1, 1)
            
            if 'heartbeat' in data[0]:
                timestamps = list(range(len(data)))
                heartbeats = [d['heartbeat'] for d in data]
                
                ax1.plot(timestamps, heartbeats, color='#7cb9e8', linewidth=2)
                ax1.set_title('Heartbeat', color='#e8e9ea', fontsize=14, pad=20)
                ax1.set_ylabel('BPM', color='#a8b5c1')
                ax1.tick_params(colors='#a8b5c1')
                ax1.grid(True, alpha=0.3, color='#404448')
                ax1.set_facecolor('#1a1d1f')
            
            # Stress chart
            ax2 = fig.add_subplot(2, 1, 2)
            
            if 'stress' in data[0]:
                stress_levels = [d['stress'] for d in data]
                
                ax2.plot(timestamps, stress_levels, color='#f4a261', linewidth=2)
                ax2.set_title('Stress Level', color='#e8e9ea', fontsize=14, pad=20)
                ax2.set_ylabel('Level', color='#a8b5c1')
                ax2.set_xlabel('Time', color='#a8b5c1')
                ax2.tick_params(colors='#a8b5c1')
                ax2.grid(True, alpha=0.3, color='#404448')
                ax2.set_facecolor('#1a1d1f')
            
            fig.tight_layout()
            
            # Create canvas and add to layout
            canvas = FigureCanvas(fig)
            canvas.setStyleSheet("background-color: #232629;")
            charts_layout.addWidget(canvas)
        
        else:
            # Placeholder for no data
            no_data_label = QLabel("No data available for this period")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("color: #a8b5c1; font-size: 16px; margin: 100px;")
            charts_layout.addWidget(no_data_label)
        
        return charts_widget
    
    def create_avg_stats_widget(self, data):
        """Create the average stats widget."""
        avg_stats_widget = QFrame()
        avg_stats_widget.setProperty("class", "stats-card")
        avg_stats_widget.setMaximumWidth(250)
        avg_stats_layout = QVBoxLayout(avg_stats_widget)
        avg_stats_layout.setContentsMargins(20, 20, 20, 20)
        avg_stats_layout.setSpacing(30)
        
        # Calculate averages from data
        if data and len(data) > 0:
            heartbeats = [d.get('heartbeat', 0) for d in data if d.get('heartbeat', 0) > 0]
            stress_levels = [d.get('stress', 0) for d in data if d.get('stress', 0) > 0]
            
            avg_heartbeat = sum(heartbeats) / len(heartbeats) if heartbeats else 0
            min_heartbeat = min(heartbeats) if heartbeats else 0
            max_heartbeat = max(heartbeats) if heartbeats else 0
            
            avg_stress = sum(stress_levels) / len(stress_levels) if stress_levels else 0
            min_stress = min(stress_levels) if stress_levels else 0
            max_stress = max(stress_levels) if stress_levels else 0
        else:
            avg_heartbeat = min_heartbeat = max_heartbeat = 0
            avg_stress = min_stress = max_stress = 0
        
        # Average heartbeat section
        avg_hb_widget = self.create_metric_widget(
            "Average Heartbeat", 
            f"{avg_heartbeat:.1f} BPM", 
            f"{min_heartbeat:.0f}/{max_heartbeat:.0f}",
            "#7cb9e8"
        )
        
        # Average stress section
        avg_stress_widget = self.create_metric_widget(
            "Average Stress",
            f"{avg_stress:.3f}",
            f"{min_stress:.2f}/{max_stress:.2f}",
            "#f4a261"
        )
        
        avg_stats_layout.addWidget(avg_hb_widget)
        avg_stats_layout.addWidget(avg_stress_widget)
        avg_stats_layout.addStretch()
        
        return avg_stats_widget
    
    def create_right_stats_widget(self, data, period):
        """Create the right stats widget with time and score."""
        right_stats_widget = QFrame()
        right_stats_widget.setProperty("class", "stats-card")
        right_stats_widget.setMaximumWidth(250)
        right_stats_layout = QVBoxLayout(right_stats_widget)
        right_stats_layout.setContentsMargins(20, 20, 20, 20)
        right_stats_layout.setSpacing(30)
        
        # Calculate totals from data
        total_time = sum([d.get('duration', 0) for d in data]) if data else 0
        total_score = sum([d.get('score', 0) for d in data]) if data else 0
        
        # Get period-specific data from database
        db_stats = self.get_period_stats(period)
        if db_stats:
            total_time = db_stats['total_time']
            total_score = db_stats['total_score']
        
        # Rest time section
        rest_minutes = total_time / 60
        rest_time_widget = self.create_metric_widget(
            "Rest in min",
            f"{rest_minutes:.0f} min",
            "",
            "#90e0ef"
        )
        
        # Score section
        period_names = {
            'daily': 'Today Score',
            'weekly': 'Weekly Score', 
            'monthly': 'Monthly Score',
            'alltime': 'All Time Score'
        }
        
        score_widget = self.create_metric_widget(
            period_names.get(period, 'Score'),
            f"{total_score:.0f}",
            "",
            "#a8dadc"
        )
        
        # Improve note
        improve_note = QLabel("Improve note")
        improve_note.setFont(QFont("Segoe UI", 12))
        improve_note.setStyleSheet("color: #a8b5c1;")
        improve_note.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        
        right_stats_layout.addWidget(rest_time_widget)
        right_stats_layout.addWidget(score_widget)
        right_stats_layout.addStretch()
        right_stats_layout.addWidget(improve_note)
        
        return right_stats_widget
    
    def create_metric_widget(self, title, value, range_text, color):
        """Create a metric widget with title, value, and optional range."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Medium))
        title_label.setStyleSheet(f"color: {color};")
        
        # Value
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        value_label.setStyleSheet("color: #e8e9ea;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()
        
        # Range (if provided)
        if range_text:
            range_label = QLabel(range_text)
            range_label.setFont(QFont("Segoe UI", 12))
            range_label.setStyleSheet("color: #a8b5c1;")
            range_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
            layout.addWidget(range_label)
        
        return widget
    
    def get_enhanced_period_data(self, period):
        """Get enhanced data for charts."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Define date ranges
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
            
            # Get sessions with heartbeat data
            cursor.execute("""
                SELECT heartbeat_data, total_time_seconds, score, timestamp
                FROM Sessions 
                WHERE user_id = ? AND DATE(timestamp) BETWEEN ? AND ?
                AND heartbeat_data IS NOT NULL AND heartbeat_data != ''
                ORDER BY timestamp
            """, (self.user_id, start_date, end_date))
            
            sessions = cursor.fetchall()
            conn.close()
            
            if not sessions:
                return []
            
            chart_data = []
            
            for session in sessions[:20]:  # Limit to first 20 sessions for performance
                try:
                    heartbeat_json = json.loads(session[0])
                    heartbeats = heartbeat_json.get('heartbeats', [])
                    stress_levels = heartbeat_json.get('stress_levels', [])
                    
                    if heartbeats and stress_levels:
                        # Take average values for this session
                        avg_heartbeat = sum(heartbeats) / len(heartbeats)
                        avg_stress = sum(stress_levels) / len(stress_levels)
                        
                        chart_data.append({
                            'heartbeat': avg_heartbeat,
                            'stress': avg_stress,
                            'duration': session[1],
                            'score': session[2],
                            'timestamp': session[3]
                        })
                        
                except (json.JSONDecodeError, TypeError):
                    continue
            
            return chart_data
            
        except Exception as e:
            print(f"Error getting enhanced period data: {e}")
            return []
    
    def get_period_stats(self, period):
        """Get basic statistics for a period."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Define date ranges
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
            
            cursor.execute("""
                SELECT SUM(total_time_seconds), SUM(score), COUNT(*)
                FROM Sessions 
                WHERE user_id = ? AND DATE(timestamp) BETWEEN ? AND ?
            """, (self.user_id, start_date, end_date))
            
            result = cursor.fetchone()
            conn.close()
            
            return {
                'total_time': result[0] or 0,
                'total_score': result[1] or 0,
                'total_sessions': result[2] or 0
            }
            
        except Exception as e:
            print(f"Error getting period stats: {e}")
            return {'total_time': 0, 'total_score': 0, 'total_sessions': 0}
    
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
        
        # Update content for the new period
        self.create_enhanced_period_content(period)


# Test the enhanced interface
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