#!/usr/bin/env python3
"""
Test script for achievements functionality
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.enhanced_wellness_window import EnhancedWellnessWindow

def test_achievements():
    """Test achievements functionality."""
    app = QApplication(sys.argv)
    
    # Create the main window
    window = EnhancedWellnessWindow(user_id=1)
    
    # Test achievements data retrieval
    print("🧪 Testing achievements data retrieval...")
    earned, all_achievements = window.get_achievements_data()
    
    print(f"📊 Found {len(earned)} earned achievements")
    print(f"📊 Found {len(all_achievements)} total achievements")
    
    print("\n🏆 Earned achievements:")
    for achievement in earned[:5]:  # Show first 5
        print(f"   {achievement['badge_icon']} {achievement['name']} ({achievement['rarity']})")
    
    print(f"\n📝 Unearned achievements (showing first 5):")
    unearned = [a for a in all_achievements if a['id'] not in [ea['id'] for ea in earned]]
    for achievement in unearned[:5]:
        print(f"   {achievement['badge_icon']} {achievement['name']} ({achievement['rarity']})")
    
    # Show the window with achievements section active
    window.show()
    window.switch_section("achievements")  # Switch to achievements
    
    print("\n✅ Achievements test completed!")
    print("🎯 Application opened with achievements section active")
    print("💡 Check the GUI to see the achievement cards layout!")
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(test_achievements())