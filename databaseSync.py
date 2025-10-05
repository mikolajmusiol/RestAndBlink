# databaseSync.py
import sqlite3
import json
from datetime import datetime
from typing import List


class DatabaseSync:
    """
    Minimalna klasa do zapisywania tylko niezbędnych danych używanych w okienku statystyk.
    """
    
    def __init__(self, db_path: str = 'user_data.db'):
        self.db_path = db_path
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Upewnia się, że baza danych istnieje z tabelami używanymi przez stats"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela Sessions - główne dane dla statystyk
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    exercise_type TEXT DEFAULT 'break',
                    time_intervals TEXT,
                    total_time_seconds INTEGER DEFAULT 0,
                    score INTEGER DEFAULT 0,
                    avg_heartbeat REAL DEFAULT 0.0,
                    min_heartbeat INTEGER DEFAULT 0,
                    max_heartbeat INTEGER DEFAULT 0,
                    stress_level REAL DEFAULT 0.0,
                    rest_quality_score REAL DEFAULT 0.0,
                    interruption_count INTEGER DEFAULT 0
                )
            ''')
            
            # Tabela Users - podstawowe dane użytkownika dla statystyk
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    total_points INTEGER DEFAULT 0,
                    total_sessions INTEGER DEFAULT 0,
                    total_time_seconds INTEGER DEFAULT 0,
                    current_streak INTEGER DEFAULT 0,
                    longest_streak INTEGER DEFAULT 0
                )
            ''')
            
            # Dodaj przykładowego użytkownika jeśli nie istnieje
            cursor.execute("SELECT COUNT(*) FROM Users WHERE id = 1")
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO Users (id, first_name, last_name, total_points, total_sessions, 
                                     total_time_seconds, current_streak, longest_streak)
                    VALUES (1, 'Jan', 'Kowalski', 0, 0, 0, 0, 0)
                ''')
            
            conn.commit()
    
    def sync_session(self, 
                    user_id: int,
                    heartbeat_data: List[int],
                    stress_level: float,
                    time_intervals: List[float],
                    points: int,
                    exercise_type: str = 'break') -> int:
        """
        Zapisuje sesję z niezbędnymi danymi dla statystyk.
        
        Returns:
            int: ID utworzonej sesji
        """
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            current_time = datetime.now().isoformat()
            
            # Oblicz statystyki tętna
            avg_heartbeat = sum(heartbeat_data) / len(heartbeat_data)
            min_heartbeat = min(heartbeat_data)
            max_heartbeat = max(heartbeat_data)
            
            # Oblicz całkowity czas
            total_time_seconds = int(sum(time_intervals))
            
            # Oblicz ocenę jakości odpoczynku (0-10)
            rest_quality = 5.0  # bazowa wartość
            if avg_heartbeat < 70:
                rest_quality += 2.0
            if stress_level < 0.3:
                rest_quality += 1.5
            rest_quality = min(10.0, max(0.0, rest_quality))
            
            # Wstaw sesję
            cursor.execute('''
                INSERT INTO Sessions (
                    user_id, timestamp, exercise_type, time_intervals, 
                    total_time_seconds, score, avg_heartbeat, min_heartbeat, 
                    max_heartbeat, stress_level, rest_quality_score, interruption_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, current_time, exercise_type, json.dumps(time_intervals),
                total_time_seconds, points, avg_heartbeat, min_heartbeat,
                max_heartbeat, stress_level, rest_quality, 0
            ))
            
            session_id = cursor.lastrowid or 0
            
            # Aktualizuj statystyki użytkownika
            cursor.execute('''
                UPDATE Users SET
                    total_points = total_points + ?,
                    total_sessions = total_sessions + 1,
                    total_time_seconds = total_time_seconds + ?
                WHERE id = ?
            ''', (points, total_time_seconds, user_id))
            
            conn.commit()
            return session_id


# Przykład użycia
if __name__ == "__main__":
    sync = DatabaseSync('user_data.db')
    
    # Przykładowe dane sesji
    heartbeat_data = [70, 68, 72, 69, 71, 67, 73, 66]  # tętno
    stress_level = 0.3  # 30% stresu
    time_intervals = [120.5, 95.0, 84.5]  # interwały w sekundach
    points = 245  # punkty
    
    session_id = sync.sync_session(
        user_id=1,
        heartbeat_data=heartbeat_data,
        stress_level=stress_level,
        time_intervals=time_intervals,
        points=points,
        exercise_type='palming'
    )
    
    print(f"Zapisano sesję o ID: {session_id}")
    print(f"- Średnie tętno: {sum(heartbeat_data)/len(heartbeat_data):.1f} BPM")
    print(f"- Stres: {stress_level*100:.0f}%")
    print(f"- Czas: {sum(time_intervals):.1f}s")
    print(f"- Punkty: {points}")
    
    # Sprawdź czy dane zostały zapisane
    with sqlite3.connect('user_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Sessions WHERE user_id = 1")
        sessions_count = cursor.fetchone()[0]
        print(f"- Łączna liczba sesji: {sessions_count}")
        
        cursor.execute("SELECT total_points, total_sessions FROM Users WHERE id = 1")
        user_stats = cursor.fetchone()
        print(f"- Punkty użytkownika: {user_stats[0]}")
        print(f"- Sesje użytkownika: {user_stats[1]}")