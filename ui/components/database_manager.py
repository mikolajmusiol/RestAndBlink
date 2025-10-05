import sqlite3
import json
from datetime import datetime, timedelta


class DatabaseManager:
    """Handles all database operations for the wellness application."""
    
    def __init__(self, db_path="user_data.db"):
        self.db_path = db_path
    
    def get_user_data(self, user_id):
        """Get user data from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT first_name, last_name, level, total_points, total_sessions
                FROM Users WHERE id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'first_name': result[0],
                    'last_name': result[1],
                    'level': result[2],
                    'total_points': result[3],
                    'total_sessions': result[4]
                }
            else:
                return {
                    'first_name': 'User',
                    'last_name': '',
                    'level': 1,
                    'total_points': 0,
                    'total_sessions': 0
                }
        except Exception as e:
            print(f"Error getting user data: {e}")
            return {
                'first_name': 'User',
                'last_name': '',
                'level': 1,
                'total_points': 0,
                'total_sessions': 0
            }
    
    def get_achievements_data(self, user_id):
        """Get achievements data from database."""
        earned_achievements = []
        all_achievements = []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get earned achievements
            cursor.execute("""
                SELECT a.id, a.name, a.description, a.badge_icon, a.rarity, ua.earned_date
                FROM Achievements a
                JOIN UserAchievements ua ON a.id = ua.achievement_id
                WHERE ua.user_id = ?
                ORDER BY ua.earned_date DESC
            """, (user_id,))

            for row in cursor.fetchall():
                earned_achievements.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'badge_icon': row[3],
                    'rarity': row[4],
                    'earned_date': row[5]
                })

            # Get all achievements
            cursor.execute("""
                SELECT id, name, description, badge_icon, rarity
                FROM Achievements
                WHERE is_active = 1
                ORDER BY id
            """)

            for row in cursor.fetchall():
                all_achievements.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'badge_icon': row[3],
                    'rarity': row[4]
                })

            conn.close()

        except Exception as e:
            print(f"Error fetching achievements data: {e}")

        return earned_achievements, all_achievements
    
    def get_enhanced_period_data(self, user_id, period):
        """Get enhanced data for charts."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Define date ranges
            today = datetime.now()
            
            if period == "daily":
                start_date = today.strftime('%Y-%m-%d')
                end_date = start_date
                print(f"🔍 DEBUG Daily: start_date={start_date}, end_date={end_date}")
            elif period == "weekly":
                start_of_week = today - timedelta(days=today.weekday())
                start_date = start_of_week.strftime('%Y-%m-%d')
                end_date = (start_of_week + timedelta(days=6)).strftime('%Y-%m-%d')
            elif period == "monthly":
                start_date = today.replace(day=1).strftime('%Y-%m-%d')
                end_date = today.strftime('%Y-%m-%d')
            else:  # alltime
                start_date = "2000-01-01"
                end_date = today.strftime('%Y-%m-%d')
            
            # Get sessions with heartbeat data
            cursor.execute("""
                SELECT heartbeat_data, total_time_seconds, score, timestamp
                FROM Sessions 
                WHERE user_id = ? AND DATE(timestamp) BETWEEN ? AND ?
                ORDER BY timestamp
            """, (user_id, start_date, end_date))
            
            sessions = cursor.fetchall()
            conn.close()
            
            print(f"🔍 Found {len(sessions)} sessions for period '{period}'")
            if sessions:
                print(f"🔍 First session heartbeat_data: {repr(sessions[0][0])}")
            
            if not sessions:
                return []
            
            chart_data = []
            
            for session in sessions[:20]:  # Limit to first 20 sessions for performance
                try:
                    if session[0] is None:
                        # Jeśli heartbeat_data to None, użyj domyślnych wartości
                        avg_heartbeat = 0
                        avg_stress = 0
                    else:
                        # PARSUJ JAKO CSV ZAMIAST JSON
                        heartbeat_data_str = session[0]
                        try:
                            # Spróbuj najpierw jako JSON (dla starych danych)
                            heartbeat_json = json.loads(heartbeat_data_str)
                            heartbeats = heartbeat_json.get('heartbeats', [])
                            stress_levels = heartbeat_json.get('stress_levels', [])
                            
                            if heartbeats and stress_levels:
                                avg_heartbeat = sum(heartbeats) / len(heartbeats)
                                avg_stress = sum(stress_levels) / len(stress_levels)
                            else:
                                avg_heartbeat = 0
                                avg_stress = 0
                        except json.JSONDecodeError:
                            # Parsuj jako CSV (dla nowych danych)
                            heartbeats = [float(x.strip()) for x in heartbeat_data_str.split(',') if x.strip()]
                            if heartbeats:
                                avg_heartbeat = sum(heartbeats) / len(heartbeats)
                                # Oblicz stress na podstawie zmienności tętna
                                heartbeat_var = sum((h - avg_heartbeat) ** 2 for h in heartbeats) / len(heartbeats)
                                avg_stress = min(100, max(0, heartbeat_var * 2)) / 100  # Scale to 0-1
                            else:
                                avg_heartbeat = 0
                                avg_stress = 0
                    
                    chart_data.append({
                        'heartbeat': avg_heartbeat,
                        'stress': avg_stress,
                        'duration': session[1],
                        'score': session[2],
                        'timestamp': session[3]
                    })
                            
                except (json.JSONDecodeError, TypeError):
                    # Jeśli błąd parsowania, użyj zer
                    chart_data.append({
                        'heartbeat': 0,
                        'stress': 0,
                        'duration': session[1],
                        'score': session[2],
                        'timestamp': session[3]
                    })
            
            return chart_data
            
        except Exception as e:
            print(f"Error getting enhanced period data: {e}")
            return []
    
    def get_period_stats(self, user_id, period):
        """Get basic statistics for a period."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Define date ranges
            today = datetime.now()
            
            if period == "daily":
                start_date = today.strftime('%Y-%m-%d')
                end_date = start_date
            elif period == "weekly":
                start_of_week = today - timedelta(days=today.weekday())
                start_date = start_of_week.strftime('%Y-%m-%d')
                end_date = (start_of_week + timedelta(days=6)).strftime('%Y-%m-%d')
            elif period == "monthly":
                start_date = today.replace(day=1).strftime('%Y-%m-%d')
                end_date = today.strftime('%Y-%m-%d')
            else:  # alltime
                start_date = "2000-01-01"
                end_date = today.strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT SUM(total_time_seconds), SUM(score), COUNT(*)
                FROM Sessions 
                WHERE user_id = ? AND DATE(timestamp) BETWEEN ? AND ?
            """, (user_id, start_date, end_date))
            
            result = cursor.fetchone()
            conn.close()
            
            return {
                'total_time': result[0] or 0,
                'total_score': result[1] or 0,
                'total_sessions': result[2] or 0
            }
            
        except Exception as e:
            print(f"Error getting period stats: {e}")
            return {'total_time': 0, 'total_score': 0, 'total_sessions': 0}
    
    def save_calibration_data(self, monitor, head_pose, left_eye, right_eye):
        """Save calibration data to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            head_yaw, head_pitch, head_roll = head_pose if head_pose else (None, None, None)
            left_x, left_y = left_eye if left_eye else (None, None)
            right_x, right_y = right_eye if right_eye else (None, None)
            created_at = datetime.now().isoformat(timespec='seconds')

            cursor.execute('''
                INSERT INTO calibration_templates 
                (monitor, head_yaw, head_pitch, head_roll, left_x, left_y, right_x, right_y, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (monitor, head_yaw, head_pitch, head_roll, left_x, left_y, right_x, right_y, created_at))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving calibration data: {e}")
            return False