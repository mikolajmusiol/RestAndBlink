#!/usr/bin/env python3
# Enhanced Rest&Blink Wellness Interface Demo

import sys
import os
from PyQt5.QtWidgets import QApplication

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from ui.enhanced_wellness_window import EnhancedWellnessWindow


def main():
    """Launch the enhanced Rest&Blink wellness interface."""
    app = QApplication(sys.argv)
    
    print("🚀 Rest&Blink - Enhanced Wellness Dashboard")
    print("=" * 60)
    print()
    print("✨ NEW INTERFACE FEATURES (Exactly as requested):")
    print()
    print("🎯 HEADER LAYOUT:")
    print("   📍 Top Left: 'Rest&Blink' logo")
    print("   👤 Top Right: 'Hi, {name} {surname}' + 'lv. {level}' below")
    print()
    print("🧭 NAVIGATION TILES (Center Top):")
    print("   🏠 Main (home page)")
    print("   📊 Stats (statistics dashboard)")
    print("   ⚙️  Configure (settings - placeholder)")
    print("   🏆 Achievements (achievements - placeholder)")
    print()
    print("📊 STATS SECTION LAYOUT:")
    print("   📌 Fixed header: 'Stats: {which stats}'")
    print("   🔘 Period tiles: Daily | Weekly | Monthly | All Time")
    print()
    print("📈 STATS DASHBOARD (For each period):")
    print("   📈 Left: Two charts stacked vertically")
    print("      • Heartbeat chart (top)")
    print("      • Stress chart (bottom)")
    print("   📊 Middle: Average metrics")
    print("      • Average Heartbeat + min/max in bottom right")
    print("      • Average Stress + min/max in bottom right")
    print("   ⏱️  Right: Time and score")
    print("      • Rest in min (top)")
    print("      • Today/Weekly/Monthly/All Time Score (bottom)")
    print("      • 'Improve note' in bottom right corner")
    print()
    print("🎨 DESIGN THEME:")
    print("   🌙 Dark wellness colors (#1a1d1f base)")
    print("   💙 Bio-hacking aesthetic with muted tones")  
    print("   🔳 Card-based layout for organization")
    print("   📱 Responsive and professional look")
    print()
    print("📊 DATA INTEGRATION:")
    print("   💾 Real data from user_data.db")
    print("   📈 Live matplotlib charts")
    print("   🔄 Dynamic period switching")
    print("   📊 154 sessions with rich heartbeat/stress data")
    print()
    
    # Check database
    if os.path.exists('user_data.db'):
        print("✅ Database connected - showing real user data")
        import sqlite3
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Sessions WHERE DATE(timestamp) = DATE('now')")
        today_sessions = cursor.fetchone()[0]
        cursor.execute("SELECT first_name, last_name, level FROM Users WHERE id = 1")
        user_info = cursor.fetchone()
        conn.close()
        
        if user_info:
            print(f"👤 User: {user_info[0]} {user_info[1]} (Level {user_info[2]})")
        print(f"📅 Today's sessions: {today_sessions}")
    else:
        print("⚠️  Database not found - will show placeholder data")
    
    print()
    print("🎯 Starting with Stats section active...")
    print("💡 Click period tiles to see different time ranges!")
    print("🔄 All charts update with real data from database!")
    print()
    
    # Create and show the window
    window = EnhancedWellnessWindow()
    window.show()
    
    # Start with stats section (as requested)
    window.switch_section("stats")
    
    print("📱 Enhanced wellness interface launched successfully!")
    print("🎉 Enjoy your bio-hacking wellness dashboard!")
    
    # Run the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()