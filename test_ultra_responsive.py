#!/usr/bin/env python3
"""
Test bardzo responsywnego GUI z minimum 2 ikonami w rzędzie
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.enhanced_wellness_window import EnhancedWellnessWindow

def main():
    """Test ultra-responsywnego interfejsu."""
    print("🔄 Testing Ultra-Responsive GUI")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # Create window
    window = EnhancedWellnessWindow(user_id=1)
    
    print("✨ Enhanced Responsive Features:")
    print("   🔢 Minimum icons per row: 2 (was 3)")
    print("   📐 Maximum icons per row: 10 (was 8)")
    print("   📏 Card sizes: 180x130 - 320x200 (more flexible)")
    print("   📊 Stats breakpoints: 800px / 1200px (was 1000px / 1400px)")
    print("   🎯 Dynamic icon sizes: 48-56px based on screen width")
    print("")
    
    # Get screen info
    from PyQt5.QtWidgets import QDesktopWidget
    desktop = QDesktopWidget()
    screen_rect = desktop.screenGeometry()
    window_size = window.size()
    
    print(f"🖥️  Screen resolution: {screen_rect.width()}x{screen_rect.height()}")
    print(f"🪟 Window size: {window_size.width()}x{window_size.height()}")
    print("")
    
    # Calculate expected columns with new parameters
    available_width = window_size.width() - 120
    card_width_with_spacing = 220  # New calculation
    expected_columns = max(2, min(10, available_width // card_width_with_spacing))
    print(f"📐 Expected achievement columns: {expected_columns}")
    
    # Determine stats layout
    if window_size.width() > 1200:
        stats_layout = "3-column (wide)"
    elif window_size.width() > 800:
        stats_layout = "2-column (medium)"
    else:
        stats_layout = "1-column (narrow)"
    
    print(f"📊 Stats layout: {stats_layout}")
    
    # Icon size
    if window_size.width() > 1400:
        icon_size = "56px (large)"
    elif window_size.width() > 1000:
        icon_size = "52px (medium)"
    else:
        icon_size = "48px (small)"
    
    print(f"😀 Icon size: {icon_size}")
    print("")
    
    # Test with achievements section
    window.switch_section("achievements")
    
    print("🚀 Ultra-responsive GUI ready!")
    print("💡 Now supports narrower screens with minimum 2 icons per row")
    print("📱 Better mobile/tablet experience")
    print("🖥️  Enhanced ultra-wide screen support (up to 10 columns)")
    print("🔄 Try resizing to very narrow widths!")
    
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())