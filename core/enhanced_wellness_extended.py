# core/enhanced_wellness_extended.py
from ui.enhanced_wellness_window import EnhancedWellnessWindow
from core.wellness_integration import MainTimerWidget


class ExtendedWellnessWindow(EnhancedWellnessWindow):
    """Rozszerzona wersja Enhanced Wellness Window z zintegrowaną funkcjonalnością timera."""
    
    def __init__(self, user_id=1):
        super().__init__(user_id)
        self.application_controller = None
        self.main_timer_widget = None
    
    def create_main_page(self):
        """Create main page with integrated timer functionality from main_old.py."""
        # Zamiast pustej strony, tworzymy widget z funkcjonalnością timera
        self.main_timer_widget = MainTimerWidget()
        return self.main_timer_widget
    
    def set_application_controller(self, controller):
        """Ustawia referencję do kontrolera aplikacji."""
        self.application_controller = controller
        if self.main_timer_widget:
            self.main_timer_widget.set_application_controller(controller)