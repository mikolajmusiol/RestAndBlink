# ui/components/achievements_widgets.py
"""Achievement widgets for displaying user achievements."""

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QGridLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class AchievementsWidgets:
    """Factory class for creating achievement widgets."""
    
    def __init__(self, ui_scaling):
        self.ui_scaling = ui_scaling
    
    def create_achievement_tooltip(self, achievement):
        """Create a formatted tooltip for an achievement."""
        description = achievement.get('description', 'No description available')
        earned_status = "✅ EARNED" if achievement['earned'] else "🔒 NOT EARNED"
        rarity_display = f"Rarity: {achievement['rarity'].upper()}"
        
        # Create rich tooltip text with HTML formatting
        tooltip_text = f"""<div style="background-color: #2c3034; color: #e8e9ea; padding: 10px; border-radius: 8px; max-width: 300px;">
<h3 style="color: #7cb9e8; margin: 0 0 5px 0;">{achievement['name']}</h3>
<p style="color: #90e0ef; margin: 0 0 8px 0; font-weight: bold;">{earned_status}</p>
<p style="color: #a8dadc; margin: 0 0 8px 0; font-size: 12px;">{rarity_display}</p>
<p style="margin: 0; line-height: 1.4;">{description}</p>
</div>"""
        return tooltip_text
    
    def create_responsive_achievements_grid(self, earned_achievements, all_achievements, window_width):
        """Create a responsive grid that adapts to screen width."""
        # Sort achievements: earned first, then unearned
        sorted_achievements = []
        # Add earned achievements first
        for achievement in all_achievements:
            if achievement['id'] in [ea['id'] for ea in earned_achievements]:
                sorted_achievements.append({**achievement, 'earned': True})
        # Then add unearned achievements
        for achievement in all_achievements:
            if achievement['id'] not in [ea['id'] for ea in earned_achievements]:
                sorted_achievements.append({**achievement, 'earned': False})

        # Calculate dynamic columns based on window width
        available_width = window_width - 120  # Account for margins and scrollbar
        card_width_with_spacing = 220  # Adjusted for new card sizes (200px avg + 20px spacing)
        min_columns = 2  # Changed from 3 to 2 for better mobile/narrow screen support
        max_columns = 10  # Increased max for ultra-wide screens
        columns = max(min_columns, min(max_columns, available_width // card_width_with_spacing))

        # Create dynamic grid layout for achievements
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(20)

        # Add achievement cards in responsive grid
        row = 0
        col = 0
        for achievement in sorted_achievements:
            card = self.create_achievement_card(achievement, window_width)
            grid_layout.addWidget(card, row, col, Qt.AlignmentFlag.AlignCenter)

            col += 1
            if col >= columns:
                col = 0
                row += 1

        # Create widget to hold the grid
        grid_widget = QWidget()
        grid_widget.setLayout(grid_layout)

        return grid_widget

    def create_achievement_card(self, achievement, window_width):
        """Create a single achievement card."""
        card = QFrame()
        card.setMinimumSize(180, 130)  # Smaller minimum for narrow screens
        card.setMaximumSize(320, 200)  # Larger maximum for wide screens
        card.setFrameStyle(QFrame.NoFrame)  # Remove frame style
        
        # Set tooltip with achievement description
        tooltip_text = self.create_achievement_tooltip(achievement)
        card.setToolTip(tooltip_text)

        # Simple style without borders/ovals
        if achievement['earned']:
            card.setStyleSheet("""
                QFrame {
                    background-color: #2a2d30;
                    border: none;
                    border-radius: 8px;
                }
                QFrame:hover {
                    background-color: #323639;
                }
            """)
        else:
            card.setStyleSheet("""
                QFrame {
                    background-color: #1e2125;
                    border: none;
                    border-radius: 8px;
                }
                QFrame:hover {
                    background-color: #252932;
                }
            """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Achievement icon - use reliable symbols instead of problematic emoji
        original_emoji = achievement['badge_icon']

        # Complete mapping to Unicode symbols that work reliably on Linux
        symbol_mapping = {
            '🎯': '●',     # Target -> Bullet
            '🚀': '▲',     # Rocket -> Triangle
            '💪': '♦',     # Muscle -> Diamond
            '⭐': '★',     # Star -> Star (should work)
            '🏃': '►',     # Runner -> Play symbol
            '👑': '♔',     # Crown -> King
            '🔸': '◇',     # Orange diamond -> White diamond
            '🔹': '◆',     # Blue diamond -> Black diamond
            '🔶': '◆',     # Large orange diamond -> Black diamond
            '🔷': '◇',     # Large blue diamond -> White diamond
            '⏰': '⊙',     # Alarm clock -> Circled dot
            '⏳': '⧗',     # Hourglass -> Hourglass symbol
        }

        # Use symbol mapping - fallback to first character if not found
        display_icon = symbol_mapping.get(original_emoji, original_emoji[0] if original_emoji else '•')

        icon_label = QLabel(display_icon)
        # Set the same tooltip for the icon
        icon_label.setToolTip(tooltip_text)

        # Dynamic font size
        if window_width > 1400:
            icon_font_size = 56
        elif window_width > 1000:
            icon_font_size = 52
        else:
            icon_font_size = 48

        # Use standard font that supports Unicode symbols
        symbol_font = QFont()
        symbol_font.setPointSize(icon_font_size)
        symbol_font.setFamily("DejaVu Sans")  # Reliable font for symbols
        symbol_font.setWeight(QFont.Bold)  # Make symbols more prominent

        icon_label.setFont(symbol_font)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Enhanced styling with color coding for different rarities
        rarity_colors = {
            'common': '#9ca3af',
            'uncommon': '#22c55e',
            'rare': '#3b82f6',
            'epic': '#a855f7',
            'legendary': '#f59e0b',
            'mythic': '#ff1744'
        }

        if not achievement['earned']:
            # Gray out unearned achievements
            icon_label.setStyleSheet("""
                QLabel {
                    color: #4a4d52;
                    font-weight: bold;
                    text-align: center;
                    background: transparent;
                }
            """)
        else:
            # Color earned achievements by rarity
            icon_color = rarity_colors.get(achievement['rarity'], '#ffffff')
            icon_label.setStyleSheet(f"""
                QLabel {{
                    color: {icon_color};
                    font-weight: bold;
                    text-align: center;
                    background: transparent;
                }}
            """)

        # Achievement name - shorter and cleaner
        name_label = QLabel(achievement['name'])
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setFont(self.ui_scaling.scaled_font("Segoe UI", 12, QFont.Bold))
        # Set the same tooltip for the name
        name_label.setToolTip(tooltip_text)
        if achievement['earned']:
            name_label.setStyleSheet(f"color: #ffffff; margin-top: {self.ui_scaling.scaled_size(5)}px;")
        else:
            name_label.setStyleSheet(f"color: #8b9197; margin-top: {self.ui_scaling.scaled_size(5)}px;")

        # Rarity indicator - smaller and more subtle
        rarity_label = QLabel(achievement['rarity'].upper())
        rarity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rarity_label.setFont(self.ui_scaling.scaled_font("Segoe UI", 8, QFont.Bold))
        # Set the same tooltip for the rarity
        rarity_label.setToolTip(tooltip_text)

        # Color code by rarity
        rarity_color = rarity_colors.get(achievement['rarity'], '#9ca3af')
        if not achievement['earned']:
            rarity_color = '#5a6269'  # Gray out unearned

        rarity_label.setStyleSheet(f"color: {rarity_color}; margin-top: 3px;")

        layout.addWidget(icon_label)
        layout.addWidget(name_label)
        layout.addWidget(rarity_label)

        return card