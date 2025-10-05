# Enhanced Wellness Window - Code Reorganization

## Overview
The original `enhanced_wellness_window.py` file (1695 lines) has been reorganized into a modular architecture with separate components for better maintainability and code organization.

## New File Structure

### Main Files
- `ui/enhanced_wellness_window_new.py` - Main window class (much cleaner, ~400 lines)
- `ui/enhanced_wellness_window.py` - Original file (kept for reference)

### Component Files (`ui/components/`)
- `__init__.py` - Component module initialization
- `ui_scaling.py` - UI scaling and responsive design utilities
- `theme_manager.py` - Theme and styling management
- `database_manager.py` - All database operations
- `chart_widgets.py` - Chart and graph widgets
- `stats_widgets.py` - Statistics display widgets
- `achievements_widgets.py` - Achievement system widgets
- `camera_calibration.py` - Camera calibration functionality

## Benefits of Reorganization

### 1. **Separation of Concerns**
- Each component handles a specific responsibility
- Easier to maintain and debug individual features
- Better code organization and readability

### 2. **Reusability**
- Components can be reused across different parts of the application
- Independent testing of components
- Easier to add new features

### 3. **Maintainability**
- Smaller, focused files are easier to work with
- Changes to one component don't affect others
- Clear interfaces between components

### 4. **Scalability**
- Easy to add new components
- Better structure for team development
- Reduced merge conflicts

## Component Descriptions

### UIScaling (`ui_scaling.py`)
- Handles responsive UI scaling based on screen DPI and resolution
- Provides scaled fonts and sizes
- Calculates responsive margins

### ThemeManager (`theme_manager.py`) 
- Manages application themes and styling
- Provides consistent button styles
- Handles dark wellness theme

### DatabaseManager (`database_manager.py`)
- All database operations in one place
- User data retrieval
- Achievement data management
- Statistics queries
- Calibration data storage

### ChartWidgets (`chart_widgets.py`)
- Creates matplotlib charts for heartbeat and stress data
- Handles chart styling and theming
- Manages data visualization

### StatsWidgets (`stats_widgets.py`)
- Creates statistical display widgets
- Quick stat cards
- Metric widgets with values and ranges
- Average statistics displays

### AchievementsWidgets (`achievements_widgets.py`)
- Handles achievement display and grid layout
- Responsive achievement cards
- Symbol mapping for cross-platform compatibility
- Rarity-based styling

### CameraCalibration (`camera_calibration.py`)
- Complete camera calibration system
- MediaPipe and OpenCV integration
- Eye tracking and head pose estimation
- Multi-monitor calibration support

## Usage Example

```python
from ui.enhanced_wellness_window_new import EnhancedWellnessWindow

# Create and show the application
app = QApplication(sys.argv)
window = EnhancedWellnessWindow(user_id=1)
window.show()
sys.exit(app.exec_())
```

## Migration Notes

### To use the new organized version:
1. Import from `enhanced_wellness_window_new.py` instead of the original
2. All functionality remains the same
3. Components are automatically initialized
4. No changes needed to external code that uses the window

### Key Improvements:
- **Reduced complexity**: Main window class is much simpler
- **Better error handling**: Each component handles its own errors
- **Improved performance**: Components can be loaded on-demand
- **Enhanced testing**: Individual components can be unit tested
- **Future-proof**: Easy to extend with new features

## Dependencies

Each component manages its own dependencies:
- `chart_widgets.py` - matplotlib, PyQt5
- `camera_calibration.py` - cv2, mediapipe, numpy, screeninfo
- `database_manager.py` - sqlite3, json, datetime
- All components - PyQt5 for UI elements

## Configuration

Components can be configured through their constructors:
```python
# Example: Custom database path
db_manager = DatabaseManager(db_path="custom_path.db")

# Example: Different scaling factors
ui_scaling = UIScaling()
ui_scaling.ui_scale = 1.5  # Custom scaling
```

This reorganization makes the codebase much more maintainable while preserving all existing functionality.