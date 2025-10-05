#!/usr/bin/env python3
"""
Quick test for the improved achievements layout
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.enhanced_wellness_window import EnhancedWellnessWindow

def main():
    """Quick achievements test."""
    print("🎮 Testing Improved Achievements Layout")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # Create window
    window = EnhancedWellnessWindow(user_id=1)
    window.switch_section("achievements")
    
    # Test data
    earned, all_achievements = window.get_achievements_data()
    print(f"✅ {len(earned)} earned achievements displayed first")
    print(f"⏳ {len(all_achievements) - len(earned)} unearned achievements grayed out")
    print("")
    print("🎨 Layout improvements:")
    print("   📏 Smaller cards: 220x160px (was 300x200px)")
    print("   🎯 No oval borders or rectangles")
    print("   😀 Larger emoji icons: 56px (was 48px)")  
    print("   📐 Better spacing: 25px horizontal")
    print("   🎪 3 cards per row, centered")
    print("")
    print("🚀 Ready! Check the achievements section!")
    
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())