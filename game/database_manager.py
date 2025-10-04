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
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        total_points INTEGER DEFAULT 0,
                        total_sessions INTEGER DEFAULT 0,
                        total_time_seconds INTEGER DEFAULT 0,
                        current_streak INTEGER DEFAULT 0,
                        longest_streak INTEGER DEFAULT 0,
                        level INTEGER DEFAULT 1,
                        experience_points INTEGER DEFAULT 0,
                        created_date TEXT NOT NULL,
                        last_activity TEXT,
                        is_active BOOLEAN DEFAULT 1
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
                        name TEXT NOT NULL UNIQUE,
                        description TEXT NOT NULL,
                        requirement_type TEXT NOT NULL,
                        requirement_value INTEGER NOT NULL,
                        points_reward INTEGER DEFAULT 0,
                        badge_icon TEXT,
                        rarity TEXT DEFAULT 'common',
                        is_active BOOLEAN DEFAULT 1,
                        created_date TEXT NOT NULL
                    )
                ''')
                
                # Create UserAchievements table - junction table for many-to-many relationship
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS UserAchievements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        achievement_id INTEGER NOT NULL,
                        earned_date TEXT NOT NULL,
                        points_awarded INTEGER DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE,
                        FOREIGN KEY (achievement_id) REFERENCES Achievements (id) ON DELETE CASCADE,
                        UNIQUE(user_id, achievement_id)
                    )
                ''')
                
                # Create index for better performance
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_user_achievements 
                    ON UserAchievements (user_id, achievement_id)
                ''')
                
                # Create UserStats table for daily/weekly tracking
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS UserStats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        date TEXT NOT NULL,
                        daily_sessions INTEGER DEFAULT 0,
                        daily_time_seconds INTEGER DEFAULT 0,
                        daily_points INTEGER DEFAULT 0,
                        streak_day INTEGER DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE,
                        UNIQUE(user_id, date)
                    )
                ''')
                
                # Create UserLevels table for level progression
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS UserLevels (
                        level INTEGER PRIMARY KEY,
                        experience_required INTEGER NOT NULL,
                        level_name TEXT NOT NULL,
                        bonus_multiplier REAL DEFAULT 1.0
                    )
                ''')
                
                # Create MonitorConfiguration table for user monitor positions
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS MonitorConfiguration (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        monitor_name TEXT NOT NULL,
                        angle_x_degrees REAL NOT NULL,
                        angle_y_degrees REAL NOT NULL,
                        distance_cm REAL DEFAULT 60.0,
                        is_primary BOOLEAN DEFAULT 0,
                        created_date TEXT NOT NULL,
                        last_updated TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE,
                        UNIQUE(user_id, monitor_name)
                    )
                ''')
                
                # Create EyeTrackingData table for storing gaze tracking history
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS EyeTrackingData (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        session_id INTEGER,
                        timestamp TEXT NOT NULL,
                        gaze_angle_x REAL NOT NULL,
                        gaze_angle_y REAL NOT NULL,
                        monitor_detected TEXT,
                        confidence_score REAL DEFAULT 0.0,
                        FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE,
                        FOREIGN KEY (session_id) REFERENCES Sessions (id) ON DELETE SET NULL
                    )
                ''')
                
                # Create index for eye tracking performance
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_eye_tracking_user_time 
                    ON EyeTrackingData (user_id, timestamp)
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
                
                # Add level progression data
                cursor.execute("SELECT COUNT(*) FROM UserLevels")
                if cursor.fetchone()[0] == 0:
                    levels = [
                        (1, 0, 'Beginner', 1.0),
                        (2, 100, 'Novice', 1.1),
                        (3, 250, 'Apprentice', 1.2),
                        (4, 500, 'Journeyman', 1.3),
                        (5, 1000, 'Expert', 1.4),
                        (6, 2000, 'Master', 1.5),
                        (7, 4000, 'Grandmaster', 1.6),
                        (8, 8000, 'Legend', 1.7),
                        (9, 15000, 'Champion', 1.8),
                        (10, 25000, 'Ultimate', 2.0)
                    ]
                    cursor.executemany('''
                        INSERT INTO UserLevels (level, experience_required, level_name, bonus_multiplier)
                        VALUES (?, ?, ?, ?)
                    ''', levels)
                    print("Added level progression system")

                # Check if Users table is empty
                cursor.execute("SELECT COUNT(*) FROM Users")
                if cursor.fetchone()[0] == 0:
                    from datetime import datetime
                    current_time = datetime.now().isoformat()
                    users = [
                        ('Anna', 'Kowalska', 150, 8, 2400, 3, 5, 2, 150, current_time, current_time, 1),
                        ('Jan', 'Nowak', 85, 5, 1500, 1, 2, 1, 85, current_time, current_time, 1),
                        ('Piotr', 'Wiśniewski', 320, 15, 4500, 7, 10, 3, 320, current_time, current_time, 1)
                    ]
                    cursor.executemany('''
                        INSERT INTO Users (first_name, last_name, total_points, total_sessions, 
                                         total_time_seconds, current_streak, longest_streak, level, 
                                         experience_points, created_date, last_activity, is_active) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', users)
                    print("Added sample users with complete profiles")
                
                # Add sample monitor configurations
                cursor.execute("SELECT COUNT(*) FROM MonitorConfiguration")
                if cursor.fetchone()[0] == 0:
                    from datetime import datetime
                    config_time = datetime.now().isoformat()
                    monitor_configs = [
                        # User 1 (Anna) - single monitor setup
                        (1, 'Primary Monitor', 0.0, 0.0, 60.0, 1, config_time, config_time, 1),
                        
                        # User 2 (Jan) - dual monitor setup
                        (2, 'Left Monitor', -25.0, 0.0, 65.0, 0, config_time, config_time, 1),
                        (2, 'Right Monitor', 25.0, 0.0, 65.0, 1, config_time, config_time, 1),
                        
                        # User 3 (Piotr) - triple monitor setup
                        (3, 'Left Monitor', -35.0, 0.0, 70.0, 0, config_time, config_time, 1),
                        (3, 'Center Monitor', 0.0, 0.0, 60.0, 1, config_time, config_time, 1),
                        (3, 'Right Monitor', 35.0, 0.0, 70.0, 0, config_time, config_time, 1)
                    ]
                    cursor.executemany('''
                        INSERT INTO MonitorConfiguration (user_id, monitor_name, angle_x_degrees, angle_y_degrees, 
                                                        distance_cm, is_primary, created_date, last_updated, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', monitor_configs)
                    print("Added sample monitor configurations")
                
                # Check if Achievements table is empty
                cursor.execute("SELECT COUNT(*) FROM Achievements")
                if cursor.fetchone()[0] == 0:
                    from datetime import datetime
                    current_time = datetime.now().isoformat()
                    achievements = [
                        # Session-based achievements (achievements earned for completing sessions)
                        ('First Steps', 'Complete your first exercise session', 'sessions', 1, 0, '🎯', 'common', 1, current_time),
                        ('Getting Started', 'Complete 5 exercise sessions', 'sessions', 5, 0, '🚀', 'common', 1, current_time),
                        ('Dedicated', 'Complete 10 exercise sessions', 'sessions', 10, 0, '💪', 'uncommon', 1, current_time),
                        ('Regular User', 'Complete 25 exercise sessions', 'sessions', 25, 0, '⭐', 'uncommon', 1, current_time),
                        ('Marathon', 'Complete 50 exercise sessions', 'sessions', 50, 0, '🏃', 'rare', 1, current_time),
                        ('Century Club', 'Complete 100 exercise sessions', 'sessions', 100, 0, '👑', 'epic', 1, current_time),
                        
                        # Points-based achievements (achievements earned for reaching point milestones)
                        ('Point Starter', 'Earn 50 points from exercises', 'points', 50, 0, '🔸', 'common', 1, current_time),
                        ('Point Collector', 'Earn 100 points from exercises', 'points', 100, 0, '🔹', 'common', 1, current_time),
                        ('Point Hunter', 'Earn 200 points from exercises', 'points', 200, 0, '🔶', 'uncommon', 1, current_time),
                        ('Point Master', 'Earn 500 points from exercises', 'points', 500, 0, '🔷', 'rare', 1, current_time),
                        ('Point Legend', 'Earn 1000 points from exercises', 'points', 1000, 0, '💎', 'epic', 1, current_time),
                        ('Point God', 'Earn 2000 points from exercises', 'points', 2000, 0, '🏆', 'legendary', 1, current_time),
                        ('Ultimate Achiever', 'Earn 5000 points from exercises', 'points', 5000, 0, '🎖️', 'mythic', 1, current_time),
                        
                        # Time-based achievements (achievements earned for total exercise time)
                        ('Time Novice', 'Exercise for 30 minutes total', 'total_time', 1800, 0, '⏰', 'common', 1, current_time),
                        ('Time Master', 'Exercise for 60 minutes total', 'total_time', 3600, 0, '⏱️', 'uncommon', 1, current_time),
                        ('Time Champion', 'Exercise for 2 hours total', 'total_time', 7200, 0, '🕐', 'rare', 1, current_time),
                        ('Time Elite', 'Exercise for 5 hours total', 'total_time', 18000, 0, '⏳', 'epic', 1, current_time),
                        
                        # Streak achievements (achievements earned for consistency)
                        ('Consistency Starter', 'Exercise 3 days in a row', 'streak', 3, 0, '🔥', 'common', 1, current_time),
                        ('Consistency King', 'Exercise 7 days in a row', 'streak', 7, 0, '🔥🔥', 'uncommon', 1, current_time),
                        ('Consistency Legend', 'Exercise 14 days in a row', 'streak', 14, 0, '🔥🔥🔥', 'rare', 1, current_time),
                        ('Consistency God', 'Exercise 30 days in a row', 'streak', 30, 0, '🔥👑', 'legendary', 1, current_time)
                    ]
                    cursor.executemany('''
                        INSERT INTO Achievements (name, description, requirement_type, requirement_value, 
                                                points_reward, badge_icon, rarity, is_active, created_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', achievements)
                    print("Added comprehensive achievements with rarity and icons")
                
                conn.commit()
                
        except sqlite3.Error as e:
            print(f"Error adding sample data: {e}")
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def add_points_to_user(self, user_id, points):
        """Add points to a user from exercise sessions and check for new achievements"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                from datetime import datetime
                
                # Add points to user
                cursor.execute('''
                    UPDATE Users 
                    SET total_points = total_points + ?, 
                        experience_points = experience_points + ?,
                        last_activity = ?
                    WHERE id = ?
                ''', (points, points, datetime.now().isoformat(), user_id))
                
                # Check for level up
                self._check_level_up(cursor, user_id)
                
                conn.commit()
                
                # After adding points, automatically check for new achievements
                newly_earned = self.auto_check_and_award_achievements(user_id)
                
                return {
                    'success': True,
                    'newly_earned_achievements': newly_earned
                }
                
        except sqlite3.Error as e:
            print(f"Error adding points: {e}")
            return {'success': False, 'error': str(e)}
    
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
        """Award an achievement to a user (achievements are earned based on points, not giving points)"""
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
                    # Award the achievement (no points given - achievements are rewards for having points)
                    cursor.execute('''
                        INSERT INTO UserAchievements (user_id, achievement_id, earned_date, points_awarded)
                        VALUES (?, ?, ?, 0)
                    ''', (user_id, achievement_id, datetime.now().isoformat()))
                    
                    # Update only last activity (no points added)
                    cursor.execute('''
                        UPDATE Users 
                        SET last_activity = ?
                        WHERE id = ?
                    ''', (datetime.now().isoformat(), user_id))
                    
                    conn.commit()
                    return True
                return False
        except sqlite3.Error as e:
            print(f"Error awarding achievement: {e}")
            return False
    
    def _check_level_up(self, cursor, user_id):
        """Internal method to check and update user level"""
        # Get user's current experience
        cursor.execute('SELECT level, experience_points FROM Users WHERE id = ?', (user_id,))
        current_level, experience = cursor.fetchone()
        
        # Find the highest level the user qualifies for
        cursor.execute('''
            SELECT level FROM UserLevels 
            WHERE experience_required <= ? 
            ORDER BY level DESC LIMIT 1
        ''', (experience,))
        
        result = cursor.fetchone()
        if result and result[0] > current_level:
            new_level = result[0]
            cursor.execute('UPDATE Users SET level = ? WHERE id = ?', (new_level, user_id))
            return new_level
        return current_level
    
    def auto_check_and_award_achievements(self, user_id):
        """Automatically check and award all eligible achievements for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get user stats
                cursor.execute('''
                    SELECT total_points, total_sessions, total_time_seconds, current_streak
                    FROM Users WHERE id = ?
                ''', (user_id,))
                
                user_stats = cursor.fetchone()
                if not user_stats:
                    return []
                
                total_points, total_sessions, total_time, current_streak = user_stats
                
                # Get achievements user doesn't have yet
                cursor.execute('''
                    SELECT a.id, a.name, a.requirement_type, a.requirement_value, a.points_reward
                    FROM Achievements a
                    WHERE a.is_active = 1 
                    AND a.id NOT IN (
                        SELECT achievement_id FROM UserAchievements WHERE user_id = ?
                    )
                ''', (user_id,))
                
                available_achievements = cursor.fetchall()
                newly_earned = []
                
                for achievement in available_achievements:
                    achievement_id, name, req_type, req_value, points_reward = achievement
                    
                    # Check if requirements are met
                    earned = False
                    if req_type == 'points' and total_points >= req_value:
                        earned = True
                    elif req_type == 'sessions' and total_sessions >= req_value:
                        earned = True
                    elif req_type == 'total_time' and total_time >= req_value:
                        earned = True
                    elif req_type == 'streak' and current_streak >= req_value:
                        earned = True
                    
                    if earned:
                        if self.award_achievement(user_id, achievement_id):
                            newly_earned.append({
                                'id': achievement_id,
                                'name': name,
                                'requirement_type': req_type,
                                'requirement_value': req_value
                            })
                
                return newly_earned
                
        except sqlite3.Error as e:
            print(f"Error auto-checking achievements: {e}")
            return []
    
    def get_user_with_achievements(self, user_id):
        """Get user info with all their achievements"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get user info
                cursor.execute('''
                    SELECT u.id, u.first_name, u.last_name, u.total_points, u.total_sessions,
                           u.total_time_seconds, u.current_streak, u.longest_streak, u.level,
                           u.experience_points, ul.level_name, ul.bonus_multiplier
                    FROM Users u
                    LEFT JOIN UserLevels ul ON u.level = ul.level
                    WHERE u.id = ?
                ''', (user_id,))
                
                user_data = cursor.fetchone()
                if not user_data:
                    return None
                
                # Get user's achievements
                cursor.execute('''
                    SELECT a.id, a.name, a.description, a.badge_icon, a.rarity, 
                           ua.earned_date, ua.points_awarded
                    FROM Achievements a
                    JOIN UserAchievements ua ON a.id = ua.achievement_id
                    WHERE ua.user_id = ?
                    ORDER BY ua.earned_date DESC
                ''', (user_id,))
                
                achievements = cursor.fetchall()
                
                return {
                    'user': {
                        'id': user_data[0],
                        'first_name': user_data[1],
                        'last_name': user_data[2],
                        'full_name': f"{user_data[1]} {user_data[2]}",
                        'total_points': user_data[3],
                        'total_sessions': user_data[4],
                        'total_time_seconds': user_data[5],
                        'current_streak': user_data[6],
                        'longest_streak': user_data[7],
                        'level': user_data[8],
                        'experience_points': user_data[9],
                        'level_name': user_data[10],
                        'bonus_multiplier': user_data[11]
                    },
                    'achievements': [
                        {
                            'id': ach[0],
                            'name': ach[1],
                            'description': ach[2],
                            'badge_icon': ach[3],
                            'rarity': ach[4],
                            'earned_date': ach[5],
                            'points_awarded': ach[6]
                        } for ach in achievements
                    ]
                }
                
        except sqlite3.Error as e:
            print(f"Error getting user with achievements: {e}")
            return None
    
    def complete_exercise_session(self, user_id, time_intervals, exercise_type="general"):
        """Complete an exercise session: add session, update stats, add points, check achievements"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                from datetime import datetime
                
                # Calculate points using ScoreManager
                from score_manager import ScoreManager
                score_manager = ScoreManager()
                session_points = score_manager.calculate_session_score(time_intervals)
                total_time = sum(time_intervals)
                
                # Add session record
                cursor.execute('''
                    INSERT INTO Sessions (user_id, timestamp, exercise_type, time_intervals, total_time_seconds, score)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, datetime.now().isoformat(), exercise_type, str(time_intervals), total_time, session_points))
                
                # Update user stats
                cursor.execute('''
                    UPDATE Users 
                    SET total_points = total_points + ?,
                        total_sessions = total_sessions + 1,
                        total_time_seconds = total_time_seconds + ?,
                        experience_points = experience_points + ?,
                        last_activity = ?
                    WHERE id = ?
                ''', (session_points, total_time, session_points, datetime.now().isoformat(), user_id))
                
                # Check for level up
                self._check_level_up(cursor, user_id)
                
                conn.commit()
                
                # Check for newly earned achievements
                newly_earned = self.auto_check_and_award_achievements(user_id)
                
                return {
                    'success': True,
                    'session_points': session_points,
                    'total_time': total_time,
                    'newly_earned_achievements': newly_earned
                }
                
        except Exception as e:
            print(f"Error completing exercise session: {e}")
            return {'success': False, 'error': str(e)}
    
    def add_monitor_configuration(self, user_id, monitor_name, angle_x, angle_y, distance_cm=60.0, is_primary=False):
        """Add or update monitor configuration for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                from datetime import datetime
                current_time = datetime.now().isoformat()
                
                # Check if monitor config already exists
                cursor.execute('''
                    SELECT id FROM MonitorConfiguration 
                    WHERE user_id = ? AND monitor_name = ?
                ''', (user_id, monitor_name))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing configuration
                    cursor.execute('''
                        UPDATE MonitorConfiguration 
                        SET angle_x_degrees = ?, angle_y_degrees = ?, distance_cm = ?, 
                            is_primary = ?, last_updated = ?
                        WHERE user_id = ? AND monitor_name = ?
                    ''', (angle_x, angle_y, distance_cm, is_primary, current_time, user_id, monitor_name))
                    action = "updated"
                else:
                    # Insert new configuration
                    cursor.execute('''
                        INSERT INTO MonitorConfiguration 
                        (user_id, monitor_name, angle_x_degrees, angle_y_degrees, distance_cm, 
                         is_primary, created_date, last_updated, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                    ''', (user_id, monitor_name, angle_x, angle_y, distance_cm, is_primary, current_time, current_time))
                    action = "added"
                
                conn.commit()
                return {'success': True, 'action': action}
                
        except sqlite3.Error as e:
            print(f"Error managing monitor configuration: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_monitor_config(self, user_id):
        """Get all monitor configurations for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, monitor_name, angle_x_degrees, angle_y_degrees, distance_cm, 
                           is_primary, created_date, last_updated
                    FROM MonitorConfiguration 
                    WHERE user_id = ? AND is_active = 1
                    ORDER BY is_primary DESC, monitor_name
                ''', (user_id,))
                
                monitors = cursor.fetchall()
                
                return [
                    {
                        'id': monitor[0],
                        'monitor_name': monitor[1],
                        'angle_x_degrees': monitor[2],
                        'angle_y_degrees': monitor[3],
                        'distance_cm': monitor[4],
                        'is_primary': bool(monitor[5]),
                        'created_date': monitor[6],
                        'last_updated': monitor[7]
                    } for monitor in monitors
                ]
                
        except sqlite3.Error as e:
            print(f"Error getting monitor configuration: {e}")
            return []
    
    def record_eye_tracking_data(self, user_id, gaze_angle_x, gaze_angle_y, session_id=None, confidence_score=0.0):
        """Record eye tracking data point"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                from datetime import datetime
                current_time = datetime.now().isoformat()
                
                # Determine which monitor user is looking at based on angles
                monitor_detected = self._detect_monitor_from_gaze(cursor, user_id, gaze_angle_x, gaze_angle_y)
                
                cursor.execute('''
                    INSERT INTO EyeTrackingData 
                    (user_id, session_id, timestamp, gaze_angle_x, gaze_angle_y, monitor_detected, confidence_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, session_id, current_time, gaze_angle_x, gaze_angle_y, monitor_detected, confidence_score))
                
                conn.commit()
                return {'success': True, 'monitor_detected': monitor_detected}
                
        except sqlite3.Error as e:
            print(f"Error recording eye tracking data: {e}")
            return {'success': False, 'error': str(e)}
    
    def _detect_monitor_from_gaze(self, cursor, user_id, gaze_x, gaze_y):
        """Internal method to detect which monitor user is looking at based on gaze angles"""
        try:
            # Get user's monitor configurations
            cursor.execute('''
                SELECT monitor_name, angle_x_degrees, angle_y_degrees 
                FROM MonitorConfiguration 
                WHERE user_id = ? AND is_active = 1
            ''', (user_id,))
            
            monitors = cursor.fetchall()
            
            # Find closest monitor based on angle distance
            min_distance = float('inf')
            closest_monitor = None
            
            for monitor_name, monitor_x, monitor_y in monitors:
                # Calculate angular distance using Euclidean distance
                distance = ((gaze_x - monitor_x) ** 2 + (gaze_y - monitor_y) ** 2) ** 0.5
                
                if distance < min_distance:
                    min_distance = distance
                    closest_monitor = monitor_name
            
            # Return monitor name if within reasonable range (e.g., 20 degrees)
            return closest_monitor if min_distance <= 20.0 else "Unknown"
            
        except Exception:
            return "Unknown"
    
    def get_eye_tracking_stats(self, user_id, session_id=None, limit=100):
        """Get eye tracking statistics for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                where_clause = "WHERE user_id = ?"
                params = [user_id]
                
                if session_id:
                    where_clause += " AND session_id = ?"
                    params.append(session_id)
                
                # Get recent tracking data
                cursor.execute(f'''
                    SELECT timestamp, gaze_angle_x, gaze_angle_y, monitor_detected, confidence_score
                    FROM EyeTrackingData 
                    {where_clause}
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', params + [limit])
                
                tracking_data = cursor.fetchall()
                
                # Get monitor usage statistics
                cursor.execute(f'''
                    SELECT monitor_detected, COUNT(*) as usage_count,
                           AVG(confidence_score) as avg_confidence
                    FROM EyeTrackingData 
                    {where_clause}
                    GROUP BY monitor_detected
                    ORDER BY usage_count DESC
                ''', params)
                
                monitor_stats = cursor.fetchall()
                
                return {
                    'recent_data': [
                        {
                            'timestamp': data[0],
                            'gaze_x': data[1],
                            'gaze_y': data[2],
                            'monitor': data[3],
                            'confidence': data[4]
                        } for data in tracking_data
                    ],
                    'monitor_usage': [
                        {
                            'monitor_name': stat[0],
                            'usage_count': stat[1],
                            'avg_confidence': round(stat[2], 2)
                        } for stat in monitor_stats
                    ]
                }
                
        except sqlite3.Error as e:
            print(f"Error getting eye tracking stats: {e}")
            return {'recent_data': [], 'monitor_usage': []}

if __name__ == "__main__":
    # Initialize database
    db_manager = DatabaseManager()
    print("Database setup complete!")