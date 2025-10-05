# ui/components/theme_manager.py
"""Theme management for the wellness application."""


class ThemeManager:
    """Manages application themes and styling."""
    
    def __init__(self, ui_scaling):
        self.ui_scaling = ui_scaling
    
    def get_wellness_theme_style(self):
        """Get the dark wellness theme stylesheet."""
        # Calculate scaled values
        button_padding_v = self.ui_scaling.scaled_size(12)
        button_padding_h = self.ui_scaling.scaled_size(24)
        border_radius = self.ui_scaling.scaled_size(8)
        frame_border_radius = self.ui_scaling.scaled_size(10)
        stats_card_radius = self.ui_scaling.scaled_size(12)
        stats_card_padding = self.ui_scaling.scaled_size(16)
        font_size = int(14 * self.ui_scaling.font_scale)
        
        return f"""
            QMainWindow {{
                background-color: #1a1d1f;
                color: #e8e9ea;
            }}
            
            QLabel {{
                color: #e8e9ea;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            
            QPushButton {{
                background-color: #2c3034;
                border: 1px solid #404448;
                color: #e8e9ea;
                padding: {button_padding_v}px {button_padding_h}px;
                border-radius: {border_radius}px;
                font-size: {font_size}px;
                font-weight: 500;
            }}
            
            QPushButton:hover {{
                background-color: #363940;
                border-color: #5a6269;
            }}
            
            QPushButton:pressed {{
                background-color: #404448;
            }}
            
            QPushButton.active {{
                background-color: #3d5a80;
                border-color: #5d7ca3;
                color: #ffffff;
            }}
            
            QFrame {{
                background-color: #262a2d;
                border: 1px solid #404448;
                border-radius: {frame_border_radius}px;
            }}
            
            QFrame.stats-card {{
                background-color: #232629;
                border: 1px solid #3a3f44;
                border-radius: {stats_card_radius}px;
                padding: {stats_card_padding}px;
            }}
            
            QScrollArea {{
                background-color: #1a1d1f;
                border: none;
            }}
            
            QScrollArea QWidget {{
                background-color: #1a1d1f;
            }}
        """
    
    def get_button_active_style(self):
        """Get active button style."""
        return """
            QPushButton {
                background-color: #3d5a80;
                border-color: #5d7ca3;
                color: #ffffff;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }
        """
    
    def get_button_inactive_style(self):
        """Get inactive button style."""
        return """
            QPushButton {
                background-color: #2c3034;
                border: 1px solid #404448;
                color: #e8e9ea;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #363940;
                border-color: #5a6269;
            }
        """
    
    def get_scrollarea_style(self):
        """Get scroll area style."""
        return """
            QScrollArea {
                background-color: #1a1d1f;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2c3034;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #404448;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5a6269;
            }
        """