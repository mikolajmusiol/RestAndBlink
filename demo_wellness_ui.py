#!/usr/bin/env python3
# Demo script for the new wellness interface

import sys
import os
from PyQt5.QtWidgets import QApplication

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from ui.main_wellness_window import WellnessMainWindow


def main():
    """Launch the new Rest&Blink wellness interface."""
    app = QApplication(sys.argv)
    
    print("🚀 Rest&Blink - Wellness Dashboard")
    print("=" * 50)
    print()
    print("✨ New Interface Features:")
    print("   🎯 Modern bio-hacking dark theme")
    print("   👤 User info with level display")
    print("   🧭 Clean navigation: Main | Stats | Configure | Achievements")
    print("   📊 Comprehensive stats dashboard")
    print("   🏥 Health metrics visualization")
    print("   📈 Period selection: Daily | Weekly | Monthly | All Time")
    print()
    print("🎨 Design Highlights:")
    print("   • Dark wellness color scheme (#1a1d1f base)")
    print("   • Bio-hacking aesthetic with muted tones")
    print("   • Card-based layout for data organization")
    print("   • Responsive grid system")
    print("   • Real-time data integration")
    print()
    print("📊 Stats Dashboard Layout:")
    print("   📈 Left: Heartbeat & Stress charts (stacked)")
    print("   📊 Middle: Average metrics with min/max ranges")
    print("   ⏱️  Right: Rest time & period scores")
    print("   💡 Bottom: Improvement notes area")
    print()
    
    # Check database
    if os.path.exists('user_data.db'):
        print("✅ Database connected - showing real user data")
    else:
        print("⚠️  Database not found - using placeholder data")
    
    print()
    print("🎯 Starting with Stats section active...")
    
    # Create and show the window
    window = WellnessMainWindow()
    window.show()
    
    # Start with stats section
    window.switch_section("stats")
    
    print("📱 Interface launched successfully!")
    print("💡 Navigate between periods to see different data views")
    
    # Run the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()