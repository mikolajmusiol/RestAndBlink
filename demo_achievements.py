#!/usr/bin/env python3
"""
Demo showcasing the achievements layout implementation
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.enhanced_wellness_window import EnhancedWellnessWindow

def main():
    """Demo achievements section."""
    print("🎮 Rest&Blink - Achievements Demo")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # Create the main window
    window = EnhancedWellnessWindow(user_id=1)
    
    # Switch directly to achievements section
    window.switch_section("achievements")
    
    print("✨ Achievements Features Implemented:")
    print("   🔲 3 large blocks per row layout")
    print("   📜 Scrollable achievement grid")
    print("   🎨 Earned achievements: Colorful with names")
    print("   🔘 Unearned achievements: Grayed out")
    print("   😀 Emoji icons from database")
    print("   🌈 Rarity color coding")
    print("   🏆 Earned achievements shown first")
    print("")
    print("🎯 Achievement counts:")
    
    earned, all_achievements = window.get_achievements_data()
    print(f"   ✅ Earned: {len(earned)}")
    print(f"   📋 Total: {len(all_achievements)}")
    print(f"   ⏳ Remaining: {len(all_achievements) - len(earned)}")
    
    print("\n🚀 Demo ready! Check the achievements tab in the application!")
    
    window.show()
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())