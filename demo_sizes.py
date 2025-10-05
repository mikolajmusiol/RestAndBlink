#!/usr/bin/env python3
"""
Demo różnych rozmiarów okna dla ultra-responsywności
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.enhanced_wellness_window import EnhancedWellnessWindow

def test_window_size(width, height, description):
    """Test specific window size."""
    print(f"\n📏 Testing {description}: {width}x{height}")
    
    # Calculate achievements layout
    available_width = width - 120
    card_width_with_spacing = 220
    columns = max(2, min(10, available_width // card_width_with_spacing))
    
    # Determine stats layout
    if width > 1200:
        stats_layout = "3-column"
    elif width > 800:
        stats_layout = "2-column"
    else:
        stats_layout = "1-column"
    
    # Icon size
    if width > 1400:
        icon_size = "56px"
    elif width > 1000:
        icon_size = "52px"
    else:
        icon_size = "48px"
    
    print(f"   🔲 Achievements: {columns} columns")
    print(f"   📊 Stats: {stats_layout}")
    print(f"   😀 Icons: {icon_size}")

def main():
    """Demo różnych rozmiarów."""
    print("📱 Ultra-Responsive GUI Size Demo")
    print("=" * 50)
    
    # Test różne rozmiary okna
    test_window_size(600, 400, "Very Narrow (Mobile)")
    test_window_size(800, 600, "Narrow (Small Tablet)")
    test_window_size(1000, 700, "Medium (Tablet)")
    test_window_size(1200, 800, "Standard (Laptop)")
    test_window_size(1600, 900, "Wide (Desktop)")
    test_window_size(2000, 1200, "Very Wide (Ultra-wide)")
    test_window_size(2560, 1440, "Ultra-wide (Gaming)")
    
    print("\n" + "=" * 50)
    print("🔄 Key Improvements:")
    print("   • Minimum 2 icons per row (vs 3 before)")
    print("   • Maximum 10 icons per row (vs 8 before)")
    print("   • Stats breakpoints lowered for better stacking")
    print("   • Dynamic icon sizes for all screen sizes")
    print("   • Smaller minimum card sizes for mobile")
    
    print("\n🚀 Starting interactive demo...")
    
    app = QApplication(sys.argv)
    window = EnhancedWellnessWindow(user_id=1)
    window.switch_section("achievements")
    
    print("\n💡 Instructions:")
    print("   1. Resize window horizontally to see column changes")
    print("   2. Very narrow = 2 columns minimum")
    print("   3. Very wide = up to 10 columns")
    print("   4. Switch to Stats to see responsive dashboard")
    
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())