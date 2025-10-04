# ui/tabs/achievements_tab.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QGridLayout, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sqlite3


class AchievementsTab(QWidget):
    """Achievements tab widget for displaying user achievements in a grid."""
    
    def __init__(self, user_id=1, db_path="user_data.db"):
        super().__init__()
        self.user_id = user_id
        self.db_path = db_path
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the achievements UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
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
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Get achievements data
        earned_achievements, all_achievements = self.get_achievements_data()
        
        # Create grid layout for achievements (3 per row)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        
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
        
        # Create achievement cards
        row = 0
        col = 0
        for achievement in sorted_achievements:
            card = self.create_achievement_card(achievement)
            grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= 3:  # 3 cards per row
                col = 0
                row += 1
        
        content_layout.addLayout(grid_layout)
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
    
    def create_achievement_card(self, achievement):
        """Create a single achievement card."""
        card = QFrame()
        card.setFixedSize(220, 160)  # Smaller size
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
        
        # Achievement icon (emoji) - larger and clearer
        icon_label = QLabel(achievement['badge_icon'])
        icon_label.setFont(QFont("Segoe UI Emoji", 56))  # Bigger emoji
        icon_label.setAlignment(Qt.AlignCenter)
        if not achievement['earned']:
            icon_label.setStyleSheet("color: #4a4d52;")
        else:
            icon_label.setStyleSheet("color: #ffffff;")
        
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
    
    def refresh_achievements(self):
        """Refresh achievements display."""
        # Clear current layout
        layout = self.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Rebuild UI
        self.setup_ui() 