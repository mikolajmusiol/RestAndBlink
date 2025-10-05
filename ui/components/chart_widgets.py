# ui/components/chart_widgets.py
"""Chart widgets for displaying statistical data."""

import matplotlib.pyplot as plt
try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
except ImportError:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class ChartWidgets:
    """Factory class for creating chart widgets."""
    
    def __init__(self, ui_scaling):
        self.ui_scaling = ui_scaling
    
    def create_charts_widget(self, data, period):
        """Create the charts widget with real heartbeat and stress data."""
        charts_widget = QFrame()
        charts_widget.setProperty("class", "stats-card")
        charts_widget.setMinimumHeight(500)
        charts_layout = QVBoxLayout(charts_widget)
        charts_layout.setContentsMargins(20, 20, 20, 20)
        
        if data and len(data) > 0:
            # Create matplotlib figure
            fig = Figure(figsize=(8, 6), facecolor='#232629')
            
            # Heartbeat chart
            ax1 = fig.add_subplot(2, 1, 1)
            
            if 'heartbeat' in data[0]:
                timestamps = list(range(len(data)))
                heartbeats = [d['heartbeat'] for d in data]
                
                ax1.plot(timestamps, heartbeats, color='#7cb9e8', linewidth=2)
                ax1.set_title('Heartbeat', color='#e8e9ea', fontsize=14, pad=20)
                ax1.set_ylabel('BPM', color='#a8b5c1')
                ax1.tick_params(colors='#a8b5c1')
                ax1.grid(True, alpha=0.3, color='#404448')
                ax1.set_facecolor('#1a1d1f')
            
            # Stress chart
            ax2 = fig.add_subplot(2, 1, 2)
            
            if 'stress' in data[0]:
                timestamps = list(range(len(data)))
                stress_levels = [d['stress'] for d in data]
                
                ax2.plot(timestamps, stress_levels, color='#f4a261', linewidth=2)
                ax2.set_title('Stress Level', color='#e8e9ea', fontsize=14, pad=20)
                ax2.set_ylabel('Level', color='#a8b5c1')
                ax2.set_xlabel('Time', color='#a8b5c1')
                ax2.tick_params(colors='#a8b5c1')
                ax2.grid(True, alpha=0.3, color='#404448')
                ax2.set_facecolor('#1a1d1f')
            
            fig.tight_layout()
            
            # Create canvas and add to layout
            canvas = FigureCanvas(fig)
            canvas.setStyleSheet("background-color: #232629;")
            charts_layout.addWidget(canvas)
        
        else:
            # Placeholder for no data
            no_data_label = QLabel("No data available for this period")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_data_label.setStyleSheet("color: #a8b5c1; font-size: 16px; margin: 100px;")
            charts_layout.addWidget(no_data_label)
        
        return charts_widget