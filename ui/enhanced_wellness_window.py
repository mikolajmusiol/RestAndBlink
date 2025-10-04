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
        
        # Set responsive window size based on screen
        from PyQt5.QtWidgets import QDesktopWidget
        desktop = QDesktopWidget()
        screen_rect = desktop.screenGeometry()
        
        # Use 85% of screen width and 80% of screen height
        window_width = int(screen_rect.width() * 0.85)
        window_height = int(screen_rect.height() * 0.80)
        
        # Minimum and maximum sizes
        window_width = max(1200, min(2400, window_width))
        window_height = max(800, min(1600, window_height))
        
        self.setGeometry(100, 100, window_width, window_height)
        self.setMinimumSize(1000, 700)  # Minimum usable size
        
        # Apply dark wellness theme
        self.apply_wellness_theme()
        
        # Get user data
        self.user_data = self.get_user_data()
        
        # Setup UI
        self.setup_ui()
    
    def resizeEvent(self, event):
        """Handle window resize to update responsive layouts."""
        super().resizeEvent(event)
        # Rebuild achievements grid when window is resized
        if hasattr(self, 'achievements_layout') and self.current_section == "achievements":
            self.rebuild_achievements_grid()
        # Stats section now uses fixed layout - no rebuild needed
    
    def rebuild_achievements_grid(self):
        """Rebuild achievements grid with new column count."""
        # Clear existing grid
        while self.achievements_layout.count():
            child = self.achievements_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Recreate grid with new dimensions
        self.create_responsive_achievements_grid()
        
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
        
        # Top header section with stats (always visible)
        self.create_header(main_layout)
        
        # Navigation section under header (always visible)
        self.create_fixed_navigation(main_layout)
        
        # Separator line under navigation
        self.create_navigation_separator(main_layout)
        
        # Content area
        self.create_content_area(main_layout)
    
    def create_header(self, parent_layout):
        """Create the top header with logo, user info and centered quick stats."""
        header_widget = QWidget()
        header_widget.setFixedHeight(90)  # Normal height for smaller cards
        header_widget.setStyleSheet("background-color: #1a1d1f;")
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(30, 10, 30, 10)
        header_layout.setSpacing(20)
        
        # Left side - Logo
        logo_label = QLabel("Rest&Blink")
        logo_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        logo_label.setStyleSheet("color: #7cb9e8; border: none;")
        header_layout.addWidget(logo_label)
        
        # Left spacer to center the stats
        header_layout.addStretch(1)
        
        # Middle - Centered Quick stats cards
        quick_stats_widget = QWidget()
        quick_stats_layout = QHBoxLayout(quick_stats_widget)
        quick_stats_layout.setContentsMargins(0, 0, 0, 0)
        quick_stats_layout.setSpacing(15)
        
        # Today's sessions card
        today_card = self.create_quick_stat_card("Today's Sessions", "8", "#7cb9e8")
        current_streak_card = self.create_quick_stat_card("Current Streak", f"{self.user_data.get('level', 1)} days", "#90e0ef")
        total_time_card = self.create_quick_stat_card("Total Time", "12h 15m", "#a8dadc")
        
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
    
    def create_fixed_navigation(self, parent_layout):
        """Create fixed navigation tiles that are always visible."""
        nav_widget = QWidget()
        nav_widget.setFixedHeight(70)
        nav_widget.setStyleSheet("background-color: #1a1d1f;")
        
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(30, 15, 30, 15)
        nav_layout.setSpacing(20)
        
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
            btn.setMinimumSize(120, 40)
            btn.clicked.connect(lambda checked, nav_id=nav_id: self.switch_section(nav_id))
            
            self.nav_buttons[nav_id] = btn
            nav_layout.addWidget(btn)
        
        # Add spacer to center navigation
        nav_layout.addStretch()
        
        parent_layout.addWidget(nav_widget)
    
    def create_navigation_separator(self, parent_layout):
        """Create a separator line under navigation."""
        # Small spacing
        spacer_top = QWidget()
        spacer_top.setFixedHeight(10)
        spacer_top.setStyleSheet("background-color: #1a1d1f;")
        parent_layout.addWidget(spacer_top)
        
        # Separator line
        separator = QFrame()
        separator.setFixedHeight(2)
        separator.setStyleSheet("background-color: #404448; border: none;")
        parent_layout.addWidget(separator)
        
        # Small spacing after
        spacer_bottom = QWidget()
        spacer_bottom.setFixedHeight(10)
        spacer_bottom.setStyleSheet("background-color: #1a1d1f;")
        parent_layout.addWidget(spacer_bottom)
    
    def create_content_area(self, parent_layout):
        """Create the main content area."""
        self.content_stack = QStackedWidget()
        
        # Main page
        main_page = self.create_main_page()
        
        # Stats page
        stats_page = self.create_stats_page()
        
        # Configure page (placeholder)
        configure_page = self.create_placeholder_page("Configuration", "Settings and preferences coming soon")
        
        # Achievements page
        achievements_page = self.create_achievements_page()
        
        # Add pages to stack
        self.content_stack.addWidget(main_page)        # index 0
        self.content_stack.addWidget(stats_page)       # index 1
        self.content_stack.addWidget(configure_page)   # index 2
        self.content_stack.addWidget(achievements_page) # index 3
        
        parent_layout.addWidget(self.content_stack)
        
        # Start with main section (which is now empty)
        self.switch_section("main")
    
    def create_main_page(self):
        """Create empty main page (content moved to header)."""
        main_page = QWidget()
        main_page.setStyleSheet("background-color: #1a1d1f;")
        main_layout = QVBoxLayout(main_page)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Empty main page - all content moved to header
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
    
    def create_achievements_page(self):
        """Create the achievements page with responsive scrollable grid."""
        page = QWidget()
        page.setStyleSheet("background-color: #1a1d1f;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1a1d1f;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2c3034;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #404448;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5a6269;
            }
        """)
        
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
        """Create a responsive grid that adapts to screen width."""
        # Get achievements data
        earned_achievements, all_achievements = self.get_achievements_data()
        
        # Sort achievements: earned first, then unearned
        sorted_achievements = []
        # Add earned achievements first
        for achievement in all_achievements:
            if achievement['id'] in [ea['id'] for ea in earned_achievements]:
                sorted_achievements.append({**achievement, 'earned': True})
        # Then add unearned achievements
        for achievement in all_achievements:
            if achievement['id'] not in [ea['id'] for ea in earned_achievements]:
                sorted_achievements.append({**achievement, 'earned': False})
        
        # Calculate dynamic columns based on window width
        # More responsive - minimum 2 icons per row for narrow screens
        available_width = self.width() - 120  # Account for margins and scrollbar
        card_width_with_spacing = 220  # Adjusted for new card sizes (200px avg + 20px spacing)
        min_columns = 2  # Changed from 3 to 2 for better mobile/narrow screen support
        max_columns = 10  # Increased max for ultra-wide screens
        columns = max(min_columns, min(max_columns, available_width // card_width_with_spacing))
        
        # Create dynamic grid layout for achievements
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(20)
        
        # Add achievement cards in responsive grid
        row = 0
        col = 0
        for achievement in sorted_achievements:
            card = self.create_achievement_card(achievement)
            grid_layout.addWidget(card, row, col, Qt.AlignCenter)
            
            col += 1
            if col >= columns:
                col = 0
                row += 1
        
        # Create widget to hold the grid
        grid_widget = QWidget()
        grid_widget.setLayout(grid_layout)
        
        self.achievements_layout.addWidget(grid_widget)
        self.achievements_layout.addStretch()
    
    def create_achievement_card(self, achievement):
        """Create a single achievement card."""
        card = QFrame()
        card.setMinimumSize(180, 130)  # Smaller minimum for narrow screens
        card.setMaximumSize(320, 200)  # Larger maximum for wide screens
        card.setFrameStyle(QFrame.NoFrame)  # Remove frame style
        
        # Simple style without borders/ovals
        if achievement['earned']:
            card.setStyleSheet("""
                QFrame {
                    background-color: #2a2d30;
                    border: none;
                    border-radius: 8px;
                }
                QFrame:hover {
                    background-color: #323639;
                }
            """)
        else:
            card.setStyleSheet("""
                QFrame {
                    background-color: #1e2125;
                    border: none;
                    border-radius: 8px;
                }
                QFrame:hover {
                    background-color: #252932;
                }
            """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)
        
        # Achievement icon - use reliable symbols instead of problematic emoji
        original_emoji = achievement['badge_icon']
        
        # Complete mapping to Unicode symbols that work reliably on Linux
        symbol_mapping = {
            '🎯': '●',     # Target -> Bullet
            '🚀': '▲',     # Rocket -> Triangle
            '💪': '♦',     # Muscle -> Diamond
            '⭐': '★',     # Star -> Star (should work)
            '🏃': '►',     # Runner -> Play symbol
            '👑': '♔',     # Crown -> King
            '🔸': '◇',     # Orange diamond -> White diamond
            '🔹': '◆',     # Blue diamond -> Black diamond
            '🔶': '◆',     # Large orange diamond -> Black diamond
            '🔷': '◇',     # Large blue diamond -> White diamond
            '⏰': '⊙',     # Alarm clock -> Circled dot
            '⏳': '⧗',     # Hourglass -> Hourglass symbol
        }
        
        # Use symbol mapping - fallback to first character if not found
        display_icon = symbol_mapping.get(original_emoji, original_emoji[0] if original_emoji else '•')
        
        icon_label = QLabel(display_icon)
        
        # Dynamic font size
        if self.width() > 1400:
            icon_font_size = 56
        elif self.width() > 1000:
            icon_font_size = 52
        else:
            icon_font_size = 48
        
        # Use standard font that supports Unicode symbols
        symbol_font = QFont()
        symbol_font.setPointSize(icon_font_size)
        symbol_font.setFamily("DejaVu Sans")  # Reliable font for symbols
        symbol_font.setWeight(QFont.Bold)  # Make symbols more prominent
        
        icon_label.setFont(symbol_font)
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Enhanced styling with color coding for different rarities
        rarity_colors = {
            'common': '#9ca3af',
            'uncommon': '#22c55e', 
            'rare': '#3b82f6',
            'epic': '#a855f7',
            'legendary': '#f59e0b',
            'mythic': '#ff1744'
        }
        
        if not achievement['earned']:
            # Gray out unearned achievements
            icon_label.setStyleSheet("""
                QLabel {
                    color: #4a4d52;
                    font-weight: bold;
                    text-align: center;
                    background: transparent;
                }
            """)
        else:
            # Color earned achievements by rarity
            icon_color = rarity_colors.get(achievement['rarity'], '#ffffff')
            icon_label.setStyleSheet(f"""
                QLabel {{
                    color: {icon_color};
                    font-weight: bold;
                    text-align: center;
                    background: transparent;
                }}
            """)
        
        # Achievement name - shorter and cleaner
        name_label = QLabel(achievement['name'])
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        if achievement['earned']:
            name_label.setStyleSheet("color: #ffffff; margin-top: 5px;")
        else:
            name_label.setStyleSheet("color: #8b9197; margin-top: 5px;")
        
        # Rarity indicator - smaller and more subtle
        rarity_label = QLabel(achievement['rarity'].upper())
        rarity_label.setAlignment(Qt.AlignCenter)
        rarity_label.setFont(QFont("Segoe UI", 8, QFont.Bold))
        
        # Color code by rarity
        rarity_colors = {
            'common': '#9ca3af',
            'uncommon': '#22c55e', 
            'rare': '#3b82f6',
            'epic': '#a855f7',
            'legendary': '#f59e0b',
            'mythic': '#ff1744'
        }
        rarity_color = rarity_colors.get(achievement['rarity'], '#9ca3af')
        if not achievement['earned']:
            rarity_color = '#5a6269'  # Gray out unearned
        
        rarity_label.setStyleSheet(f"color: {rarity_color}; margin-top: 3px;")
        
        layout.addWidget(icon_label)
        layout.addWidget(name_label)
        layout.addWidget(rarity_label)
        
        return card
    
    def get_achievements_data(self):
        """Get achievements data from database."""
        earned_achievements = []
        all_achievements = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get earned achievements
            cursor.execute("""
                SELECT a.id, a.name, a.description, a.badge_icon, a.rarity, ua.earned_date
                FROM Achievements a
                JOIN UserAchievements ua ON a.id = ua.achievement_id
                WHERE ua.user_id = ?
                ORDER BY ua.earned_date DESC
            """, (self.user_id,))
            
            for row in cursor.fetchall():
                earned_achievements.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'badge_icon': row[3],
                    'rarity': row[4],
                    'earned_date': row[5]
                })
            
            # Get all achievements
            cursor.execute("""
                SELECT id, name, description, badge_icon, rarity
                FROM Achievements
                WHERE is_active = 1
                ORDER BY id
            """)
            
            for row in cursor.fetchall():
                all_achievements.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'badge_icon': row[3],
                    'rarity': row[4]
                })
            
            conn.close()
            
        except Exception as e:
            print(f"Error fetching achievements data: {e}")
        
        return earned_achievements, all_achievements
    
    def create_quick_stat_card(self, title, value, color):
        """Create a quick stat card without borders."""
        card = QFrame()
        card.setFrameStyle(QFrame.NoFrame)  # Remove frame
        
        # Smaller, more reasonable size
        card.setFixedSize(180, 70)
        card.setMinimumSize(180, 70)
        
        # Simple card style without borders
        card.setStyleSheet("""
            QFrame {
                background-color: #232629;
                border: none;
                border-radius: 8px;
                padding: 8px;
            }
            QFrame:hover {
                background-color: #2a2d30;
            }
        """)
        
        # Use a simple vertical layout with tight spacing
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(2)
        
        # Title label - small and compact
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 9, QFont.Medium))  
        title_label.setStyleSheet(f"color: {color}; background: transparent; margin: 0px; padding: 0px;")
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setMaximumHeight(18)
        
        # Value label - smaller to fit
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        value_label.setStyleSheet("color: #e8e9ea; background: transparent; margin: 0px; padding: 0px;")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setMinimumHeight(25)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()  # Push content to top
        
        return card
    
    def create_stats_page(self):
        """Create the stats page with period selection."""
        stats_page = QWidget()
        stats_page.setStyleSheet("background-color: #1a1d1f;")
        
        stats_layout = QVBoxLayout(stats_page)
        stats_layout.setContentsMargins(30, 20, 30, 20)
        stats_layout.setSpacing(20)
        
        # Stats header - wrapped in container for centering
        header_container = QWidget()
        header_container.setStyleSheet("border: none; background: transparent;")
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        # Add stretchers to center the header
        header_layout.addStretch()
        
        stats_header = QLabel("Stats: Health & Wellness Analytics")
        stats_header.setFont(QFont("Segoe UI", 20, QFont.Medium))
        stats_header.setStyleSheet("color: #e8e9ea; border: none; background: transparent;")
        header_layout.addWidget(stats_header)
        
        header_layout.addStretch()
        
        stats_layout.addWidget(header_container)
        
        # Period selection buttons
        period_widget = QWidget()
        period_widget.setStyleSheet("border: none; background: transparent;")
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
        
        # Simple fixed layout - no responsive changes
        dashboard_layout.addWidget(charts_widget, 0, 0, 2, 1)  # Charts on left, span 2 rows
        dashboard_layout.addWidget(avg_stats_widget, 0, 1, 1, 1)  # Top right
        dashboard_layout.addWidget(right_stats_widget, 1, 1, 1, 1)  # Bottom right
        
        # Set column stretch
        dashboard_layout.setColumnStretch(0, 3)  # Charts take more space
        dashboard_layout.setColumnStretch(1, 1)  # Right column
        
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