import numpy as np
import math
import json
import os
from datetime import datetime

class ScoreManager:
    def __init__(self, data_file="user_data.json"):
        self.data_file = data_file
        self.MAX_TIME_SECONDS = 300  # 5 minutes
        self.load_data()
    
    def load_data(self):
        """Load user score data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.total_score = data.get('total_score', 0)
                    self.sessions = data.get('sessions', [])
            except (json.JSONDecodeError, KeyError):
                self.total_score = 0
                self.sessions = []
        else:
            self.total_score = 0
            self.sessions = []
    
    def save_data(self):
        """Save user score data to file"""
        data = {
            'total_score': self.total_score,
            'sessions': self.sessions,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, indent=2, fp=f)
    
    def calculate_interval_score(self, exercise_time_seconds):
        """
        Calculate score for a single time interval using exponential function e^x
        where x is seconds, normalized to 0-100 points for max 5 minutes
        
        Args:
            exercise_time_seconds (float): Time exercised in seconds (0-300)
            
        Returns:
            int: Score from 0 to 100 points for this interval
        """
        # Clamp time to maximum
        time_clamped = min(exercise_time_seconds, self.MAX_TIME_SECONDS)
        
        # Ensure non-negative time
        time_clamped = max(0, time_clamped)
        
        if time_clamped == 0:
            return 0
        
        # Calculate fairer exponential score
        # Use e^(x/120) instead of e^(x/60) for more balanced scoring
        # This gives us e^2.5 ≈ 12.18 at max time (300s), much more reasonable
        # Promotes continuous exercise but doesn't overly penalize breaks
        scaled_time = time_clamped / 120.0  # Scale to [0, 2.5] for 300 seconds
        raw_score = math.exp(scaled_time)
        
        # Normalize to 0-100: (e^(x/120) - 1) / (e^2.5 - 1) * 100
        max_raw_score = math.exp(2.5)  # e^2.5 ≈ 12.18
        normalized_score = ((raw_score - 1) / (max_raw_score - 1)) * 100
        
        return int(normalized_score)  # Cast to int as requested
    
    def calculate_session_score(self, time_intervals):
        """
        Calculate total score for multiple time intervals that sum up to max 5 minutes
        
        Args:
            time_intervals (list): List of time intervals in seconds 
                                 Example: [120, 70, 50, 60] = 300 seconds total
            
        Returns:
            int: Total score summed from all intervals
        """
        if not time_intervals:
            return 0
        
        # Ensure total time doesn't exceed maximum
        total_time = sum(time_intervals)
        if total_time > self.MAX_TIME_SECONDS:
            # Scale down intervals proportionally if they exceed max time
            scale_factor = self.MAX_TIME_SECONDS / total_time
            time_intervals = [interval * scale_factor for interval in time_intervals]
        
        # Calculate score for each interval and sum them
        return sum(self.calculate_interval_score(interval) for interval in time_intervals)
    
    def add_session(self, time_intervals, exercise_type="general"):
        """
        Add a new exercise session and update total score
        
        Args:
            time_intervals (list): List of time intervals in seconds
            exercise_type (str): Type of exercise performed
            
        Returns:
            int: Score earned for this session
        """
        session_score = self.calculate_session_score(time_intervals)
        
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'time_intervals': time_intervals,
            'total_time_seconds': sum(time_intervals),
            'exercise_type': exercise_type,
            'score': session_score
        }
        
        self.sessions.append(session_data)
        self.total_score += session_score
        self.save_data()
        
        return session_score
    
    def get_total_score(self):
        """Get total accumulated score"""
        return self.total_score
    
    def get_session_count(self):
        """Get total number of sessions completed"""
        return len(self.sessions)
    
    def get_average_session_score(self):
        """Get average score per session"""
        if not self.sessions:
            return 0
        return sum(session['score'] for session in self.sessions) / len(self.sessions)
    
    def get_recent_sessions(self, count=10):
        """Get most recent sessions"""
        return self.sessions[-count:] if self.sessions else []
    
    def reset_scores(self):
        """Reset all scores and sessions"""
        self.total_score = 0
        self.sessions = []
        self.save_data()
    
    def get_score_breakdown_for_time(self, max_seconds=300, step_seconds=30):
        """
        Get score breakdown for different time intervals (for display/debugging)
        
        Args:
            max_seconds (int): Maximum time to show
            step_seconds (int): Step interval
            
        Returns:
            list: List of (time, score) tuples
        """
        breakdown = []
        for seconds in range(0, max_seconds + 1, step_seconds):
            score = self.calculate_interval_score(seconds)
            breakdown.append((seconds, score))
        return breakdown
    
    def calculate_example_scores(self):
        """
        Example function showing how the scoring works with multiple intervals
        
        Returns:
            dict: Examples of different interval combinations and their scores
        """
        return {
            'example_intervals': self.calculate_session_score([120, 70, 50, 60]),  # 300 seconds total
        }