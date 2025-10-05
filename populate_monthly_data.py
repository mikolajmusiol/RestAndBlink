#!/usr/bin/env python3
# Script to populate database with extensive monthly data

import sys
import os
import random
import json
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from game.database_manager import DatabaseManager


class DataPopulator:
    """Populate database with realistic monthly data for statistics testing."""
    
    def __init__(self):
        self.db_manager = DatabaseManager('user_data.db')
        self.user_id = 1  # Assuming user ID 1 exists
        
    def generate_realistic_heartbeat_data(self, base_heartbeat=75, duration_minutes=5):
        """Generate realistic heartbeat data for a session."""
        timestamps = []
        heartbeats = []
        stress_levels = []
        
        # Generate data points every 5 seconds
        for i in range(0, duration_minutes * 60, 5):
            timestamps.append(i)
            
            # Generate realistic heartbeat with some variation
            variation = random.randint(-8, 8)
            heartbeat = max(50, min(120, base_heartbeat + variation))
            heartbeats.append(heartbeat)
            
            # Generate stress level (higher heartbeat = potentially higher stress)
            stress_base = (heartbeat - 60) / 100  # Normalize around 60 BPM
            stress_variation = random.uniform(-0.2, 0.2)
            stress = max(0.0, min(1.0, stress_base + stress_variation))
            stress_levels.append(stress)
        
        return {
            'timestamps': timestamps,
            'heartbeats': heartbeats,
            'stress_levels': stress_levels
        }
    
    def calculate_session_metrics(self, heartbeat_data, interruptions=0):
        """Calculate session metrics from heartbeat data."""
        heartbeats = heartbeat_data['heartbeats']
        stress_levels = heartbeat_data['stress_levels']
        
        if not heartbeats:
            return {
                'avg_heartbeat': 0,
                'min_heartbeat': 0,
                'max_heartbeat': 0,
                'stress_level': 0.0,
                'rest_quality_score': 0.0
            }
        
        avg_heartbeat = sum(heartbeats) / len(heartbeats)
        min_heartbeat = min(heartbeats)
        max_heartbeat = max(heartbeats)
        avg_stress = sum(stress_levels) / len(stress_levels)
        
        # Calculate rest quality (lower is better for rest)
        heartbeat_variance = sum([(hb - avg_heartbeat) ** 2 for hb in heartbeats]) / len(heartbeats)
        rest_quality = max(0.0, min(10.0, 10.0 - (heartbeat_variance / 50) - (interruptions * 0.5)))
        
        return {
            'avg_heartbeat': avg_heartbeat,
            'min_heartbeat': min_heartbeat,
            'max_heartbeat': max_heartbeat,
            'stress_level': avg_stress,
            'rest_quality_score': rest_quality
        }
    
    def add_realistic_session(self, timestamp, exercise_type="eye_break"):
        """Add a realistic session with all data."""
        try:
            # Generate session parameters
            duration_minutes = random.choice([3, 5, 8, 10, 12])  # Realistic break durations
            time_intervals = [120, 180] if duration_minutes >= 5 else [120]  # Break intervals
            total_time = sum(time_intervals)
            
            # Generate interruptions (0-3, weighted toward fewer)
            interruptions = random.choices([0, 1, 2, 3], weights=[60, 25, 10, 5])[0]
            
            # Generate heartbeat data
            base_heartbeat = random.randint(65, 85)  # Realistic resting heart rate
            heartbeat_data = self.generate_realistic_heartbeat_data(base_heartbeat, duration_minutes)
            
            # Calculate metrics
            metrics = self.calculate_session_metrics(heartbeat_data, interruptions)
            
            # Calculate score (simple scoring based on time and quality)
            base_score = (total_time / 60) * 10  # 10 points per minute
            quality_bonus = metrics['rest_quality_score'] * 2
            interruption_penalty = interruptions * 3
            score = max(0, int(base_score + quality_bonus - interruption_penalty))
            
            # Generate session notes
            notes_options = [
                "Good rest session",
                "Good rest session with one interruption",
                "Excellent relaxation period", 
                "Brief but effective break",
                "Deep breathing exercises completed",
                "Eye exercises completed successfully",
                "Mindful break session",
                "Quick energy restoration",
                "Focused relaxation time"
            ]
            notes = random.choice(notes_options)
            if interruptions > 1:
                notes += f" - {interruptions} interruptions"
            
            # Insert session into database
            import sqlite3
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO Sessions (
                        user_id, timestamp, exercise_type, time_intervals, 
                        total_time_seconds, score, heartbeat_data, avg_heartbeat,
                        min_heartbeat, max_heartbeat, stress_level, rest_quality_score,
                        interruption_count, session_completed, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.user_id, timestamp.isoformat(), exercise_type, 
                    str(time_intervals), total_time, score, json.dumps(heartbeat_data),
                    metrics['avg_heartbeat'], metrics['min_heartbeat'], metrics['max_heartbeat'],
                    metrics['stress_level'], metrics['rest_quality_score'],
                    interruptions, 1, notes
                ))
                
                session_id = cursor.lastrowid
                conn.commit()
                
                return session_id
                
        except Exception as e:
            print(f"Error adding session for {timestamp}: {e}")
            return None
    
    def _get_connection(self):
        """Get database connection - helper method."""
        import sqlite3
        return sqlite3.connect(self.db_manager.db_path)
    
    def populate_monthly_data(self):
        """Populate database with realistic data for the entire month."""
        print("🚀 Starting monthly data population...")
        
        # Get current date and calculate month range
        today = datetime.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Generate sessions for each day of the month
        current_date = start_of_month
        total_sessions = 0
        
        while current_date <= today:
            # Determine if this is a weekday (more sessions) or weekend (fewer sessions)
            is_weekend = current_date.weekday() >= 5
            
            # Number of sessions per day (weighted)
            if is_weekend:
                daily_sessions = random.choices([0, 1, 2, 3, 4], weights=[20, 30, 25, 15, 10])[0]
            else:
                daily_sessions = random.choices([2, 3, 4, 5, 6, 7, 8], weights=[5, 10, 20, 25, 20, 15, 5])[0]
            
            print(f"📅 Generating {daily_sessions} sessions for {current_date.strftime('%Y-%m-%d')}")
            
            # Generate sessions throughout the day
            for session_num in range(daily_sessions):
                # Generate realistic times (working hours with some variation)
                if is_weekend:
                    # Weekend sessions more spread out
                    hour = random.randint(9, 20)
                else:
                    # Workday sessions during work hours
                    hour = random.choices(
                        range(8, 19), 
                        weights=[5, 10, 15, 20, 15, 20, 25, 20, 15, 10, 5]  # Peak around lunch/afternoon
                    )[0]
                
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                
                session_time = current_date.replace(hour=hour, minute=minute, second=second)
                
                # Add some variation to session times to avoid clustering
                session_time += timedelta(minutes=random.randint(-30, 30))
                
                # Ensure we don't go beyond today
                if session_time > today:
                    continue
                
                # Choose exercise type
                exercise_types = ["eye_break", "stretch_break", "breathing_exercise", "mindfulness"]
                exercise_type = random.choices(
                    exercise_types, 
                    weights=[50, 25, 15, 10]  # Eye breaks most common
                )[0]
                
                session_id = self.add_realistic_session(session_time, exercise_type)
                if session_id:
                    total_sessions += 1
            
            current_date += timedelta(days=1)
        
        print(f"✅ Successfully added {total_sessions} sessions to the database")
        
        # Update user statistics
        self.update_user_stats()
        
        # Add some achievements data
        self.add_achievement_data()
        
        print("🎉 Monthly data population completed!")
    
    def update_user_stats(self):
        """Update user statistics based on sessions."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get total stats
                cursor.execute('''
                    SELECT COUNT(*), SUM(total_time_seconds), SUM(score)
                    FROM Sessions WHERE user_id = ?
                ''', (self.user_id,))
                
                result = cursor.fetchone()
                total_sessions = result[0] or 0
                total_time = result[1] or 0
                total_points = result[2] or 0
                
                # Calculate level and experience
                level = min(10, max(1, total_points // 100))
                experience_points = total_points
                
                # Update user record
                cursor.execute('''
                    UPDATE Users SET 
                    total_points = ?, total_sessions = ?, total_time_seconds = ?,
                    level = ?, experience_points = ?, last_activity = ?
                    WHERE id = ?
                ''', (total_points, total_sessions, total_time, level, experience_points, 
                      datetime.now().isoformat(), self.user_id))
                
                conn.commit()
                print(f"📊 Updated user stats: {total_sessions} sessions, {total_points} points, level {level}")
                
        except Exception as e:
            print(f"Error updating user stats: {e}")
    
    def add_achievement_data(self):
        """Add some sample achievements."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if achievements exist
                cursor.execute("SELECT COUNT(*) FROM Achievements")
                achievement_count = cursor.fetchone()[0]
                
                if achievement_count == 0:
                    # Add sample achievements
                    achievements = [
                        ("First Break", "Complete your first break session", "sessions", 1, 10),
                        ("Dedicated User", "Complete 10 break sessions", "sessions", 10, 25),
                        ("Break Master", "Complete 50 break sessions", "sessions", 50, 100),
                        ("Time Manager", "Spend 1 hour in break sessions", "time", 3600, 50),
                        ("Wellness Warrior", "Spend 5 hours in break sessions", "time", 18000, 150),
                    ]
                    
                    for name, desc, req_type, req_value, points in achievements:
                        cursor.execute('''
                            INSERT INTO Achievements (name, description, requirement_type, 
                                                    requirement_value, points_reward, created_date)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (name, desc, req_type, req_value, points, datetime.now().isoformat()))
                    
                    conn.commit()
                    print("🏆 Added sample achievements")
                
        except Exception as e:
            print(f"Error adding achievements: {e}")


def main():
    """Main function to populate the database."""
    print("📊 Database Population Script")
    print("=" * 50)
    
    # Check if database exists
    if not os.path.exists('user_data.db'):
        print("❌ Error: user_data.db not found!")
        print("Please make sure the database file exists in the current directory.")
        return 1
    
    # Create populator and run
    populator = DataPopulator()
    
    try:
        populator.populate_monthly_data()
        print("\n✅ Database population completed successfully!")
        print("\n📈 You can now view comprehensive statistics in the stats tabs:")
        print("   • Daily stats with rich seaborn visualizations")
        print("   • Weekly trends and patterns")  
        print("   • Monthly analysis and heatmaps")
        print("   • All-time comprehensive statistics")
        
    except Exception as e:
        print(f"\n❌ Error during population: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())