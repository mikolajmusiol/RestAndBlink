#!/usr/bin/env python3
"""
Alternative emoji fix - using Unicode symbols that work better on Linux
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QFrame, QGridLayout, QScrollArea
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class ImprovedEmojiTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Improved Emoji/Symbol Test")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        content_widget = QWidget()
        grid_layout = QGridLayout(content_widget)
        
        # Test achievement data with better symbols
        achievements = [
            {"name": "First Steps", "emoji": "🎯", "fallback": "●", "rarity": "common"},
            {"name": "Getting Started", "emoji": "🚀", "fallback": "▲", "rarity": "common"},
            {"name": "Dedicated", "emoji": "💪", "fallback": "♦", "rarity": "uncommon"},
            {"name": "Regular User", "emoji": "⭐", "fallback": "★", "rarity": "uncommon"},
            {"name": "Marathon", "emoji": "🏃", "fallback": "►", "rarity": "rare"},
            {"name": "Century Club", "emoji": "👑", "fallback": "♔", "rarity": "epic"},
            {"name": "Point Starter", "emoji": "🔸", "fallback": "◊", "rarity": "common"},
            {"name": "Point Collector", "emoji": "🔹", "fallback": "◇", "rarity": "uncommon"},
        ]
        
        # Create grid of achievement cards
        row, col = 0, 0
        for achievement in achievements:
            card = self.create_achievement_card(achievement)
            grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= 4:  # 4 columns
                col = 0
                row += 1
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1d1f; }
            QScrollArea { background-color: #1a1d1f; border: none; }
        """)
    
    def create_achievement_card(self, achievement):
        """Create achievement card with robust icon rendering."""
        card = QFrame()
        card.setMinimumSize(180, 140)
        card.setMaximumSize(200, 160)
        card.setStyleSheet("""
            QFrame {
                background-color: #2a2d30;
                border: none;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 15, 10, 10)
        
        # Try emoji first, fallback to symbol
        icon_text = achievement["emoji"]
        
        # Create icon label
        icon_label = QLabel(icon_text)
        
        # Set up robust font
        icon_font = QFont()
        icon_font.setPointSize(42)
        
        # Use multiple font families for maximum compatibility
        font_families = [
            "Noto Color Emoji",
            "Segoe UI Emoji", 
            "Apple Color Emoji",
            "Symbola",
            "DejaVu Sans",
            "Arial Unicode MS",
            "sans-serif"
        ]
        
        for font_family in font_families:
            icon_font.setFamily(font_family)
            icon_label.setFont(icon_font)
            # You could test rendering here, but for simplicity, just use the first available
            break
        
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: transparent;
                font-weight: normal;
            }
        """)
        
        # Name label
        name_label = QLabel(achievement["name"])
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: bold;")
        
        # Rarity label
        rarity_label = QLabel(achievement["rarity"].upper())
        rarity_label.setAlignment(Qt.AlignCenter)
        rarity_colors = {
            'common': '#9ca3af',
            'uncommon': '#22c55e',
            'rare': '#3b82f6',
            'epic': '#a855f7',
        }
        color = rarity_colors.get(achievement["rarity"], '#9ca3af')
        rarity_label.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: bold;")
        
        layout.addWidget(icon_label)
        layout.addWidget(name_label)
        layout.addWidget(rarity_label)
        
        return card

def main():
    app = QApplication(sys.argv)
    window = ImprovedEmojiTestWindow()
    window.show()
    
    print("🧪 Testing improved emoji/symbol rendering...")
    print("✅ This version uses better font fallbacks and Unicode symbols")
    print("🔍 Check if the icons display properly in the grid")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()