# ui/tabs/weekly_stats_tab.py

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


class WeeklyStatsTab(QWidget):
    """Zakładka do wyświetlania tygodniowych statystyk."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_path = "user_data.db"
        self.user_id = 1  # Assuming single user for now
        self.setLayout(self._setup_layout())
        self.load_weekly_stats()

    def _setup_layout(self):
        main_layout = QVBoxLayout()
        
        # Scroll area for all content
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Header
        header_label = QLabel("<h2>Tygodniowe Statystyki</h2>")
        header_label.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(header_label)

        # Date range info
        self.date_range_label = QLabel()
        self.date_range_label.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(self.date_range_label)

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

    def load_weekly_stats(self):
        """Load and display weekly statistics."""
        # Get current week range (Monday to Sunday)
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        start_date = start_of_week.strftime('%Y-%m-%d')
        end_date = end_of_week.strftime('%Y-%m-%d')
        
        self.date_range_label.setText(f"<b>{start_of_week.strftime('%d.%m')} - {end_of_week.strftime('%d.%m.%Y')}</b>")
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get weekly basic stats
            weekly_stats = self._get_weekly_basic_stats(conn, start_date, end_date)
            self._display_basic_stats(weekly_stats)
            
            # Get daily aggregated data for charts
            daily_data = self._get_weekly_daily_data(conn, start_date, end_date)
            if daily_data:
                self._create_weekly_charts(daily_data, start_of_week)
            
            conn.close()
            
        except Exception as e:
            print(f"Error loading weekly stats: {e}")

    def _get_weekly_basic_stats(self, conn, start_date, end_date):
        """Get basic statistics for the week."""
        cursor = conn.cursor()
        
        # Weekly sessions summary
        cursor.execute("""
            SELECT COUNT(*) as sessions, 
                   SUM(total_time_seconds) as total_time,
                   AVG(score) as avg_score,
                   AVG(avg_heartbeat) as avg_heartbeat,
                   AVG(stress_level) as avg_stress,
                   AVG(rest_quality_score) as avg_rest_quality,
                   SUM(interruption_count) as total_interruptions,
                   COUNT(DISTINCT DATE(timestamp)) as active_days
            FROM Sessions 
            WHERE user_id = ? AND DATE(timestamp) BETWEEN ? AND ?
        """, (self.user_id, start_date, end_date))
        
        result = cursor.fetchone()
        
        stats = {
            'sessions': result[0] or 0,
            'total_time': result[1] or 0,
            'avg_score': result[2] or 0,
            'avg_heartbeat': result[3] or 0,
            'avg_stress': result[4] or 0,
            'avg_rest_quality': result[5] or 0,
            'total_interruptions': result[6] or 0,
            'active_days': result[7] or 0
        }
        
        # Get best and worst days
        cursor.execute("""
            SELECT DATE(timestamp) as date, 
                   COUNT(*) as day_sessions,
                   AVG(rest_quality_score) as avg_quality,
                   SUM(total_time_seconds) as day_time
            FROM Sessions 
            WHERE user_id = ? AND DATE(timestamp) BETWEEN ? AND ?
            GROUP BY DATE(timestamp)
            ORDER BY avg_quality DESC
        """, (self.user_id, start_date, end_date))
        
        daily_results = cursor.fetchall()
        
        if daily_results:
            best_day = daily_results[0]
            worst_day = daily_results[-1]
            stats['best_day'] = best_day[0]
            stats['best_day_quality'] = best_day[2] or 0
            stats['worst_day'] = worst_day[0]
            stats['worst_day_quality'] = worst_day[2] or 0
        else:
            stats['best_day'] = None
            stats['best_day_quality'] = 0
            stats['worst_day'] = None
            stats['worst_day_quality'] = 0
        
        return stats

    def _get_weekly_daily_data(self, conn, start_date, end_date):
        """Get daily aggregated data for the week."""
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DATE(timestamp) as date,
                   COUNT(*) as sessions,
                   SUM(total_time_seconds) as total_time,
                   AVG(avg_heartbeat) as avg_heartbeat,
                   AVG(stress_level) as avg_stress,
                   AVG(rest_quality_score) as avg_quality,
                   SUM(interruption_count) as interruptions,
                   AVG(score) as avg_score
            FROM Sessions 
            WHERE user_id = ? AND DATE(timestamp) BETWEEN ? AND ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        """, (self.user_id, start_date, end_date))
        
        results = cursor.fetchall()
        
        if not results:
            return None
            
        data = []
        for row in results:
            data.append({
                'date': datetime.strptime(row[0], '%Y-%m-%d'),
                'sessions': row[1],
                'total_time': row[2] or 0,
                'avg_heartbeat': row[3] or 0,
                'avg_stress': row[4] or 0,
                'avg_quality': row[5] or 0,
                'interruptions': row[6] or 0,
                'avg_score': row[7] or 0
            })
        
        return data

    def _display_basic_stats(self, stats):
        """Display basic statistics in the stats frame."""
        # Clear existing widgets
        for i in reversed(range(self.stats_layout.count())): 
            self.stats_layout.itemAt(i).widget().setParent(None)

        row = 0
        
        # Sessions count
        self.stats_layout.addWidget(QLabel("<b>Sesje w tygodniu:</b>"), row, 0)
        self.stats_layout.addWidget(QLabel(str(stats['sessions'])), row, 1)
        
        # Active days
        self.stats_layout.addWidget(QLabel("<b>Aktywne dni:</b>"), row, 2)
        self.stats_layout.addWidget(QLabel(f"{stats['active_days']}/7"), row, 3)
        row += 1
        
        # Total time
        hours = stats['total_time'] // 3600
        minutes = (stats['total_time'] % 3600) // 60
        self.stats_layout.addWidget(QLabel("<b>Łączny czas:</b>"), row, 0)
        self.stats_layout.addWidget(QLabel(f"{hours}h {minutes}m"), row, 1)
        
        # Average daily sessions
        avg_daily_sessions = stats['sessions'] / max(stats['active_days'], 1)
        self.stats_layout.addWidget(QLabel("<b>Średnio sesji/dzień:</b>"), row, 2)
        self.stats_layout.addWidget(QLabel(f"{avg_daily_sessions:.1f}"), row, 3)
        row += 1
        
        # Average heartbeat
        self.stats_layout.addWidget(QLabel("<b>Średnie tętno:</b>"), row, 0)
        self.stats_layout.addWidget(QLabel(f"{stats['avg_heartbeat']:.1f} BPM"), row, 1)
        
        # Average stress
        self.stats_layout.addWidget(QLabel("<b>Średni stres:</b>"), row, 2)
        self.stats_layout.addWidget(QLabel(f"{stats['avg_stress']:.2f}"), row, 3)
        row += 1
        
        # Rest quality
        self.stats_layout.addWidget(QLabel("<b>Jakość odpoczynku:</b>"), row, 0)
        self.stats_layout.addWidget(QLabel(f"{stats['avg_rest_quality']:.1f}/10"), row, 1)
        
        # Total interruptions
        self.stats_layout.addWidget(QLabel("<b>Przerwania:</b>"), row, 2)
        self.stats_layout.addWidget(QLabel(str(stats['total_interruptions'])), row, 3)
        row += 1
        
        # Best day
        if stats['best_day']:
            best_date = datetime.strptime(stats['best_day'], '%Y-%m-%d')
            self.stats_layout.addWidget(QLabel("<b>Najlepszy dzień:</b>"), row, 0)
            self.stats_layout.addWidget(QLabel(f"{best_date.strftime('%A')} ({stats['best_day_quality']:.1f})"), row, 1)
        
        # Worst day
        if stats['worst_day']:
            worst_date = datetime.strptime(stats['worst_day'], '%Y-%m-%d')
            self.stats_layout.addWidget(QLabel("<b>Najgorszy dzień:</b>"), row, 2)
            self.stats_layout.addWidget(QLabel(f"{worst_date.strftime('%A')} ({stats['worst_day_quality']:.1f})"), row, 3)

    def _create_weekly_charts(self, data, start_of_week):
        """Create weekly trend charts."""
        if not data:
            return
            
        # Clear existing charts
        for i in reversed(range(self.charts_layout.count())): 
            self.charts_layout.itemAt(i).widget().setParent(None)

        df = pd.DataFrame(data)
        
        # Create full week dataframe with all days
        full_week_data = []
        for i in range(7):
            current_date = start_of_week + timedelta(days=i)
            day_data = df[df['date'].dt.date == current_date.date()]
            
            if not day_data.empty:
                full_week_data.append(day_data.iloc[0].to_dict())
            else:
                full_week_data.append({
                    'date': current_date,
                    'sessions': 0,
                    'total_time': 0,
                    'avg_heartbeat': 0,
                    'avg_stress': 0,
                    'avg_quality': 0,
                    'interruptions': 0,
                    'avg_score': 0
                })
        
        full_df = pd.DataFrame(full_week_data)
        full_df['day_name'] = full_df['date'].dt.strftime('%A')
        full_df['day_short'] = full_df['date'].dt.strftime('%a')
        
        # Set matplotlib style
        plt.style.use('default')
        
        # Create figure with subplots
        fig = Figure(figsize=(14, 10))
        
        # Daily sessions trend
        ax1 = fig.add_subplot(3, 2, 1)
        bars1 = ax1.bar(full_df['day_short'], full_df['sessions'], color='lightgray', 
                       edgecolor='black', linewidth=1)
        ax1.set_title('Sesje według dni tygodnia')
        ax1.set_xlabel('Dzień tygodnia')
        ax1.set_ylabel('Liczba sesji')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, value in zip(bars1, full_df['sessions']):
            if value > 0:
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                        str(int(value)), ha='center', va='bottom')
        
        # Daily time trend
        ax2 = fig.add_subplot(3, 2, 2)
        time_minutes = full_df['total_time'] / 60
        bars2 = ax2.bar(full_df['day_short'], time_minutes, color='lightgray', 
                       edgecolor='black', linewidth=1)
        ax2.set_title('Czas przerw według dni')
        ax2.set_xlabel('Dzień tygodnia')
        ax2.set_ylabel('Czas (minuty)')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, value in zip(bars2, time_minutes):
            if value > 0:
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                        f'{int(value)}m', ha='center', va='bottom')
        
        # Heartbeat trend
        ax3 = fig.add_subplot(3, 2, 3)
        valid_heartbeat = full_df[full_df['avg_heartbeat'] > 0]
        if not valid_heartbeat.empty:
            ax3.plot(valid_heartbeat['day_short'], valid_heartbeat['avg_heartbeat'], 
                    marker='o', linewidth=2, color='black', markersize=6)
            ax3.set_title('Średnie tętno w tygodniu')
            ax3.set_xlabel('Dzień tygodnia')
            ax3.set_ylabel('Tętno (BPM)')
            ax3.grid(True, alpha=0.3)
            
            # Add value labels
            for day, heartbeat in zip(valid_heartbeat['day_short'], valid_heartbeat['avg_heartbeat']):
                ax3.annotate(f'{heartbeat:.0f}', (day, heartbeat), 
                           textcoords="offset points", xytext=(0,10), ha='center')
        
        # Stress level trend
        ax4 = fig.add_subplot(3, 2, 4)
        valid_stress = full_df[full_df['avg_stress'] > 0]
        if not valid_stress.empty:
            ax4.plot(valid_stress['day_short'], valid_stress['avg_stress'], 
                    marker='s', linewidth=2, color='gray', markersize=6)
            ax4.set_title('Średni poziom stresu')
            ax4.set_xlabel('Dzień tygodnia')
            ax4.set_ylabel('Poziom stresu')
            ax4.grid(True, alpha=0.3)
            
            # Add value labels
            for day, stress in zip(valid_stress['day_short'], valid_stress['avg_stress']):
                ax4.annotate(f'{stress:.2f}', (day, stress), 
                           textcoords="offset points", xytext=(0,10), ha='center')
        
        # Quality vs Interruptions scatter
        ax5 = fig.add_subplot(3, 2, 5)
        valid_data = full_df[(full_df['avg_quality'] > 0) & (full_df['interruptions'] >= 0)]
        if not valid_data.empty:
            scatter = ax5.scatter(valid_data['interruptions'], valid_data['avg_quality'], 
                                 s=valid_data['sessions']*20, alpha=0.6, color='black')
            ax5.set_title('Jakość vs Przerwania (wielkość = sesje)')
            ax5.set_xlabel('Liczba przerwań')
            ax5.set_ylabel('Jakość odpoczynku')
            ax5.grid(True, alpha=0.3)
            
            # Add day labels
            for _, row in valid_data.iterrows():
                ax5.annotate(row['day_short'], (row['interruptions'], row['avg_quality']),
                           xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # Weekly summary pie chart (active vs inactive days)
        ax6 = fig.add_subplot(3, 2, 6)
        active_days = len(full_df[full_df['sessions'] > 0])
        inactive_days = 7 - active_days
        
        if active_days > 0:
            sizes = [active_days, inactive_days]
            labels = ['Aktywne dni', 'Nieaktywne dni']
            colors = ['lightgray', 'white']
            wedges, texts, autotexts = ax6.pie(sizes, labels=labels, colors=colors, 
                                              autopct='%1.0f', startangle=90,
                                              wedgeprops=dict(edgecolor='black'))
            ax6.set_title('Aktywność w tygodniu')
        
        fig.tight_layout()
        
        # Add chart to layout
        canvas = FigureCanvas(fig)
        self.charts_layout.addWidget(canvas)

    def refresh_stats(self):
        """Refresh the weekly statistics."""
        self.load_weekly_stats()