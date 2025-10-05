# ui/components/stats_widgets.py
"""Statistics widgets for displaying metrics and data."""

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class StatsWidgets:
    """Factory class for creating statistics widgets."""
    
    def __init__(self, ui_scaling):
        self.ui_scaling = ui_scaling
    
    def create_quick_stat_card(self, title, value, color):
        """Create a simple, clean quick stat card."""
        card = QFrame()
        card.setFrameStyle(QFrame.NoFrame)
        
        # Standard size that works well
        card.setFixedSize(self.ui_scaling.scaled_size(180), self.ui_scaling.scaled_size(75))
        
        # Clean, simple styling
        border_radius = self.ui_scaling.scaled_size(8)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #232629;
                border: none;
                border-radius: {border_radius}px;
            }}
            QFrame:hover {{
                background-color: #2a2d30;
            }}
        """)

        # Simple layout with reasonable margins
        layout = QVBoxLayout(card)
        layout.setContentsMargins(
            self.ui_scaling.scaled_size(10), 
            self.ui_scaling.scaled_size(12), 
            self.ui_scaling.scaled_size(10), 
            self.ui_scaling.scaled_size(10)
        )
        layout.setSpacing(self.ui_scaling.scaled_size(5))
        
        # Title label
        title_label = QLabel(title)
        title_label.setFont(self.ui_scaling.scaled_font("Segoe UI", 9))
        title_label.setStyleSheet(f"color: {color}; background: transparent;")
        title_label.setWordWrap(True)
        
        # Value label
        value_label = QLabel(value)
        value_label.setFont(self.ui_scaling.scaled_font("Segoe UI", 12, QFont.Bold))
        value_label.setStyleSheet("color: #e8e9ea; background: transparent;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()
        
        return card
    
    def create_metric_widget(self, title, value, range_text, color):
        """Create a metric widget with title, value, and optional range."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.ui_scaling.scaled_size(10))
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(self.ui_scaling.scaled_font("Segoe UI", 14, QFont.Medium))
        title_label.setStyleSheet(f"color: {color};")
        
        # Value
        value_label = QLabel(value)
        value_label.setFont(self.ui_scaling.scaled_font("Segoe UI", 24, QFont.Bold))
        value_label.setStyleSheet("color: #e8e9ea;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()
        
        # Range (if provided)
        if range_text:
            range_label = QLabel(range_text)
            range_label.setFont(self.ui_scaling.scaled_font("Segoe UI", 12))
            range_label.setStyleSheet("color: #a8b5c1;")
            range_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
            layout.addWidget(range_label)
        
        return widget
    
    def create_avg_stats_widget(self, data, ui_scaling):
        """Create the average stats widget."""
        avg_stats_widget = QFrame()
        avg_stats_widget.setProperty("class", "stats-card")
        avg_stats_widget.setMaximumWidth(250)
        avg_stats_layout = QVBoxLayout(avg_stats_widget)
        avg_stats_layout.setContentsMargins(20, 20, 20, 20)
        avg_stats_layout.setSpacing(30)
        
        # Calculate averages from data
        if data and len(data) > 0:
            heartbeats = [d.get('heartbeat', 0) for d in data if d.get('heartbeat', 0) > 0]
            stress_levels = [d.get('stress', 0) for d in data if d.get('stress', 0) > 0]
            
            avg_heartbeat = sum(heartbeats) / len(heartbeats) if heartbeats else 0
            min_heartbeat = min(heartbeats) if heartbeats else 0
            max_heartbeat = max(heartbeats) if heartbeats else 0
            
            avg_stress = sum(stress_levels) / len(stress_levels) if stress_levels else 0
            min_stress = min(stress_levels) if stress_levels else 0
            max_stress = max(stress_levels) if stress_levels else 0
        else:
            avg_heartbeat = min_heartbeat = max_heartbeat = 0
            avg_stress = min_stress = max_stress = 0
        
        # Average heartbeat section
        avg_hb_widget = self.create_metric_widget(
            "Average Heartbeat", 
            f"{avg_heartbeat:.1f} BPM", 
            f"{min_heartbeat:.0f}/{max_heartbeat:.0f}",
            "#7cb9e8"
        )
        
        # Average stress section
        avg_stress_widget = self.create_metric_widget(
            "Average Stress",
            f"{avg_stress:.3f}",
            f"{min_stress:.2f}/{max_stress:.2f}",
            "#f4a261"
        )
        
        avg_stats_layout.addWidget(avg_hb_widget)
        avg_stats_layout.addWidget(avg_stress_widget)
        avg_stats_layout.addStretch()
        
        return avg_stats_widget
    
    def create_right_stats_widget(self, data, period, db_stats):
        """Create the right stats widget with time and score."""
        right_stats_widget = QFrame()
        right_stats_widget.setProperty("class", "stats-card")
        right_stats_widget.setMaximumWidth(250)
        right_stats_layout = QVBoxLayout(right_stats_widget)
        right_stats_layout.setContentsMargins(20, 20, 20, 20)
        right_stats_layout.setSpacing(30)
        
        # Calculate totals from data
        total_time = sum([d.get('duration', 0) for d in data]) if data else 0
        total_score = sum([d.get('score', 0) for d in data]) if data else 0
        
        # Use database stats if available
        if db_stats:
            total_time = db_stats['total_time']
            total_score = db_stats['total_score']
        
        # Rest time section
        rest_minutes = total_time / 60
        rest_time_widget = self.create_metric_widget(
            "Rest in min",
            f"{rest_minutes:.0f} min",
            "",
            "#90e0ef"
        )
        
        # Score section
        period_names = {
            'daily': 'Today Score',
            'weekly': 'Weekly Score', 
            'monthly': 'Monthly Score',
            'alltime': 'All Time Score'
        }
        
        score_widget = self.create_metric_widget(
            period_names.get(period, 'Score'),
            f"{total_score:.0f}",
            "",
            "#a8dadc"
        )
        
        # Improve note
        improve_note = QLabel("Improve note")
        improve_note.setFont(self.ui_scaling.scaled_font("Segoe UI", 12))
        improve_note.setStyleSheet("color: #a8b5c1;")
        improve_note.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        
        right_stats_layout.addWidget(rest_time_widget)
        right_stats_layout.addWidget(score_widget)
        right_stats_layout.addStretch()
        right_stats_layout.addWidget(improve_note)
        
        return right_stats_widget