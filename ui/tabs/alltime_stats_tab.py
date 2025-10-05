# ui/tabs/alltime_stats_tab.py

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


class AlltimeStatsTab(QWidget):
    """Zakładka do wyświetlania ogólnych statystyk za wszystkie czasy."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_path = "user_data.db"
        self.user_id = 1  # Assuming single user for now
        self.setLayout(self._setup_layout())
        self.load_alltime_stats()

    def _setup_layout(self):
        main_layout = QVBoxLayout()
        
        # Scroll area for all content
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Header
        header_label = QLabel("<h2>Statystyki za Wszystkie Czasy</h2>")
        header_label.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(header_label)

        # Period info
        self.period_label = QLabel()
        self.period_label.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(self.period_label)

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

    def load_alltime_stats(self):
        """Load and display all-time statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get all-time basic stats
            alltime_stats = self._get_alltime_basic_stats(conn)
            self._display_basic_stats(alltime_stats)
            
            # Get historical data for charts
            historical_data = self._get_historical_data(conn)
            if historical_data:
                self._create_alltime_charts(historical_data, alltime_stats)
            
            conn.close()
            
        except Exception as e:
            print(f"Error loading all-time stats: {e}")

    def _get_alltime_basic_stats(self, conn):
        """Get basic all-time statistics."""
        cursor = conn.cursor()
        
        # Basic session stats
        cursor.execute("""
            SELECT COUNT(*) as total_sessions, 
                   SUM(total_time_seconds) as total_time,
                   AVG(score) as avg_score,
                   AVG(avg_heartbeat) as avg_heartbeat,
                   AVG(stress_level) as avg_stress,
                   AVG(rest_quality_score) as avg_rest_quality,
                   SUM(interruption_count) as total_interruptions,
                   COUNT(DISTINCT DATE(timestamp)) as total_active_days,
                   MIN(DATE(timestamp)) as first_session,
                   MAX(DATE(timestamp)) as last_session,
                   MAX(score) as best_score,
                   MIN(score) as worst_score,
                   MAX(rest_quality_score) as best_quality,
                   MIN(rest_quality_score) as worst_quality
            FROM Sessions 
            WHERE user_id = ?
        """, (self.user_id,))
        
        result = cursor.fetchone()
        
        stats = {
            'total_sessions': result[0] or 0,
            'total_time': result[1] or 0,
            'avg_score': result[2] or 0,
            'avg_heartbeat': result[3] or 0,
            'avg_stress': result[4] or 0,
            'avg_rest_quality': result[5] or 0,
            'total_interruptions': result[6] or 0,
            'total_active_days': result[7] or 0,
            'first_session': result[8],
            'last_session': result[9],
            'best_score': result[10] or 0,
            'worst_score': result[11] or 0,
            'best_quality': result[12] or 0,
            'worst_quality': result[13] or 0
        }
        
        # Calculate period
        if stats['first_session'] and stats['last_session']:
            first_date = datetime.strptime(stats['first_session'], '%Y-%m-%d')
            last_date = datetime.strptime(stats['last_session'], '%Y-%m-%d')
            period_days = (last_date - first_date).days + 1
            stats['period_days'] = period_days
            
            self.period_label.setText(f"<b>Okres: {first_date.strftime('%d.%m.%Y')} - {last_date.strftime('%d.%m.%Y')} ({period_days} dni)</b>")
        else:
            stats['period_days'] = 0
            self.period_label.setText("<b>Brak danych</b>")
        
        # Get streak information
        cursor.execute("""
            SELECT current_streak, longest_streak
            FROM Users 
            WHERE id = ?
        """, (self.user_id,))
        
        streak_result = cursor.fetchone()
        if streak_result:
            stats['current_streak'] = streak_result[0] or 0
            stats['longest_streak'] = streak_result[1] or 0
        else:
            stats['current_streak'] = 0
            stats['longest_streak'] = 0
        
        # Get achievements count
        cursor.execute("""
            SELECT COUNT(*) as earned_achievements
            FROM UserAchievements 
            WHERE user_id = ?
        """, (self.user_id,))
        
        achievements_result = cursor.fetchone()
        stats['earned_achievements'] = achievements_result[0] or 0
        
        # Get total available achievements
        cursor.execute("SELECT COUNT(*) FROM Achievements WHERE is_active = 1")
        total_achievements_result = cursor.fetchone()
        stats['total_achievements'] = total_achievements_result[0] or 0
        
        # Calculate additional metrics
        if stats['period_days'] > 0:
            stats['avg_sessions_per_day'] = stats['total_sessions'] / stats['period_days']
            stats['consistency_rate'] = stats['total_active_days'] / stats['period_days']
        else:
            stats['avg_sessions_per_day'] = 0
            stats['consistency_rate'] = 0
        
        # Get most productive hour
        cursor.execute("""
            SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
            FROM Sessions 
            WHERE user_id = ?
            GROUP BY hour
            ORDER BY count DESC
            LIMIT 1
        """, (self.user_id,))
        
        hour_result = cursor.fetchone()
        stats['most_productive_hour'] = hour_result[0] if hour_result else None
        
        # Get most active day of week
        cursor.execute("""
            SELECT strftime('%w', timestamp) as day_of_week, COUNT(*) as count
            FROM Sessions 
            WHERE user_id = ?
            GROUP BY day_of_week
            ORDER BY count DESC
            LIMIT 1
        """, (self.user_id,))
        
        day_result = cursor.fetchone()
        if day_result:
            days = ['Niedziela', 'Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota']
            stats['most_active_day'] = days[int(day_result[0])]
        else:
            stats['most_active_day'] = None
        
        return stats

    def _get_historical_data(self, conn):
        """Get historical data for trend analysis."""
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DATE(timestamp) as date,
                   COUNT(*) as sessions,
                   SUM(total_time_seconds) as total_time,
                   AVG(avg_heartbeat) as avg_heartbeat,
                   AVG(stress_level) as avg_stress,
                   AVG(rest_quality_score) as avg_quality,
                   SUM(interruption_count) as interruptions,
                   AVG(score) as avg_score,
                   strftime('%w', timestamp) as day_of_week,
                   strftime('%H', timestamp) as hour
            FROM Sessions 
            WHERE user_id = ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        """, (self.user_id,))
        
        daily_results = cursor.fetchall()
        
        if not daily_results:
            return None
        
        data = []
        for row in daily_results:
            data.append({
                'date': datetime.strptime(row[0], '%Y-%m-%d'),
                'sessions': row[1],
                'total_time': row[2] or 0,
                'avg_heartbeat': row[3] or 0,
                'avg_stress': row[4] or 0,
                'avg_quality': row[5] or 0,
                'interruptions': row[6] or 0,
                'avg_score': row[7] or 0,
                'day_of_week': int(row[8]),
                'hour': int(row[9])
            })
        
        # Get hourly distribution
        cursor.execute("""
            SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
            FROM Sessions 
            WHERE user_id = ?
            GROUP BY hour
            ORDER BY hour
        """, (self.user_id,))
        
        hourly_data = cursor.fetchall()
        
        return {
            'daily': data,
            'hourly': hourly_data
        }

    def _display_basic_stats(self, stats):
        """Display basic statistics in the stats frame."""
        # Clear existing widgets
        for i in reversed(range(self.stats_layout.count())): 
            self.stats_layout.itemAt(i).widget().setParent(None)

        row = 0
        
        # Total sessions
        self.stats_layout.addWidget(QLabel("<b>Łączne sesje:</b>"), row, 0)
        self.stats_layout.addWidget(QLabel(str(stats['total_sessions'])), row, 1)
        
        # Total time
        total_hours = stats['total_time'] // 3600
        total_minutes = (stats['total_time'] % 3600) // 60
        self.stats_layout.addWidget(QLabel("<b>Łączny czas:</b>"), row, 2)
        self.stats_layout.addWidget(QLabel(f"{total_hours}h {total_minutes}m"), row, 3)
        row += 1
        
        # Active days
        self.stats_layout.addWidget(QLabel("<b>Aktywne dni:</b>"), row, 0)
        self.stats_layout.addWidget(QLabel(str(stats['total_active_days'])), row, 1)
        
        # Consistency rate
        self.stats_layout.addWidget(QLabel("<b>Regularność:</b>"), row, 2)
        self.stats_layout.addWidget(QLabel(f"{stats['consistency_rate']:.1%}"), row, 3)
        row += 1
        
        # Average sessions per day
        self.stats_layout.addWidget(QLabel("<b>Średnio sesji/dzień:</b>"), row, 0)
        self.stats_layout.addWidget(QLabel(f"{stats['avg_sessions_per_day']:.1f}"), row, 1)
        
        # Current streak
        self.stats_layout.addWidget(QLabel("<b>Obecna passa:</b>"), row, 2)
        self.stats_layout.addWidget(QLabel(f"{stats['current_streak']} dni"), row, 3)
        row += 1
        
        # Longest streak
        self.stats_layout.addWidget(QLabel("<b>Najdłuższa passa:</b>"), row, 0)
        self.stats_layout.addWidget(QLabel(f"{stats['longest_streak']} dni"), row, 1)
        
        # Achievements
        self.stats_layout.addWidget(QLabel("<b>Osiągnięcia:</b>"), row, 2)
        self.stats_layout.addWidget(QLabel(f"{stats['earned_achievements']}/{stats['total_achievements']}"), row, 3)
        row += 1
        
        # Best/worst scores
        self.stats_layout.addWidget(QLabel("<b>Najlepszy wynik:</b>"), row, 0)
        self.stats_layout.addWidget(QLabel(f"{stats['best_score']:.1f}"), row, 1)
        
        self.stats_layout.addWidget(QLabel("<b>Najgorszy wynik:</b>"), row, 2)
        self.stats_layout.addWidget(QLabel(f"{stats['worst_score']:.1f}"), row, 3)
        row += 1
        
        # Health averages
        self.stats_layout.addWidget(QLabel("<b>Średnie tętno:</b>"), row, 0)
        self.stats_layout.addWidget(QLabel(f"{stats['avg_heartbeat']:.1f} BPM"), row, 1)
        
        self.stats_layout.addWidget(QLabel("<b>Średni stres:</b>"), row, 2)
        self.stats_layout.addWidget(QLabel(f"{stats['avg_stress']:.2f}"), row, 3)
        row += 1
        
        # Most productive patterns
        if stats['most_productive_hour']:
            self.stats_layout.addWidget(QLabel("<b>Najaktywniejsza godzina:</b>"), row, 0)
            self.stats_layout.addWidget(QLabel(f"{stats['most_productive_hour']}:00"), row, 1)
        
        if stats['most_active_day']:
            self.stats_layout.addWidget(QLabel("<b>Najaktywniejszy dzień:</b>"), row, 2)
            self.stats_layout.addWidget(QLabel(stats['most_active_day']), row, 3)

    def _create_alltime_charts(self, data, stats):
        """Create all-time overview charts."""
        if not data or not data['daily']:
            return
            
        # Clear existing charts
        for i in reversed(range(self.charts_layout.count())): 
            self.charts_layout.itemAt(i).widget().setParent(None)

        df = pd.DataFrame(data['daily'])
        
        # Set matplotlib style
        plt.style.use('default')
        
        # Create figure with subplots
        fig = Figure(figsize=(16, 12))
        
        # Long-term trend (sessions over time)
        ax1 = fig.add_subplot(3, 3, 1)
        ax1.plot(df['date'], df['sessions'], linewidth=1, color='black', alpha=0.7)
        
        # Add moving average
        if len(df) > 7:
            df['sessions_ma'] = df['sessions'].rolling(window=7, center=True).mean()
            ax1.plot(df['date'], df['sessions_ma'], linewidth=2, color='gray', 
                    label='Średnia 7-dniowa')
            ax1.legend()
        
        ax1.set_title('Trend sesji w czasie')
        ax1.set_xlabel('Data')
        ax1.set_ylabel('Sesje dziennie')
        ax1.grid(True, alpha=0.3)
        
        # Quality trend over time
        ax2 = fig.add_subplot(3, 3, 2)
        quality_data = df[df['avg_quality'] > 0]
        if not quality_data.empty:
            ax2.plot(quality_data['date'], quality_data['avg_quality'], 
                    linewidth=1, color='black', alpha=0.7)
            
            # Add trend line
            if len(quality_data) > 2:
                z = np.polyfit(range(len(quality_data)), quality_data['avg_quality'], 1)
                p = np.poly1d(z)
                trend_line = p(range(len(quality_data)))
                ax2.plot(quality_data['date'], trend_line, '--', color='gray', 
                        label=f'Trend: {"↗️" if z[0] > 0 else "↘️"}')
                ax2.legend()
            
            ax2.set_title('Trend jakości odpoczynku')
            ax2.set_xlabel('Data')
            ax2.set_ylabel('Jakość odpoczynku')
            ax2.grid(True, alpha=0.3)
        
        # Day of week analysis
        ax3 = fig.add_subplot(3, 3, 3)
        day_names = ['Niedziela', 'Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota']
        day_sessions = df.groupby('day_of_week')['sessions'].sum().reindex(range(7), fill_value=0)
        
        bars3 = ax3.bar([day_names[i] for i in range(7)], day_sessions.values, 
                       color='lightgray', edgecolor='black', linewidth=1)
        ax3.set_title('Aktywność według dni tygodnia')
        ax3.set_xlabel('Dzień tygodnia')
        ax3.set_ylabel('Łączne sesje')
        ax3.tick_params(axis='x', rotation=45)
        
        # Find max day and highlight it
        max_day_idx = day_sessions.values.argmax()
        bars3[max_day_idx].set_color('gray')
        
        # Cumulative time over period
        ax4 = fig.add_subplot(3, 3, 4)
        df['cumulative_time'] = df['total_time'].cumsum() / 3600  # Convert to hours
        ax4.plot(df['date'], df['cumulative_time'], linewidth=2, color='black')
        ax4.set_title('Skumulowany czas przerw')
        ax4.set_xlabel('Data')
        ax4.set_ylabel('Czas (godziny)')
        ax4.grid(True, alpha=0.3)
        
        # Add milestone markers
        milestones = [10, 25, 50, 100]  # Hours
        for milestone in milestones:
            milestone_data = df[df['cumulative_time'] >= milestone]
            if not milestone_data.empty:
                first_milestone = milestone_data.iloc[0]
                ax4.axhline(y=milestone, color='gray', linestyle='--', alpha=0.5)
                ax4.text(first_milestone['date'], milestone + 2, f'{milestone}h', 
                        ha='left', va='bottom', fontsize=8)
        
        # Heartbeat vs Stress correlation
        ax5 = fig.add_subplot(3, 3, 5)
        valid_health = df[(df['avg_heartbeat'] > 0) & (df['avg_stress'] > 0)]
        if not valid_health.empty:
            scatter = ax5.scatter(valid_health['avg_heartbeat'], valid_health['avg_stress'], 
                                 s=valid_health['sessions']*10, alpha=0.6, color='black')
            ax5.set_title('Tętno vs Stres (wszystkie sesje)')
            ax5.set_xlabel('Średnie tętno (BPM)')
            ax5.set_ylabel('Poziom stresu')
            ax5.grid(True, alpha=0.3)
            
            # Add correlation
            correlation = np.corrcoef(valid_health['avg_heartbeat'], valid_health['avg_stress'])[0, 1]
            ax5.text(0.05, 0.95, f'Korelacja: {correlation:.3f}', transform=ax5.transAxes,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        # Session distribution histogram
        ax6 = fig.add_subplot(3, 3, 6)
        ax6.hist(df['sessions'], bins=max(int(df['sessions'].max()), 1), 
                alpha=0.7, color='lightgray', edgecolor='black')
        ax6.set_title('Rozkład dziennych sesji')
        ax6.set_xlabel('Sesje dziennie')
        ax6.set_ylabel('Częstotliwość (dni)')
        ax6.grid(True, alpha=0.3, axis='y')
        
        # Performance metrics radar-like comparison
        ax7 = fig.add_subplot(3, 3, 7)
        
        # Normalize metrics to 0-100 scale for comparison
        metrics = {
            'Sesje': (stats['avg_sessions_per_day'] / max(stats['avg_sessions_per_day'], 1)) * 100,
            'Jakość': (stats['avg_rest_quality'] / 10) * 100,
            'Regularność': stats['consistency_rate'] * 100,
            'Niski stres': (1 - min(stats['avg_stress'], 1)) * 100,
            'Osiągnięcia': (stats['earned_achievements'] / max(stats['total_achievements'], 1)) * 100
        }
        
        bars7 = ax7.barh(list(metrics.keys()), list(metrics.values()), 
                        color='lightgray', edgecolor='black', linewidth=1)
        ax7.set_title('Ogólna wydajność (%)')
        ax7.set_xlabel('Procent maksymalnej wartości')
        ax7.set_xlim(0, 100)
        
        # Add value labels
        for bar, value in zip(bars7, metrics.values()):
            ax7.text(value + 2, bar.get_y() + bar.get_height()/2, 
                    f'{value:.0f}%', va='center', ha='left')
        
        # Monthly aggregation
        ax8 = fig.add_subplot(3, 3, 8)
        df['month'] = df['date'].dt.to_period('M')
        monthly_stats = df.groupby('month').agg({
            'sessions': 'sum',
            'total_time': 'sum',
            'avg_quality': 'mean'
        }).reset_index()
        
        if not monthly_stats.empty:
            ax8_twin = ax8.twinx()
            
            bars8 = ax8.bar(range(len(monthly_stats)), monthly_stats['sessions'], 
                           alpha=0.7, color='lightgray', edgecolor='black', linewidth=1)
            ax8.set_title('Miesięczne podsumowanie')
            ax8.set_xlabel('Miesiąc')
            ax8.set_ylabel('Sesje', color='black')
            ax8.set_xticks(range(len(monthly_stats)))
            ax8.set_xticklabels([str(m) for m in monthly_stats['month']], rotation=45)
            
            # Quality line on secondary axis
            quality_line = ax8_twin.plot(range(len(monthly_stats)), monthly_stats['avg_quality'], 
                                        color='gray', marker='o', linewidth=2, label='Jakość')
            ax8_twin.set_ylabel('Średnia jakość', color='gray')
            ax8_twin.tick_params(axis='y', labelcolor='gray')
        
        # Achievement progress over time
        ax9 = fig.add_subplot(3, 3, 9)
        
        # Simple achievement progress visualization
        achievement_progress = stats['earned_achievements'] / max(stats['total_achievements'], 1)
        
        # Create a simple progress pie chart
        sizes = [achievement_progress, 1 - achievement_progress]
        labels = ['Zdobyte', 'Pozostałe']
        colors = ['lightgray', 'white']
        
        wedges, texts, autotexts = ax9.pie(sizes, labels=labels, colors=colors, 
                                          autopct=lambda pct: f'{pct:.1f}%' if pct > 5 else '',
                                          startangle=90, wedgeprops=dict(edgecolor='black'))
        ax9.set_title(f'Postęp osiągnięć\n({stats["earned_achievements"]}/{stats["total_achievements"]})')
        
        fig.tight_layout()
        
        # Add chart to layout
        canvas = FigureCanvas(fig)
        self.charts_layout.addWidget(canvas)

    def refresh_stats(self):
        """Refresh the all-time statistics."""
        self.load_alltime_stats()