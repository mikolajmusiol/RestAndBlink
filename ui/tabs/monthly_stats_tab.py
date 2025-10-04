# ui/tabs/monthly_stats_tab.py

import sqlite3
import json
from datetime import datetime, timedelta
from calendar import monthrange
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QGridLayout, QScrollArea, QFrame)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class MonthlyStatsTab(QWidget):
    """Zakładka do wyświetlania miesięcznych statystyk."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_path = "user_data.db"
        self.user_id = 1  # Assuming single user for now
        self.setLayout(self._setup_layout())
        self.load_monthly_stats()

    def _setup_layout(self):
        main_layout = QVBoxLayout()
        
        # Scroll area for all content
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Header
        header_label = QLabel("<h2>Miesięczne Statystyki</h2>")
        header_label.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(header_label)

        # Month info
        self.month_label = QLabel()
        self.month_label.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(self.month_label)

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

    def load_monthly_stats(self):
        """Load and display monthly statistics."""
        # Get current month range
        today = datetime.now()
        start_of_month = today.replace(day=1)
        _, last_day = monthrange(today.year, today.month)
        end_of_month = today.replace(day=last_day)
        
        start_date = start_of_month.strftime('%Y-%m-%d')
        end_date = end_of_month.strftime('%Y-%m-%d')
        
        month_name = today.strftime('%B %Y')
        self.month_label.setText(f"<b>{month_name}</b>")
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get monthly basic stats
            monthly_stats = self._get_monthly_basic_stats(conn, start_date, end_date)
            self._display_basic_stats(monthly_stats)
            
            # Get weekly aggregated data for charts
            weekly_data = self._get_monthly_weekly_data(conn, start_of_month, end_of_month)
            if weekly_data:
                self._create_monthly_charts(weekly_data, start_of_month)
            
            conn.close()
            
        except Exception as e:
            print(f"Error loading monthly stats: {e}")

    def _get_monthly_basic_stats(self, conn, start_date, end_date):
        """Get basic statistics for the month."""
        cursor = conn.cursor()
        
        # Monthly sessions summary
        cursor.execute("""
            SELECT COUNT(*) as sessions, 
                   SUM(total_time_seconds) as total_time,
                   AVG(score) as avg_score,
                   AVG(avg_heartbeat) as avg_heartbeat,
                   AVG(stress_level) as avg_stress,
                   AVG(rest_quality_score) as avg_rest_quality,
                   SUM(interruption_count) as total_interruptions,
                   COUNT(DISTINCT DATE(timestamp)) as active_days,
                   MIN(avg_heartbeat) as min_heartbeat,
                   MAX(avg_heartbeat) as max_heartbeat,
                   MIN(stress_level) as min_stress,
                   MAX(stress_level) as max_stress
            FROM Sessions 
            WHERE user_id = ? AND DATE(timestamp) BETWEEN ? AND ?
            AND avg_heartbeat > 0
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
            'active_days': result[7] or 0,
            'min_heartbeat': result[8] or 0,
            'max_heartbeat': result[9] or 0,
            'min_stress': result[10] or 0,
            'max_stress': result[11] or 0
        }
        
        # Get consistency metrics
        cursor.execute("""
            SELECT DATE(timestamp) as date, COUNT(*) as day_sessions
            FROM Sessions 
            WHERE user_id = ? AND DATE(timestamp) BETWEEN ? AND ?
            GROUP BY DATE(timestamp)
            ORDER BY day_sessions DESC
        """, (self.user_id, start_date, end_date))
        
        daily_sessions = cursor.fetchall()
        
        if daily_sessions:
            sessions_per_day = [row[1] for row in daily_sessions]
            stats['max_daily_sessions'] = max(sessions_per_day)
            stats['consistency'] = len(sessions_per_day) / ((datetime.strptime(end_date, '%Y-%m-%d') - 
                                                           datetime.strptime(start_date, '%Y-%m-%d')).days + 1)
        else:
            stats['max_daily_sessions'] = 0
            stats['consistency'] = 0
        
        # Get improvement trend (compare first half vs second half)
        mid_date = (datetime.strptime(start_date, '%Y-%m-%d') + 
                   (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')) / 2).strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT AVG(rest_quality_score) as avg_quality
            FROM Sessions 
            WHERE user_id = ? AND DATE(timestamp) BETWEEN ? AND ?
            AND rest_quality_score > 0
        """, (self.user_id, start_date, mid_date))
        
        first_half_quality = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT AVG(rest_quality_score) as avg_quality
            FROM Sessions 
            WHERE user_id = ? AND DATE(timestamp) BETWEEN ? AND ?
            AND rest_quality_score > 0
        """, (self.user_id, mid_date, end_date))
        
        second_half_quality = cursor.fetchone()[0] or 0
        
        stats['improvement_trend'] = second_half_quality - first_half_quality
        
        return stats

    def _get_monthly_weekly_data(self, conn, start_of_month, end_of_month):
        """Get weekly aggregated data for the month."""
        cursor = conn.cursor()
        
        # Get all sessions for the month first
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
        """, (self.user_id, start_of_month.strftime('%Y-%m-%d'), end_of_month.strftime('%Y-%m-%d')))
        
        daily_results = cursor.fetchall()
        
        if not daily_results:
            return None
        
        # Group by weeks
        weekly_data = []
        current_week_start = start_of_month - timedelta(days=start_of_month.weekday())
        
        while current_week_start <= end_of_month:
            week_end = current_week_start + timedelta(days=6)
            
            # Filter daily results for this week
            week_sessions = []
            total_sessions = 0
            total_time = 0
            heartbeats = []
            stress_levels = []
            qualities = []
            total_interruptions = 0
            scores = []
            active_days = 0
            
            for daily in daily_results:
                daily_date = datetime.strptime(daily[0], '%Y-%m-%d')
                if current_week_start <= daily_date <= week_end:
                    total_sessions += daily[1]
                    total_time += daily[2] or 0
                    if daily[3] and daily[3] > 0:
                        heartbeats.append(daily[3])
                    if daily[4] and daily[4] > 0:
                        stress_levels.append(daily[4])
                    if daily[5] and daily[5] > 0:
                        qualities.append(daily[5])
                    total_interruptions += daily[6] or 0
                    if daily[7] and daily[7] > 0:
                        scores.append(daily[7])
                    active_days += 1
            
            if total_sessions > 0:
                weekly_data.append({
                    'week_start': current_week_start,
                    'week_end': week_end,
                    'sessions': total_sessions,
                    'total_time': total_time,
                    'avg_heartbeat': np.mean(heartbeats) if heartbeats else 0,
                    'avg_stress': np.mean(stress_levels) if stress_levels else 0,
                    'avg_quality': np.mean(qualities) if qualities else 0,
                    'interruptions': total_interruptions,
                    'avg_score': np.mean(scores) if scores else 0,
                    'active_days': active_days
                })
            
            current_week_start += timedelta(days=7)
        
        return weekly_data

    def _display_basic_stats(self, stats):
        """Display basic statistics in the stats frame."""
        # Clear existing widgets
        for i in reversed(range(self.stats_layout.count())): 
            self.stats_layout.itemAt(i).widget().setParent(None)

        row = 0
        
        # Sessions count
        self.stats_layout.addWidget(QLabel("<b>Sesje w miesiącu:</b>"), row, 0)
        self.stats_layout.addWidget(QLabel(str(stats['sessions'])), row, 1)
        
        # Active days
        self.stats_layout.addWidget(QLabel("<b>Aktywne dni:</b>"), row, 2)
        self.stats_layout.addWidget(QLabel(f"{stats['active_days']} dni"), row, 3)
        row += 1
        
        # Total time
        hours = stats['total_time'] // 3600
        minutes = (stats['total_time'] % 3600) // 60
        self.stats_layout.addWidget(QLabel("<b>Łączny czas:</b>"), row, 0)
        self.stats_layout.addWidget(QLabel(f"{hours}h {minutes}m"), row, 1)
        
        # Consistency
        self.stats_layout.addWidget(QLabel("<b>Regularność:</b>"), row, 2)
        self.stats_layout.addWidget(QLabel(f"{stats['consistency']:.1%}"), row, 3)
        row += 1
        
        # Average heartbeat range
        self.stats_layout.addWidget(QLabel("<b>Zakres tętna:</b>"), row, 0)
        heartbeat_range = f"{stats['min_heartbeat']:.0f}-{stats['max_heartbeat']:.0f} BPM"
        self.stats_layout.addWidget(QLabel(heartbeat_range), row, 1)
        
        # Average stress range
        self.stats_layout.addWidget(QLabel("<b>Zakres stresu:</b>"), row, 2)
        stress_range = f"{stats['min_stress']:.2f}-{stats['max_stress']:.2f}"
        self.stats_layout.addWidget(QLabel(stress_range), row, 3)
        row += 1
        
        # Rest quality
        self.stats_layout.addWidget(QLabel("<b>Średnia jakość:</b>"), row, 0)
        self.stats_layout.addWidget(QLabel(f"{stats['avg_rest_quality']:.1f}/10"), row, 1)
        
        # Max daily sessions
        self.stats_layout.addWidget(QLabel("<b>Najaktywniejszy dzień:</b>"), row, 2)
        self.stats_layout.addWidget(QLabel(f"{stats['max_daily_sessions']} sesji"), row, 3)
        row += 1
        
        # Total interruptions
        self.stats_layout.addWidget(QLabel("<b>Łączne przerwania:</b>"), row, 0)
        self.stats_layout.addWidget(QLabel(str(stats['total_interruptions'])), row, 1)
        
        # Improvement trend
        self.stats_layout.addWidget(QLabel("<b>Trend poprawy:</b>"), row, 2)
        trend_text = "↗️ Poprawa" if stats['improvement_trend'] > 0.1 else "↘️ Spadek" if stats['improvement_trend'] < -0.1 else "→ Stabilny"
        self.stats_layout.addWidget(QLabel(trend_text), row, 3)

    def _create_monthly_charts(self, data, start_of_month):
        """Create monthly trend charts."""
        if not data:
            return
            
        # Clear existing charts
        for i in reversed(range(self.charts_layout.count())): 
            self.charts_layout.itemAt(i).widget().setParent(None)

        df = pd.DataFrame(data)
        df['week_number'] = df['week_start'].apply(lambda x: f"Tydzień {((x - start_of_month).days // 7) + 1}")
        
        # Set matplotlib style
        plt.style.use('default')
        
        # Create figure with subplots
        fig = Figure(figsize=(14, 12))
        
        # Weekly sessions trend
        ax1 = fig.add_subplot(3, 2, 1)
        bars1 = ax1.bar(df['week_number'], df['sessions'], color='lightgray', 
                       edgecolor='black', linewidth=1)
        ax1.set_title('Sesje według tygodni')
        ax1.set_xlabel('Tydzień')
        ax1.set_ylabel('Liczba sesji')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, value in zip(bars1, df['sessions']):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    str(int(value)), ha='center', va='bottom')
        
        # Weekly time trend
        ax2 = fig.add_subplot(3, 2, 2)
        time_hours = df['total_time'] / 3600
        bars2 = ax2.bar(df['week_number'], time_hours, color='lightgray', 
                       edgecolor='black', linewidth=1)
        ax2.set_title('Czas przerw według tygodni')
        ax2.set_xlabel('Tydzień')
        ax2.set_ylabel('Czas (godziny)')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, value in zip(bars2, time_hours):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'{value:.1f}h', ha='center', va='bottom')
        
        # Heartbeat trend over weeks
        ax3 = fig.add_subplot(3, 2, 3)
        valid_heartbeat = df[df['avg_heartbeat'] > 0]
        if not valid_heartbeat.empty:
            ax3.plot(range(len(valid_heartbeat)), valid_heartbeat['avg_heartbeat'], 
                    marker='o', linewidth=2, color='black', markersize=6)
            ax3.set_title('Trend tętna w miesiącu')
            ax3.set_xlabel('Tygodnie')
            ax3.set_ylabel('Średnie tętno (BPM)')
            ax3.set_xticks(range(len(valid_heartbeat)))
            ax3.set_xticklabels([f'T{i+1}' for i in range(len(valid_heartbeat))])
            ax3.grid(True, alpha=0.3)
            
            # Add trend line
            if len(valid_heartbeat) > 1:
                z = np.polyfit(range(len(valid_heartbeat)), valid_heartbeat['avg_heartbeat'], 1)
                p = np.poly1d(z)
                ax3.plot(range(len(valid_heartbeat)), p(range(len(valid_heartbeat))), 
                        "--", color='gray', alpha=0.8)
        
        # Quality vs Stress scatter
        ax4 = fig.add_subplot(3, 2, 4)
        valid_data = df[(df['avg_quality'] > 0) & (df['avg_stress'] > 0)]
        if not valid_data.empty:
            scatter = ax4.scatter(valid_data['avg_stress'], valid_data['avg_quality'], 
                                 s=valid_data['sessions']*10, alpha=0.6, color='black')
            ax4.set_title('Jakość vs Stres (wielkość = sesje)')
            ax4.set_xlabel('Średni poziom stresu')
            ax4.set_ylabel('Jakość odpoczynku')
            ax4.grid(True, alpha=0.3)
            
            # Add week labels
            for i, row in valid_data.iterrows():
                ax4.annotate(f'T{i+1}', (row['avg_stress'], row['avg_quality']),
                           xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # Active days per week
        ax5 = fig.add_subplot(3, 2, 5)
        bars5 = ax5.bar(df['week_number'], df['active_days'], color='lightgray', 
                       edgecolor='black', linewidth=1)
        ax5.set_title('Aktywne dni w tygodniu')
        ax5.set_xlabel('Tydzień')
        ax5.set_ylabel('Aktywne dni')
        ax5.set_ylim(0, 7)
        ax5.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, value in zip(bars5, df['active_days']):
            ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    str(int(value)), ha='center', va='bottom')
        
        # Monthly summary heatmap (quality by week and metric)
        ax6 = fig.add_subplot(3, 2, 6)
        
        # Create data for heatmap
        metrics_data = []
        weeks = []
        
        for i, row in df.iterrows():
            weeks.append(f'T{i+1}')
            metrics_data.append([
                row['avg_quality'] / 10 * 100,  # Scale to 0-100
                (1 - row['avg_stress']) * 100 if row['avg_stress'] > 0 else 50,  # Invert stress
                row['active_days'] / 7 * 100  # Scale to 0-100
            ])
        
        if metrics_data:
            heatmap_data = np.array(metrics_data).T
            im = ax6.imshow(heatmap_data, cmap='Greys', aspect='auto', vmin=0, vmax=100)
            
            ax6.set_title('Miesięczna mapa wydajności (%)')
            ax6.set_xticks(range(len(weeks)))
            ax6.set_xticklabels(weeks)
            ax6.set_yticks(range(3))
            ax6.set_yticklabels(['Jakość', 'Niski stres', 'Aktywność'])
            
            # Add text annotations
            for i in range(len(weeks)):
                for j in range(3):
                    text = ax6.text(i, j, f'{heatmap_data[j, i]:.0f}%',
                                   ha="center", va="center", color="black")
        
        fig.tight_layout()
        
        # Add chart to layout
        canvas = FigureCanvas(fig)
        self.charts_layout.addWidget(canvas)

    def refresh_stats(self):
        """Refresh the monthly statistics."""
        self.load_monthly_stats()