# ui/components/ui_scaling.py
"""UI scaling utilities for responsive design."""

from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtGui import QFont


class UIScaling:
    """Handles UI scaling calculations and font management."""
    
    def __init__(self):
        self.ui_scale = 1.0
        self.font_scale = 1.0
        self.calculate_ui_scaling()
    
    def calculate_ui_scaling(self):
        """Calculate UI scaling factor based on screen DPI and resolution."""
        try:
            desktop = QDesktopWidget()
            screen_rect = desktop.screenGeometry()
            
            # Get screen DPI
            app = QApplication.instance()
            if app is None:
                import sys
                temp_app = QApplication(sys.argv if hasattr(sys, 'argv') else [])
                desktop = QDesktopWidget()
                screen_rect = desktop.screenGeometry()
            
            # Try to get DPI information
            try:
                dpi = desktop.logicalDpiX()
            except:
                dpi = 96
            
            # Base DPI (Windows standard)
            base_dpi = 96.0
            
            # Calculate DPI scaling factor
            dpi_scale = dpi / base_dpi
            
            # Get screen geometry
            screen_width = screen_rect.width()
            screen_height = screen_rect.height()
            
            # Base resolution scaling (1920x1080 as reference)
            base_width = 1920
            base_height = 1080
            
            resolution_scale_x = screen_width / base_width
            resolution_scale_y = screen_height / base_height
            resolution_scale = min(resolution_scale_x, resolution_scale_y)
            
            # Combine DPI and resolution scaling
            combined_scale = (dpi_scale * 0.7) + (resolution_scale * 0.3)
            
            # Clamp scaling between reasonable bounds
            self.ui_scale = max(0.8, min(2.0, combined_scale))
            
            # Font scaling (slightly different curve for better readability)
            self.font_scale = max(0.9, min(1.8, combined_scale * 0.95))
            
            print(f"UI Scaling - Screen: {screen_width}x{screen_height}, DPI: {dpi}")
            print(f"DPI Scale: {dpi_scale:.2f}, Resolution Scale: {resolution_scale:.2f}")
            print(f"Final UI Scale: {self.ui_scale:.2f}, Font Scale: {self.font_scale:.2f}")
            
        except Exception as e:
            print(f"Error calculating UI scaling: {e}")
            # Fallback scaling
            self.ui_scale = 1.0
            self.font_scale = 1.0

    def scaled_font(self, family, size, weight=QFont.Normal):
        """Create a font with scaled size."""
        scaled_size = int(size * self.font_scale)
        return QFont(family, scaled_size, weight)

    def scaled_size(self, size):
        """Scale a size value."""
        return int(size * self.ui_scale)

    def get_responsive_margins(self, window_width):
        """Get responsive margins based on window size."""
        if window_width < 1200:
            return self.scaled_size(15)
        elif window_width < 1600:
            return self.scaled_size(20)
        else:
            return self.scaled_size(30)