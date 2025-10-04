#!/usr/bin/env python3
# Extended script to populate database with comprehensive data

import sys
import os
import random
import json
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from game.database_manager import DatabaseManager


def populate_extended_data():
    """Populate database with extensive data spanning multiple weeks."""
    print("🚀 Starting extended data population (last 30 days)...")
    
    db_manager = DatabaseManager('user_data.db')
    user_id = 1
    
    # Generate data for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    current_date = start_date
    total_sessions = 0
    
    while current_date <= end_date:
        # Skip some days randomly to make it more realistic
        if random.random() < 0.1:  # 10% chance to skip a day
            current_date += timedelta(days=1)
            continue
            
        # Determine if this is a weekday (more sessions) or weekend (fewer sessions)
        is_weekend = current_date.weekday() >= 5
        
        # Number of sessions per day (weighted)
        if is_weekend:
            daily_sessions = random.choices([0, 1, 2, 3, 4, 5], weights=[10, 20, 30, 20, 15, 5])[0]
        else:
            daily_sessions = random.choices([2, 3, 4, 5, 6, 7, 8, 9], weights=[5, 10, 15, 25, 20, 15, 8, 2])[0]
        
        print(f"📅 Generating {daily_sessions} sessions for {current_date.strftime('%Y-%m-%d')} ({'Weekend' if is_weekend else 'Weekday'})")
        
        # Generate sessions throughout the day
        session_times = []
        for session_num in range(daily_sessions):
            # Generate realistic times (working hours with some variation)
            if is_weekend:
                # Weekend sessions more spread out (9 AM - 8 PM)
                hour = random.randint(9, 20)
            else:
                # Workday sessions during work hours with peaks
                hour = random.choices(
                    list(range(8, 19)), 
                    weights=[5, 8, 12, 15, 18, 20, 25, 22, 18, 15, 8]  # Peak around 10AM-2PM
                )[0]
            
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            session_time = current_date.replace(hour=hour, minute=minute, second=second)
            
            # Add some variation to avoid exact clustering
            session_time += timedelta(minutes=random.randint(-20, 20))
            
            # Ensure we don't go beyond end_date or before start_date
            if session_time > end_date or session_time < start_date:
                continue
                
            session_times.append(session_time)
        
        # Sort sessions by time and add them
        session_times.sort()
        
        for session_time in session_times:
            # Choose exercise type with realistic distribution
            exercise_types = ["eye_break", "stretch_break", "breathing_exercise", "mindfulness", "posture_check"]
            exercise_type = random.choices(
                exercise_types, 
                weights=[45, 20, 15, 10, 10]  # Eye breaks most common
            )[0]
            
            # Generate session parameters
            duration_minutes = random.choices([3, 5, 8, 10, 12, 15], weights=[10, 30, 25, 20, 10, 5])[0]
            time_intervals = [120, 180] if duration_minutes >= 5 else [90, 120]
            total_time = sum(time_intervals)
            
            # Generate interruptions (weighted toward fewer)
            interruptions = random.choices([0, 1, 2, 3, 4], weights=[50, 30, 15, 4, 1])[0]
            
            # Generate realistic heartbeat data
            base_heartbeat = random.randint(62, 88)  # Realistic resting heart rate range
            
            # Time of day affects base heartbeat slightly
            if session_time.hour < 10:  # Morning - slightly lower
                base_heartbeat -= random.randint(0, 5)
            elif session_time.hour > 16:  # Evening - slightly higher
                base_heartbeat += random.randint(0, 5)
            
            # Generate heartbeat data points
            timestamps = []
            heartbeats = []
            stress_levels = []
            
            for i in range(0, duration_minutes * 60, 5):
                timestamps.append(i)
                
                # Generate realistic heartbeat with gradual changes
                if i == 0:
                    heartbeat = base_heartbeat
                else:
                    # Small changes from previous reading
                    change = random.randint(-3, 3)
                    heartbeat = max(55, min(110, heartbeats[-1] + change))
                
                heartbeats.append(heartbeat)
                
                # Generate stress level correlated with heartbeat changes
                if len(heartbeats) > 1:
                    heartbeat_change = abs(heartbeats[-1] - heartbeats[-2])
                    stress_base = (heartbeat - 65) / 50  # Normalize around 65 BPM
                    stress_variation = random.uniform(-0.15, 0.15)
                    stress_spike = heartbeat_change * 0.02  # Spikes from heartbeat changes
                    stress = max(0.0, min(1.0, stress_base + stress_variation + stress_spike))
                else:
                    stress = random.uniform(0.1, 0.4)  # Initial stress level
                
                stress_levels.append(stress)
            
            heartbeat_data = {
                'timestamps': timestamps,
                'heartbeats': heartbeats,
                'stress_levels': stress_levels
            }
            
            # Calculate metrics
            if heartbeats:
                avg_heartbeat = sum(heartbeats) / len(heartbeats)
                min_heartbeat = min(heartbeats)
                max_heartbeat = max(heartbeats)
                avg_stress = sum(stress_levels) / len(stress_levels)
                
                # Calculate rest quality (multiple factors)
                heartbeat_variance = sum([(hb - avg_heartbeat) ** 2 for hb in heartbeats]) / len(heartbeats)
                stress_penalty = avg_stress * 2
                interruption_penalty = interruptions * 0.8
                time_bonus = min(2, total_time / 300)  # Bonus for longer sessions
                
                rest_quality = max(0.0, min(10.0, 8.0 - (heartbeat_variance / 25) - stress_penalty - interruption_penalty + time_bonus))
            else:
                avg_heartbeat = min_heartbeat = max_heartbeat = 0
                avg_stress = rest_quality = 0.0
            
            # Calculate score with multiple factors
            base_score = (total_time / 60) * 8  # 8 points per minute
            quality_bonus = rest_quality * 3
            stress_bonus = (1 - avg_stress) * 10  # Lower stress = higher bonus
            interruption_penalty = interruptions * 4
            consistency_bonus = 5 if session_times.index(session_time) < len(session_times) - 1 else 0
            
            score = max(5, int(base_score + quality_bonus + stress_bonus - interruption_penalty + consistency_bonus))
            
            # Generate contextual notes
            quality_descriptions = ["Excellent", "Very good", "Good", "Fair", "Poor"]
            quality_desc = quality_descriptions[min(4, int(rest_quality / 2))]
            
            stress_descriptions = ["Very relaxed", "Relaxed", "Moderate", "Elevated", "High stress"]
            stress_desc = stress_descriptions[min(4, int(avg_stress * 5))]
            
            notes_templates = [
                f"{quality_desc} rest session - {stress_desc}",
                f"{exercise_type.replace('_', ' ').title()} completed - {quality_desc.lower()} quality",
                f"Break session with {stress_desc.lower()} stress levels",
                f"{quality_desc} relaxation period"
            ]
            
            notes = random.choice(notes_templates)
            if interruptions > 0:
                notes += f" ({interruptions} interruption{'s' if interruptions > 1 else ''})"

            # Insert session directly into database
            try:
                import sqlite3
                with sqlite3.connect('user_data.db') as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO Sessions (
                            user_id, timestamp, exercise_type, time_intervals, 
                            total_time_seconds, score, heartbeat_data, avg_heartbeat,
                            min_heartbeat, max_heartbeat, stress_level, rest_quality_score,
                            interruption_count, session_completed, notes
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        user_id, session_time.isoformat(), exercise_type, 
                        str(time_intervals), total_time, score, json.dumps(heartbeat_data),
                        avg_heartbeat, min_heartbeat, max_heartbeat,
                        avg_stress, rest_quality, interruptions, 1, notes
                    ))
                    
                    conn.commit()
                    total_sessions += 1
                    
            except Exception as e:
                print(f"Error adding session for {session_time}: {e}")
        
        current_date += timedelta(days=1)
    
    print(f"✅ Successfully added {total_sessions} sessions spanning 30 days")
    
    # Update user statistics
    try:
        import sqlite3
        with sqlite3.connect('user_data.db') as conn:
            cursor = conn.cursor()
            
            # Get total stats
            cursor.execute('''
                SELECT COUNT(*), SUM(total_time_seconds), SUM(score), 
                       AVG(rest_quality_score), AVG(stress_level)
                FROM Sessions WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            total_sessions_db = result[0] or 0
            total_time = result[1] or 0
            total_points = result[2] or 0
            avg_quality = result[3] or 0
            avg_stress = result[4] or 0
            
            # Calculate level progression
            level = min(20, max(1, total_points // 150))
            experience_points = total_points
            
            # Calculate streaks (simplified)
            current_streak = random.randint(3, 12)
            longest_streak = max(current_streak, random.randint(5, 25))
            
            # Update user record
            cursor.execute('''
                UPDATE Users SET 
                total_points = ?, total_sessions = ?, total_time_seconds = ?,
                current_streak = ?, longest_streak = ?, level = ?, experience_points = ?, 
                last_activity = ?
                WHERE id = ?
            ''', (total_points, total_sessions_db, total_time, current_streak, longest_streak,
                  level, experience_points, datetime.now().isoformat(), user_id))
            
            conn.commit()
            
            hours = total_time // 3600
            minutes = (total_time % 3600) // 60
            
            print(f"\n📊 Final Statistics:")
            print(f"   • Total sessions: {total_sessions_db}")
            print(f"   • Total time: {hours}h {minutes}m") 
            print(f"   • Total points: {total_points}")
            print(f"   • Average quality: {avg_quality:.1f}/10")
            print(f"   • Average stress: {avg_stress:.2f}")
            print(f"   • Level: {level}")
            print(f"   • Current streak: {current_streak} days")
            print(f"   • Longest streak: {longest_streak} days")
            
    except Exception as e:
        print(f"Error updating user stats: {e}")
    
    print("\n🎉 Extended data population completed!")
    print("\n📈 The statistics tabs now have rich data to display:")
    print("   • Daily: Multiple sessions with heartbeat and stress data")
    print("   • Weekly: Patterns across different days")
    print("   • Monthly: Comprehensive trends and analysis")
    print("   • All-time: Full historical overview with correlations")


if __name__ == "__main__":
    populate_extended_data()