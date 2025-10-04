#!/usr/bin/env python3
"""
Test the new symbol-based achievement icons
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QFrame, QGridLayout, QScrollArea
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class SymbolTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Symbol-Based Achievement Icons Test")
        self.setGeometry(100, 100, 1000, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("✅ NEW: Reliable Symbol-Based Achievement Icons")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #22c55e; margin: 20px; text-align: center;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        content_widget = QWidget()
        grid_layout = QGridLayout(content_widget)
        
        # Test achievements with symbol mapping
        achievements = [
            {"name": "First Steps", "emoji": "🎯", "symbol": "●", "rarity": "common", "earned": True},
            {"name": "Getting Started", "emoji": "🚀", "symbol": "▲", "rarity": "common", "earned": True},
            {"name": "Dedicated", "emoji": "💪", "symbol": "♦", "rarity": "uncommon", "earned": True},
            {"name": "Regular User", "emoji": "⭐", "symbol": "★", "rarity": "uncommon", "earned": False},
            {"name": "Marathon", "emoji": "🏃", "symbol": "►", "rarity": "rare", "earned": False},
            {"name": "Century Club", "emoji": "👑", "symbol": "♔", "rarity": "epic", "earned": False},
            {"name": "Point Starter", "emoji": "🔸", "symbol": "◇", "rarity": "common", "earned": True},
            {"name": "Point Collector", "emoji": "🔹", "symbol": "◆", "rarity": "uncommon", "earned": True},
            {"name": "Time Master", "emoji": "⏰", "symbol": "⊙", "rarity": "rare", "earned": False},
            {"name": "Time Elite", "emoji": "⏳", "symbol": "⧗", "rarity": "epic", "earned": False},
        ]
        
        # Create grid of achievement cards
        row, col = 0, 0
        for achievement in achievements:
            card = self.create_achievement_card(achievement)
            grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= 5:  # 5 columns
                col = 0
                row += 1
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # Footer
        footer = QLabel("🎯 These symbols should display properly without 'no glyph' issues!")
        footer.setStyleSheet("color: #7cb9e8; margin: 10px; text-align: center;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1d1f; }
            QScrollArea { background-color: #1a1d1f; border: none; }
        """)
    
    def create_achievement_card(self, achievement):
        """Create achievement card with symbol instead of emoji."""
        card = QFrame()
        card.setMinimumSize(180, 140)
        card.setMaximumSize(200, 160)
        
        if achievement["earned"]:
            card.setStyleSheet("""
                QFrame {
                    background-color: #2a2d30;
                    border: none;
                    border-radius: 8px;
                    margin: 5px;
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
                    margin: 5px;
                }
                QFrame:hover {
                    background-color: #252932;
                }
            """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 15, 10, 10)
        
        # Use symbol instead of emoji
        symbol_label = QLabel(achievement["symbol"])
        
        # Set up robust font
        symbol_font = QFont()
        symbol_font.setPointSize(42)
        symbol_font.setFamily("DejaVu Sans")
        symbol_font.setWeight(QFont.Bold)
        
        symbol_label.setFont(symbol_font)
        symbol_label.setAlignment(Qt.AlignCenter)
        
        # Color by rarity and earned status
        rarity_colors = {
            'common': '#9ca3af',
            'uncommon': '#22c55e',
            'rare': '#3b82f6',
            'epic': '#a855f7',
        }
        
        if achievement["earned"]:
            icon_color = rarity_colors.get(achievement["rarity"], '#ffffff')
        else:
            icon_color = '#4a4d52'  # Gray for unearned
        
        symbol_label.setStyleSheet(f"""
            QLabel {{
                color: {icon_color};
                background: transparent;
                font-weight: bold;
            }}
        """)
        
        # Name label
        name_label = QLabel(achievement["name"])
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: bold;")
        
        # Rarity label
        rarity_label = QLabel(achievement["rarity"].upper())
        rarity_label.setAlignment(Qt.AlignCenter)
        rarity_color = rarity_colors.get(achievement["rarity"], '#9ca3af')
        if not achievement["earned"]:
            rarity_color = '#5a6269'
        rarity_label.setStyleSheet(f"color: {rarity_color}; font-size: 10px; font-weight: bold;")
        
        # Original emoji info (for comparison)
        emoji_info = QLabel(f"Was: {achievement['emoji']}")
        emoji_info.setAlignment(Qt.AlignCenter)
        emoji_info.setStyleSheet("color: #666; font-size: 8px;")
        
        layout.addWidget(symbol_label)
        layout.addWidget(name_label)
        layout.addWidget(rarity_label)
        layout.addWidget(emoji_info)
        
        return card

def main():
    app = QApplication(sys.argv)
    window = SymbolTestWindow()
    window.show()
    
    print("🔧 Testing symbol-based achievement icons...")
    print("✅ These should display properly without 'no glyph' issues")
    print("🎯 Symbols are colored by rarity: Common=Gray, Uncommon=Green, Rare=Blue, Epic=Purple")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()