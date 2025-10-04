import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path='../user_data.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create Users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        total_points INTEGER DEFAULT 0,
                        total_sessions INTEGER DEFAULT 0,
                        total_time_seconds INTEGER DEFAULT 0,
                        created_date TEXT,
                        last_activity TEXT
                    )
                ''')
                
                # Create Sessions table for exercise tracking
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        timestamp TEXT,
                        exercise_type TEXT,
                        time_intervals TEXT,
                        total_time_seconds INTEGER,
                        score INTEGER,
                        FOREIGN KEY (user_id) REFERENCES Users (id)
                    )
                ''')
                
                # Create Achievements table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Achievements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        requirement_type TEXT,
                        requirement_value INTEGER,
                        points INTEGER
                    )
                ''')
                
                # Create UserAchievements table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS UserAchievements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        achievement_id INTEGER,
                        earned_date TEXT,
                        FOREIGN KEY (user_id) REFERENCES Users (id),
                        FOREIGN KEY (achievement_id) REFERENCES Achievements (id)
                    )
                ''')
                
                conn.commit()
                print(f"Database initialized successfully: {self.db_path}")
                
                # Add sample data if tables are empty
                self.add_sample_data()
                
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
    
    def add_sample_data(self):
        """Add sample data if tables are empty"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if Users table is empty
                cursor.execute("SELECT COUNT(*) FROM Users")
                if cursor.fetchone()[0] == 0:
                    from datetime import datetime
                    current_time = datetime.now().isoformat()
                    cursor.execute('''
                        INSERT INTO Users (name, total_points, total_sessions, total_time_seconds, created_date, last_activity) VALUES 
                        ('Alice', 150, 8, 2400, ?, ?),
                        ('Bob', 85, 5, 1500, ?, ?),
                        ('Charlie', 320, 15, 4500, ?, ?)
                    ''', (current_time, current_time, current_time, current_time, current_time, current_time))
                    print("Added sample users with points")
                
                # Check if Achievements table is empty
                cursor.execute("SELECT COUNT(*) FROM Achievements")
                if cursor.fetchone()[0] == 0:
                    achievements = [
                        # Session-based achievements
                        ('First Steps', 'Complete your first exercise session', 'sessions', 1, 10),
                        ('Getting Started', 'Complete 5 exercise sessions', 'sessions', 5, 25),
                        ('Dedicated', 'Complete 10 exercise sessions', 'sessions', 10, 50),
                        ('Regular User', 'Complete 25 exercise sessions', 'sessions', 25, 100),
                        ('Marathon', 'Complete 50 exercise sessions', 'sessions', 50, 200),
                        ('Century Club', 'Complete 100 exercise sessions', 'sessions', 100, 500),
                        
                        # Points-based achievements
                        ('Point Starter', 'Earn 50 points', 'points', 50, 20),
                        ('Point Collector', 'Earn 100 points', 'points', 100, 50),
                        ('Point Hunter', 'Earn 200 points', 'points', 200, 100),
                        ('Point Master', 'Earn 500 points', 'points', 500, 250),
                        ('Point Legend', 'Earn 1000 points', 'points', 1000, 500),
                        ('Point God', 'Earn 2000 points', 'points', 2000, 1000),
                        ('Ultimate Achiever', 'Earn 5000 points', 'points', 5000, 2500),
                        
                        # Time-based achievements
                        ('Time Novice', 'Exercise for 30 minutes total', 'total_time', 1800, 50),
                        ('Time Master', 'Exercise for 60 minutes total', 'total_time', 3600, 100),
                        ('Time Champion', 'Exercise for 2 hours total', 'total_time', 7200, 200),
                        ('Time Elite', 'Exercise for 5 hours total', 'total_time', 18000, 500),
                        
                        # Streak achievements
                        ('Consistency Starter', 'Exercise 3 days in a row', 'streak', 3, 75),
                        ('Consistency King', 'Exercise 7 days in a row', 'streak', 7, 150),
                        ('Consistency Legend', 'Exercise 14 days in a row', 'streak', 14, 300),
                        ('Consistency God', 'Exercise 30 days in a row', 'streak', 30, 750)
                    ]
                    cursor.executemany('''
                        INSERT INTO Achievements (name, description, requirement_type, requirement_value, points)
                        VALUES (?, ?, ?, ?, ?)
                    ''', achievements)
                    print("Added comprehensive achievements")
                
                conn.commit()
                
        except sqlite3.Error as e:
            print(f"Error adding sample data: {e}")
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def add_points_to_user(self, user_id, points):
        """Add points to a user and update their stats"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                from datetime import datetime
                
                cursor.execute('''
                    UPDATE Users 
                    SET total_points = total_points + ?, 
                        last_activity = ?
                    WHERE id = ?
                ''', (points, datetime.now().isoformat(), user_id))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error adding points: {e}")
            return False
    
    def update_user_session_stats(self, user_id, time_seconds):
        """Update user's session count and total time"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                from datetime import datetime
                
                cursor.execute('''
                    UPDATE Users 
                    SET total_sessions = total_sessions + 1,
                        total_time_seconds = total_time_seconds + ?,
                        last_activity = ?
                    WHERE id = ?
                ''', (time_seconds, datetime.now().isoformat(), user_id))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error updating user stats: {e}")
            return False
    
    def get_user_stats(self, user_id):
        """Get user's current stats"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, total_points, total_sessions, total_time_seconds
                    FROM Users WHERE id = ?
                ''', (user_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'id': result[0],
                        'name': result[1],
                        'total_points': result[2],
                        'total_sessions': result[3],
                        'total_time_seconds': result[4]
                    }
                return None
        except sqlite3.Error as e:
            print(f"Error getting user stats: {e}")
            return None
    
    def award_achievement(self, user_id, achievement_id):
        """Award an achievement to a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                from datetime import datetime
                
                # Check if user already has this achievement
                cursor.execute('''
                    SELECT COUNT(*) FROM UserAchievements 
                    WHERE user_id = ? AND achievement_id = ?
                ''', (user_id, achievement_id))
                
                if cursor.fetchone()[0] == 0:
                    # Award the achievement
                    cursor.execute('''
                        INSERT INTO UserAchievements (user_id, achievement_id, earned_date)
                        VALUES (?, ?, ?)
                    ''', (user_id, achievement_id, datetime.now().isoformat()))
                    
                    conn.commit()
                    return True
                return False
        except sqlite3.Error as e:
            print(f"Error awarding achievement: {e}")
            return False

if __name__ == "__main__":
    # Initialize database
    db_manager = DatabaseManager()
    print("Database setup complete!")