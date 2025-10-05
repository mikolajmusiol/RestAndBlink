# ui/tabs/daily_stats_tab.py

import sqlite3
import json
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QGridLayout, QScrollArea, QFrame)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class DailyStatsTab(QWidget):
    """Zakładka do wyświetlania dziennych statystyk."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_path = "user_data.db"
        self.user_id = 1  # Assuming single user for now
        self.setLayout(self._setup_layout())
        self.load_daily_stats()

    def _setup_layout(self):
        main_layout = QVBoxLayout()
        
        # Scroll area for all content
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Header
        header_label = QLabel("<h2>Dzienne Statystyki</h2>")
        header_label.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(header_label)

        # Stats summary section
        self.stats_frame = QFrame()
        self.stats_frame.setFrameStyle(QFrame.Box)
        self.stats_layout = QGridLayout(self.stats_frame)
        scroll_layout.addWidget(self.stats_frame)

        # Charts section
        self.charts_frame = QFrame()
        self.charts_frame.setFrameStyle(QFrame.Box)
        self.charts_layout = QVBoxLayout(self.charts_frame)
        scroll_layout.addWidget(self.charts_frame)

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        return main_layout

    def load_daily_stats(self):
        """Load and display daily statistics."""
        today = datetime.now().strftime('%Y-%m-%d')
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get today's basic stats
            today_stats = self._get_today_basic_stats(conn, today)
            self._display_basic_stats(today_stats)
            
            # Get heartbeat and stress data for charts
            heartbeat_data = self._get_today_heartbeat_data(conn, today)
            if heartbeat_data:
                self._create_heartbeat_charts(heartbeat_data)
            
            conn.close()
            
        except Exception as e:
            print(f"Error loading daily stats: {e}")

    def _get_today_basic_stats(self, conn, today):
        """Get basic statistics for today."""
        cursor = conn.cursor()
        
        # Today's sessions
        cursor.execute("""
            SELECT COUNT(*) as sessions, 
                   SUM(total_time_seconds) as total_time,
                   AVG(score) as avg_score,
                   AVG(avg_heartbeat) as avg_heartbeat,
                   AVG(stress_level) as avg_stress,
                   AVG(rest_quality_score) as avg_rest_quality,
                   SUM(interruption_count) as total_interruptions
            FROM Sessions 
            WHERE user_id = ? AND DATE(timestamp) = ?
        """, (self.user_id, today))
        
        result = cursor.fetchone()
        
        stats = {
            'sessions': result[0] or 0,
            'total_time': result[1] or 0,
            'avg_score': result[2] or 0,
            'avg_heartbeat': result[3] or 0,
            'avg_stress': result[4] or 0,
            'avg_rest_quality': result[5] or 0,
            'total_interruptions': result[6] or 0
        }
        
        # Get best and worst session
        cursor.execute("""
            SELECT MAX(rest_quality_score) as best_quality,
                   MIN(rest_quality_score) as worst_quality
            FROM Sessions 
            WHERE user_id = ? AND DATE(timestamp) = ? AND rest_quality_score > 0
        """, (self.user_id, today))
        
        quality_result = cursor.fetchone()
        stats['best_quality'] = quality_result[0] or 0
        stats['worst_quality'] = quality_result[1] or 0
        
        return stats

    def _get_today_heartbeat_data(self, conn, today):
        """Get heartbeat and stress data for today's sessions."""
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT heartbeat_data, avg_heartbeat, stress_level, timestamp,
                   rest_quality_score, interruption_count
            FROM Sessions 
            WHERE user_id = ? AND DATE(timestamp) = ? 
            AND heartbeat_data IS NOT NULL AND heartbeat_data != ''
            ORDER BY timestamp
        """, (self.user_id, today))
        
        sessions = cursor.fetchall()
        
        if not sessions:
            return None
            
        all_data = []
        
        for session in sessions:
            try:
                heartbeat_json = json.loads(session[0])
                timestamps = heartbeat_json.get('timestamps', [])
                heartbeats = heartbeat_json.get('heartbeats', [])
                stress_levels = heartbeat_json.get('stress_levels', [])
                
                session_time = datetime.fromisoformat(session[3])
                
                for i, (timestamp, heartbeat, stress) in enumerate(zip(timestamps, heartbeats, stress_levels)):
                    all_data.append({
                        'time': session_time + timedelta(seconds=timestamp),
                        'heartbeat': heartbeat,
                        'stress': stress,
                        'session_time': session_time.strftime('%H:%M'),
                        'avg_heartbeat': session[1],
                        'avg_stress': session[2],
                        'rest_quality': session[4],
                        'interruptions': session[5]
                    })
            except (json.JSONDecodeError, TypeError):
                continue
        
        return all_data

    def _display_basic_stats(self, stats):
        """Display basic statistics in the stats frame."""
        # Clear existing widgets
        for i in reversed(range(self.stats_layout.count())): 
            self.stats_layout.itemAt(i).widget().setParent(None)

        row = 0
        
        # Sessions count
        self.stats_layout.addWidget(QLabel("<b>Liczba sesji dzisiaj:</b>"), row, 0)
        self.stats_layout.addWidget(QLabel(str(stats['sessions'])), row, 1)
        
        # Total time
        hours = stats['total_time'] // 3600
        minutes = (stats['total_time'] % 3600) // 60
        self.stats_layout.addWidget(QLabel("<b>Łączny czas przerw:</b>"), row, 2)
        self.stats_layout.addWidget(QLabel(f"{hours}h {minutes}m"), row, 3)
        row += 1
        
        # Average score
        self.stats_layout.addWidget(QLabel("<b>Średni wynik:</b>"), row, 0)
        self.stats_layout.addWidget(QLabel(f"{stats['avg_score']:.1f}"), row, 1)
        
        # Average heartbeat
        self.stats_layout.addWidget(QLabel("<b>Średnie tętno:</b>"), row, 2)
        self.stats_layout.addWidget(QLabel(f"{stats['avg_heartbeat']:.1f} BPM"), row, 3)
        row += 1
        
        # Stress level
        self.stats_layout.addWidget(QLabel("<b>Średni poziom stresu:</b>"), row, 0)
        self.stats_layout.addWidget(QLabel(f"{stats['avg_stress']:.2f}"), row, 1)
        
        # Rest quality
        self.stats_layout.addWidget(QLabel("<b>Jakość odpoczynku:</b>"), row, 2)
        self.stats_layout.addWidget(QLabel(f"{stats['avg_rest_quality']:.1f}/10"), row, 3)
        row += 1
        
        # Interruptions
        self.stats_layout.addWidget(QLabel("<b>Łączne przerwania:</b>"), row, 0)
        self.stats_layout.addWidget(QLabel(str(stats['total_interruptions'])), row, 1)
        
        # Quality range
        quality_range = stats['best_quality'] - stats['worst_quality']
        self.stats_layout.addWidget(QLabel("<b>Rozstęp jakości:</b>"), row, 2)
        self.stats_layout.addWidget(QLabel(f"{quality_range:.1f}"), row, 3)

    def _create_heartbeat_charts(self, data):
        """Create heartbeat and stress level charts."""
        if not data:
            return
            
        # Clear existing charts
        for i in reversed(range(self.charts_layout.count())): 
            self.charts_layout.itemAt(i).widget().setParent(None)

        df = pd.DataFrame(data)
        
        # Set matplotlib style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig = Figure(figsize=(12, 10))
        
        # Heartbeat over time
        ax1 = fig.add_subplot(3, 2, 1)
        ax1.plot(range(len(df)), df['heartbeat'], linewidth=1.5, color='black')
        ax1.set_title('Tętno w ciągu dnia')
        ax1.set_xlabel('Czas (próbki)')
        ax1.set_ylabel('Tętno (BPM)')
        ax1.grid(True, alpha=0.3)
        
        # Stress level over time
        ax2 = fig.add_subplot(3, 2, 2)
        ax2.plot(range(len(df)), df['stress'], linewidth=1.5, color='gray')
        ax2.set_title('Poziom stresu w ciągu dnia')
        ax2.set_xlabel('Czas (próbki)')
        ax2.set_ylabel('Poziom stresu')
        ax2.grid(True, alpha=0.3)
        
        # Heartbeat distribution
        ax3 = fig.add_subplot(3, 2, 3)
        ax3.hist(df['heartbeat'], bins=20, alpha=0.7, color='lightgray', edgecolor='black')
        ax3.set_title('Rozkład tętna')
        ax3.set_xlabel('Tętno (BPM)')
        ax3.set_ylabel('Częstotliwość')
        
        # Stress distribution
        ax4 = fig.add_subplot(3, 2, 4)
        ax4.hist(df['stress'], bins=20, alpha=0.7, color='lightgray', edgecolor='black')
        ax4.set_title('Rozkład poziomu stresu')
        ax4.set_xlabel('Poziom stresu')
        ax4.set_ylabel('Częstotliwość')
        
        # Correlation scatter plot
        ax5 = fig.add_subplot(3, 2, 5)
        ax5.scatter(df['heartbeat'], df['stress'], alpha=0.6, color='black', s=20)
        ax5.set_title('Korelacja: Tętno vs Stres')
        ax5.set_xlabel('Tętno (BPM)')
        ax5.set_ylabel('Poziom stresu')
        ax5.grid(True, alpha=0.3)
        
        # Add correlation coefficient
        correlation = np.corrcoef(df['heartbeat'], df['stress'])[0, 1]
        ax5.text(0.05, 0.95, f'r = {correlation:.3f}', transform=ax5.transAxes, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        # Box plot comparison
        ax6 = fig.add_subplot(3, 2, 6)
        box_data = [df['heartbeat'], df['stress'] * 100]  # Scale stress for comparison
        bp = ax6.boxplot(box_data, labels=['Tętno', 'Stres (x100)'], patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('lightgray')
            patch.set_edgecolor('black')
        ax6.set_title('Porównanie rozkładów')
        ax6.set_ylabel('Wartość')
        
        fig.tight_layout()
        
        # Add chart to layout
        canvas = FigureCanvas(fig)
        self.charts_layout.addWidget(canvas)

    def refresh_stats(self):
        """Refresh the daily statistics."""
        self.load_daily_stats()