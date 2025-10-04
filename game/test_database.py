#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database_manager import DatabaseManager

def test_achievement_system():
    """Test the new achievement system"""
    db = DatabaseManager()
    
    print("=== TESTING NEW ACHIEVEMENT SYSTEM ===\n")
    
    # Test user 1 (Anna Kowalska)
    user_id = 1
    print(f"📊 Testing automatic achievement checking for user {user_id}")
    
    # Get user info with achievements
    user_info = db.get_user_with_achievements(user_id)
    if user_info:
        user = user_info['user']
        achievements = user_info['achievements']
        
        print(f"\n👤 User: {user['full_name']}")
        print(f"🏆 Level {user['level']} ({user['level_name']})")
        print(f"💎 Total Points: {user['total_points']}")
        print(f"🎯 Sessions: {user['total_sessions']}")
        print(f"⏱️  Total Time: {user['total_time_seconds']}s ({user['total_time_seconds']/60:.1f} min)")
        print(f"🔥 Current Streak: {user['current_streak']} days")
        print(f"📈 Experience: {user['experience_points']} XP")
        print(f"✨ Bonus Multiplier: {user['bonus_multiplier']}x")
        
        print(f"\n🏅 Current Achievements ({len(achievements)}):")
        for ach in achievements:
            print(f"  {ach['badge_icon']} {ach['name']} ({ach['rarity']}) - {ach['points_awarded']} pts")
    
    # Test adding points from exercise session and checking achievements
    print(f"\n� Simulating exercise session - adding 50 points...")
    result = db.add_points_to_user(user_id, 50)
    
    if result['success'] and result['newly_earned_achievements']:
        print(f"🎉 NEW ACHIEVEMENTS EARNED:")
        for ach in result['newly_earned_achievements']:
            req_text = f"{ach['requirement_value']} {ach['requirement_type']}"
            print(f"  🏆 {ach['name']} (for reaching {req_text})")
    else:
        print("  No new achievements earned from this session.")
    
    print(f"\n" + "="*50)
    
    # Show updated user info
    user_info_updated = db.get_user_with_achievements(user_id)
    if user_info_updated:
        user = user_info_updated['user']
        print(f"📊 UPDATED STATS for {user['full_name']}:")
        print(f"💎 Total Points: {user['total_points']}")
        print(f"🏆 Level: {user['level']} ({user['level_name']})")
        print(f"🏅 Total Achievements: {len(user_info_updated['achievements'])}")

def test_monitor_configuration():
    """Test monitor configuration functionality"""
    db = DatabaseManager()
    
    print("\n=== MONITOR CONFIGURATION TEST ===\n")
    
    # Test getting monitor configurations for each user
    for user_id in [1, 2, 3]:
        print(f"📺 Monitor setup for User {user_id}:")
        monitors = db.get_user_monitor_config(user_id)
        
        for monitor in monitors:
            primary_text = " (PRIMARY)" if monitor['is_primary'] else ""
            print(f"  🖥️  {monitor['monitor_name']}{primary_text}")
            print(f"      Angle X: {monitor['angle_x_degrees']}°, Angle Y: {monitor['angle_y_degrees']}°")
            print(f"      Distance: {monitor['distance_cm']}cm")
        print()
    
    # Test adding new monitor configuration
    print("🔧 Testing monitor configuration update...")
    result = db.add_monitor_configuration(1, "Secondary Monitor", 45.0, -10.0, 55.0, False)
    if result['success']:
        print(f"✅ Monitor configuration {result['action']} successfully")
    
    # Test eye tracking data recording
    print("\n👁️  Testing eye tracking data recording...")
    import random
    
    # Simulate some eye tracking data for User 1
    for i in range(5):
        # Generate random gaze angles (simulating eye movement)
        gaze_x = random.uniform(-30, 30)
        gaze_y = random.uniform(-15, 15)
        confidence = random.uniform(0.7, 1.0)
        
        result = db.record_eye_tracking_data(1, gaze_x, gaze_y, confidence_score=confidence)
        if result['success']:
            print(f"  📊 Gaze recorded: ({gaze_x:.1f}°, {gaze_y:.1f}°) → {result['monitor_detected']}")
    
    # Get eye tracking statistics
    print("\n📈 Eye tracking statistics for User 1:")
    stats = db.get_eye_tracking_stats(1, limit=5)
    
    print("  Recent gaze data:")
    for data in stats['recent_data']:
        print(f"    {data['timestamp'][-8:]}: ({data['gaze_x']:.1f}°, {data['gaze_y']:.1f}°) → {data['monitor']}")
    
    print("  Monitor usage:")
    for usage in stats['monitor_usage']:
        print(f"    {usage['monitor_name']}: {usage['usage_count']} times (confidence: {usage['avg_confidence']})")

def test_database_structure():
    """Test and display database structure"""
    db = DatabaseManager()
    
    print("\n=== DATABASE STRUCTURE TEST ===\n")
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Show all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = cursor.fetchall()
            print("� DATABASE TABLES:")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Show Users table structure
            cursor.execute("PRAGMA table_info(Users)")
            users_columns = cursor.fetchall()
            print("\n👥 USERS TABLE:")
            for col in users_columns:
                print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
            
            # Show MonitorConfiguration table structure  
            cursor.execute("PRAGMA table_info(MonitorConfiguration)")
            monitor_columns = cursor.fetchall()
            print(f"\n� MONITOR_CONFIGURATION TABLE:")
            for col in monitor_columns:
                print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
            
            # Show EyeTrackingData table structure
            cursor.execute("PRAGMA table_info(EyeTrackingData)")
            eye_columns = cursor.fetchall()
            print(f"\n�️  EYE_TRACKING_DATA TABLE:")
            for col in eye_columns:
                print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
            
            # Show all users with their monitor count
            cursor.execute("""
                SELECT u.id, u.first_name, u.last_name, u.total_points, u.level,
                       COUNT(mc.id) as monitor_count
                FROM Users u
                LEFT JOIN MonitorConfiguration mc ON u.id = mc.user_id AND mc.is_active = 1
                GROUP BY u.id
            """)
            users = cursor.fetchall()
            print(f"\n👤 USERS WITH MONITOR SETUP:")
            for user in users:
                print(f"  ID: {user[0]} | {user[1]} {user[2]} | {user[3]} pts | Level {user[4]} | {user[5]} monitors")
    
    except Exception as e:
        print(f"Error testing database structure: {e}")

if __name__ == "__main__":
    test_database_structure()
    test_monitor_configuration()
    test_achievement_system()