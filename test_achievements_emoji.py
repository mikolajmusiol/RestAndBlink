#!/usr/bin/env python3
"""
Quick test for achievements emoji rendering.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
sys.path.append('/home/jaromek/Programming/Repos/HackYeah2025')

from ui.enhanced_wellness_window import EnhancedWellnessWindow

def main():
    app = QApplication(sys.argv)
    
    # Create the main window
    window = EnhancedWellnessWindow()
    window.show()
    
    # Switch directly to achievements to test emoji rendering
    window.switch_section("achievements")
    
    print("🏆 Testing achievements emoji rendering...")
    print("✅ Check the achievements section for proper emoji display")
    print("❌ If you see 'no glyph' boxes, the emoji fonts need more work")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()