#!/usr/bin/env python3
"""
Test responsywnego GUI z dynamicznym układem
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.enhanced_wellness_window import EnhancedWellnessWindow

def main():
    """Test responsywnego interfejsu."""
    print("🔄 Testing Responsive GUI")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # Create window
    window = EnhancedWellnessWindow(user_id=1)
    
    print("✨ Responsive Features:")
    print("   📏 Auto window sizing (85% screen width/80% height)")
    print("   🔲 Dynamic achievements grid (3-8 columns)")
    print("   📊 Responsive stats layout (1-3 columns)")
    print("   🎯 Flexible card sizes (200x140 - 280x180)")
    print("   🖥️  Minimum window size: 1000x700")
    print("")
    
    # Get screen info
    from PyQt5.QtWidgets import QDesktopWidget
    desktop = QDesktopWidget()
    screen_rect = desktop.screenGeometry()
    window_size = window.size()
    
    print(f"🖥️  Screen resolution: {screen_rect.width()}x{screen_rect.height()}")
    print(f"🪟 Window size: {window_size.width()}x{window_size.height()}")
    print("")
    
    # Calculate expected columns
    available_width = window_size.width() - 120
    card_width_with_spacing = 260
    expected_columns = max(3, min(8, available_width // card_width_with_spacing))
    print(f"📐 Expected achievement columns: {expected_columns}")
    
    # Test with achievements section
    window.switch_section("achievements")
    
    print("\n🚀 GUI ready! Try resizing the window to see responsive behavior!")
    print("💡 Achievements grid will adjust column count automatically")
    print("📊 Stats layout will adapt to different window sizes")
    
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())