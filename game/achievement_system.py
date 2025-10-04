import sqlite3
from database_manager import DatabaseManager

class AchievementSystem:
    def __init__(self, db_path='../user_data.db'):
        self.db_path = db_path
        # Initialize database if needed
        self.db_manager = DatabaseManager(db_path)
    
    def get_all_achievements(self):
        """Get all available achievements"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Achievements")
                achievements = cursor.fetchall()
                return achievements
        except sqlite3.Error as e:
            print(f"Error reading achievements: {e}")
            return []
    
    def get_user_achievements(self, user_id):
        """Get achievements earned by a specific user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT a.*, ua.earned_date 
                    FROM Achievements a
                    JOIN UserAchievements ua ON a.id = ua.achievement_id
                    WHERE ua.user_id = ?
                ''', (user_id,))
                achievements = cursor.fetchall()
                return achievements
        except sqlite3.Error as e:
            print(f"Error reading user achievements: {e}")
            return []
    
    def check_achievement_progress(self, user_id):
        """Check progress towards achievements for a user and award new ones"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get user's current stats
                cursor.execute('''
                    SELECT total_points, total_sessions, total_time_seconds 
                    FROM Users WHERE id = ?
                ''', (user_id,))
                user_stats = cursor.fetchone()
                
                if not user_stats:
                    print(f"User {user_id} not found")
                    return {}
                
                total_points, total_sessions, total_time = user_stats
                
                print(f"User {user_id} progress:")
                print(f"- Total points: {total_points}")
                print(f"- Sessions completed: {total_sessions}")
                print(f"- Total exercise time: {total_time} seconds ({total_time/60:.1f} minutes)")
                
                # Check for new achievements
                newly_earned = self.check_and_award_achievements(user_id, total_points, total_sessions, total_time)
                
                return {
                    'total_points': total_points,
                    'total_sessions': total_sessions,
                    'total_time': total_time,
                    'newly_earned': newly_earned
                }
                
        except sqlite3.Error as e:
            print(f"Error checking achievement progress: {e}")
            return {}
    
    def check_and_award_achievements(self, user_id, total_points, total_sessions, total_time):
        """Check and award achievements based on user stats"""
        newly_earned = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get all achievements user doesn't have yet
                cursor.execute('''
                    SELECT a.* FROM Achievements a
                    WHERE a.id NOT IN (
                        SELECT achievement_id FROM UserAchievements WHERE user_id = ?
                    )
                ''', (user_id,))
                
                available_achievements = cursor.fetchall()
                
                for achievement in available_achievements:
                    achievement_id, name, description, req_type, req_value, points = achievement
                    
                    # Check if requirements are met
                    earned = False
                    if req_type == 'points' and total_points >= req_value:
                        earned = True
                    elif req_type == 'sessions' and total_sessions >= req_value:
                        earned = True
                    elif req_type == 'total_time' and total_time >= req_value:
                        earned = True
                    
                    if earned:
                        # Award the achievement
                        if self.db_manager.award_achievement(user_id, achievement_id):
                            newly_earned.append((name, description, points))
                            print(f"🏆 New achievement earned: {name}")
                
                return newly_earned
                
        except sqlite3.Error as e:
            print(f"Error checking achievements: {e}")
            return []

if __name__ == "__main__":
    # Test the achievement system
    achievement_system = AchievementSystem()
    
    print("=== All Achievements ===")
    achievements = achievement_system.get_all_achievements()
    for achievement in achievements:
        print(f"ID: {achievement[0]}, Name: {achievement[1]}, Description: {achievement[2]}")
    
    print("\n=== User Progress (User ID: 1) ===")
    progress = achievement_system.check_achievement_progress(1)