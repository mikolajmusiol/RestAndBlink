#!/usr/bin/env python3
"""
Test emoji rendering fix for achievements.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class EmojiTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Emoji Rendering Test")
        self.setGeometry(100, 100, 600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Test different emoji rendering methods
        emojis = ["🎯", "🚀", "💪", "⭐", "🏃", "👑", "🔸", "🔹", "🔶", "🔷"]
        
        for i, emoji in enumerate(emojis):
            frame = QFrame()
            frame.setStyleSheet("background-color: #2a2d30; border-radius: 8px; margin: 5px;")
            frame.setMinimumHeight(60)
            
            frame_layout = QVBoxLayout(frame)
            
            # Create emoji label with improved font
            emoji_label = QLabel(emoji)
            emoji_font = QFont()
            emoji_font.setPointSize(32)
            emoji_font.setFamily("Noto Color Emoji")
            emoji_font.setStyleHint(QFont.System)
            emoji_font.setHintingPreference(QFont.PreferFullHinting)
            
            emoji_label.setFont(emoji_font)
            emoji_label.setAlignment(Qt.AlignCenter)
            emoji_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    background: transparent;
                    text-align: center;
                }
            """)
            
            # Add name label
            name_label = QLabel(f"Test Emoji {i+1}")
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setStyleSheet("color: #ffffff; font-size: 12px;")
            
            frame_layout.addWidget(emoji_label)
            frame_layout.addWidget(name_label)
            layout.addWidget(frame)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1d1f;
            }
        """)

def main():
    app = QApplication(sys.argv)
    window = EmojiTestWindow()
    window.show()
    
    print("🧪 Testing emoji rendering...")
    print("✅ If you see colorful emojis in the window, the fix is working!")
    print("❌ If you see 'no glyph' boxes, the emoji font needs additional fixes.")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()