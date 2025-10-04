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
                
                # Create Sessions table for comprehensive exercise and health tracking
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        timestamp TEXT NOT NULL,
                        exercise_type TEXT DEFAULT 'break',
                        time_intervals TEXT,
                        total_time_seconds INTEGER DEFAULT 0,
                        score INTEGER DEFAULT 0,
                        heartbeat_data TEXT,
                        avg_heartbeat REAL DEFAULT 0.0,
                        min_heartbeat INTEGER DEFAULT 0,
                        max_heartbeat INTEGER DEFAULT 0,
                        stress_level REAL DEFAULT 0.0,
                        rest_quality_score REAL DEFAULT 0.0,
                        interruption_count INTEGER DEFAULT 0,
                        session_completed BOOLEAN DEFAULT 1,
                        notes TEXT,
                        FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE
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
                
                # Create HeartbeatData table for detailed heartbeat tracking (every 5 seconds)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS HeartbeatData (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        timestamp TEXT NOT NULL,
                        heartbeat_bpm INTEGER NOT NULL,
                        stress_indicator REAL DEFAULT 0.0,
                        activity_level TEXT DEFAULT 'resting',
                        data_quality REAL DEFAULT 1.0,
                        FOREIGN KEY (session_id) REFERENCES Sessions (id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE
                    )
                ''')
                
                # Create DailyHealthStats table for end-of-day summaries
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS DailyHealthStats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        date TEXT NOT NULL,
                        total_break_time_seconds INTEGER DEFAULT 0,
                        total_sessions INTEGER DEFAULT 0,
                        avg_daily_heartbeat REAL DEFAULT 0.0,
                        min_daily_heartbeat INTEGER DEFAULT 0,
                        max_daily_heartbeat INTEGER DEFAULT 0,
                        avg_stress_level REAL DEFAULT 0.0,
                        avg_rest_quality REAL DEFAULT 0.0,
                        total_interruptions INTEGER DEFAULT 0,
                        best_rest_session_id INTEGER,
                        worst_rest_session_id INTEGER,
                        health_score REAL DEFAULT 0.0,
                        notes TEXT,
                        created_timestamp TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE,
                        FOREIGN KEY (best_rest_session_id) REFERENCES Sessions (id) ON DELETE SET NULL,
                        FOREIGN KEY (worst_rest_session_id) REFERENCES Sessions (id) ON DELETE SET NULL,
                        UNIQUE(user_id, date)
                    )
                ''')
                
                # Create indexes for performance
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_heartbeat_session_time 
                    ON HeartbeatData (session_id, timestamp)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_daily_stats_user_date 
                    ON DailyHealthStats (user_id, date)
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
    
    def start_health_session(self, user_id, exercise_type="break"):
        """Start a new health tracking session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                from datetime import datetime
                current_time = datetime.now().isoformat()
                
                cursor.execute('''
                    INSERT INTO Sessions (user_id, timestamp, exercise_type, session_completed)
                    VALUES (?, ?, ?, 0)
                ''', (user_id, current_time, exercise_type))
                
                session_id = cursor.lastrowid
                conn.commit()
                
                return {'success': True, 'session_id': session_id}
                
        except sqlite3.Error as e:
            print(f"Error starting health session: {e}")
            return {'success': False, 'error': str(e)}
    
    def record_heartbeat(self, session_id, user_id, heartbeat_bpm, stress_indicator=0.0, activity_level='resting'):
        """Record heartbeat data point (every 5 seconds)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                from datetime import datetime
                current_time = datetime.now().isoformat()
                
                # Calculate data quality based on reasonable heartbeat ranges
                data_quality = 1.0
                if heartbeat_bpm < 40 or heartbeat_bpm > 200:
                    data_quality = 0.3  # Poor quality data
                elif heartbeat_bpm < 50 or heartbeat_bpm > 150:
                    data_quality = 0.7  # Medium quality data
                
                cursor.execute('''
                    INSERT INTO HeartbeatData 
                    (session_id, user_id, timestamp, heartbeat_bpm, stress_indicator, activity_level, data_quality)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (session_id, user_id, current_time, heartbeat_bpm, stress_indicator, activity_level, data_quality))
                
                conn.commit()
                return {'success': True, 'data_quality': data_quality}
                
        except sqlite3.Error as e:
            print(f"Error recording heartbeat: {e}")
            return {'success': False, 'error': str(e)}
    
    def complete_health_session(self, session_id, time_intervals, interruption_count=0, notes=""):
        """Complete a health session with full analysis"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                from datetime import datetime
                
                # Get all heartbeat data for this session
                cursor.execute('''
                    SELECT heartbeat_bpm, stress_indicator, data_quality 
                    FROM HeartbeatData 
                    WHERE session_id = ?
                    ORDER BY timestamp
                ''', (session_id,))
                
                heartbeat_records = cursor.fetchall()
                
                if heartbeat_records:
                    # Calculate heartbeat statistics
                    heartbeats = [record[0] for record in heartbeat_records]
                    stress_levels = [record[1] for record in heartbeat_records]
                    
                    avg_heartbeat = sum(heartbeats) / len(heartbeats)
                    min_heartbeat = min(heartbeats)
                    max_heartbeat = max(heartbeats)
                    avg_stress = sum(stress_levels) / len(stress_levels) if stress_levels else 0.0
                    
                    # Calculate rest quality score (lower heartbeat variability = better rest)
                    if len(heartbeats) > 1:
                        heartbeat_variance = sum([(hb - avg_heartbeat) ** 2 for hb in heartbeats]) / len(heartbeats)
                        rest_quality = max(0.0, min(10.0, 10.0 - (heartbeat_variance / 100)))
                    else:
                        rest_quality = 5.0  # Default moderate quality
                    
                    # Create heartbeat data JSON
                    heartbeat_data = {
                        'timestamps': [i * 5 for i in range(len(heartbeats))],  # Every 5 seconds
                        'heartbeats': heartbeats,
                        'stress_levels': stress_levels
                    }
                    
                else:
                    # No heartbeat data available
                    avg_heartbeat = min_heartbeat = max_heartbeat = 0
                    avg_stress = rest_quality = 0.0
                    heartbeat_data = {'timestamps': [], 'heartbeats': [], 'stress_levels': []}
                
                # Calculate total time and score
                total_time = sum(time_intervals) if time_intervals else 0
                
                # Calculate session score using ScoreManager
                from score_manager import ScoreManager
                score_manager = ScoreManager()
                session_score = score_manager.calculate_session_score(time_intervals) if time_intervals else 0
                
                # Update session record
                cursor.execute('''
                    UPDATE Sessions 
                    SET time_intervals = ?, total_time_seconds = ?, score = ?,
                        heartbeat_data = ?, avg_heartbeat = ?, min_heartbeat = ?, max_heartbeat = ?,
                        stress_level = ?, rest_quality_score = ?, interruption_count = ?,
                        session_completed = 1, notes = ?
                    WHERE id = ?
                ''', (
                    str(time_intervals), total_time, session_score,
                    str(heartbeat_data), avg_heartbeat, min_heartbeat, max_heartbeat,
                    avg_stress, rest_quality, interruption_count, notes, session_id
                ))
                
                # Update user stats
                cursor.execute('SELECT user_id FROM Sessions WHERE id = ?', (session_id,))
                user_id = cursor.fetchone()[0]
                
                cursor.execute('''
                    UPDATE Users 
                    SET total_points = total_points + ?,
                        total_sessions = total_sessions + 1,
                        total_time_seconds = total_time_seconds + ?,
                        experience_points = experience_points + ?,
                        last_activity = ?
                    WHERE id = ?
                ''', (session_score, total_time, session_score, datetime.now().isoformat(), user_id))
                
                # Check for level up
                self._check_level_up(cursor, user_id)
                
                conn.commit()
                
                # Check for newly earned achievements
                newly_earned = self.auto_check_and_award_achievements(user_id)
                
                return {
                    'success': True,
                    'session_stats': {
                        'total_time': total_time,
                        'score': session_score,
                        'avg_heartbeat': round(avg_heartbeat, 1),
                        'heartbeat_range': f"{min_heartbeat}-{max_heartbeat}",
                        'avg_stress': round(avg_stress, 2),
                        'rest_quality': round(rest_quality, 1),
                        'interruptions': interruption_count
                    },
                    'newly_earned_achievements': newly_earned
                }
                
        except Exception as e:
            print(f"Error completing health session: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_daily_health_summary(self, user_id, date=None):
        """Generate end-of-day health statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                from datetime import datetime, date as date_module
                
                if date is None:
                    date = date_module.today().isoformat()
                
                # Get all sessions for the day
                cursor.execute('''
                    SELECT id, total_time_seconds, avg_heartbeat, min_heartbeat, max_heartbeat,
                           stress_level, rest_quality_score, interruption_count
                    FROM Sessions
                    WHERE user_id = ? AND DATE(timestamp) = ? AND session_completed = 1
                ''', (user_id, date))
                
                sessions = cursor.fetchall()
                
                if not sessions:
                    return {'success': False, 'message': 'No sessions found for this date'}
                
                # Calculate daily statistics
                total_sessions = len(sessions)
                total_break_time = sum(session[1] for session in sessions)
                
                # Heartbeat statistics (only from sessions with heartbeat data)
                heartbeat_sessions = [s for s in sessions if s[2] > 0]
                if heartbeat_sessions:
                    avg_daily_heartbeat = sum(s[2] for s in heartbeat_sessions) / len(heartbeat_sessions)
                    min_daily_heartbeat = min(s[3] for s in heartbeat_sessions)
                    max_daily_heartbeat = max(s[4] for s in heartbeat_sessions)
                else:
                    avg_daily_heartbeat = min_daily_heartbeat = max_daily_heartbeat = 0
                
                # Stress and quality statistics
                stress_sessions = [s for s in sessions if s[5] > 0]
                avg_stress = sum(s[5] for s in stress_sessions) / len(stress_sessions) if stress_sessions else 0
                
                quality_sessions = [s for s in sessions if s[6] > 0]
                avg_rest_quality = sum(s[6] for s in quality_sessions) / len(quality_sessions) if quality_sessions else 0
                
                total_interruptions = sum(s[7] for s in sessions)
                
                # Find best and worst sessions
                if quality_sessions:
                    best_session = max(quality_sessions, key=lambda x: x[6])
                    worst_session = min(quality_sessions, key=lambda x: x[6])
                    best_session_id = best_session[0]
                    worst_session_id = worst_session[0]
                else:
                    best_session_id = worst_session_id = None
                
                # Calculate overall health score (0-100)
                health_score = self._calculate_health_score(
                    avg_rest_quality, avg_stress, total_interruptions, total_sessions
                )
                
                # Save daily summary
                cursor.execute('''
                    INSERT OR REPLACE INTO DailyHealthStats
                    (user_id, date, total_break_time_seconds, total_sessions, avg_daily_heartbeat,
                     min_daily_heartbeat, max_daily_heartbeat, avg_stress_level, avg_rest_quality,
                     total_interruptions, best_rest_session_id, worst_rest_session_id, 
                     health_score, created_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, date, total_break_time, total_sessions, avg_daily_heartbeat,
                    min_daily_heartbeat, max_daily_heartbeat, avg_stress, avg_rest_quality,
                    total_interruptions, best_session_id, worst_session_id, health_score,
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                
                return {
                    'success': True,
                    'daily_stats': {
                        'date': date,
                        'total_sessions': total_sessions,
                        'total_break_time_minutes': round(total_break_time / 60, 1),
                        'avg_heartbeat': round(avg_daily_heartbeat, 1),
                        'heartbeat_range': f"{min_daily_heartbeat}-{max_daily_heartbeat}",
                        'avg_stress_level': round(avg_stress, 2),
                        'avg_rest_quality': round(avg_rest_quality, 1),
                        'total_interruptions': total_interruptions,
                        'health_score': round(health_score, 1)
                    }
                }
                
        except Exception as e:
            print(f"Error generating daily health summary: {e}")
            return {'success': False, 'error': str(e)}
    
    def _calculate_health_score(self, rest_quality, stress_level, interruptions, sessions):
        """Calculate overall health score (0-100)"""
        # Base score from rest quality (0-10 scale -> 0-50 points)
        quality_score = (rest_quality / 10.0) * 50
        
        # Stress penalty (0-1 scale -> 0-25 points penalty)
        stress_penalty = stress_level * 25
        
        # Interruption penalty (each interruption = -2 points)
        interruption_penalty = min(interruptions * 2, 20)  # Max 20 points penalty
        
        # Session bonus (more sessions = better, up to +5 points)
        session_bonus = min(sessions, 5)
        
        health_score = max(0, min(100, quality_score - stress_penalty - interruption_penalty + session_bonus))
        return health_score
    
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