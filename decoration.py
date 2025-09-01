import random
import math
from colorama import Fore
from ascii_art import DECORATIONS, DECORATION_CATEGORIES, COLOR_ADJUSTMENTS
from config import DECORATION_SPAWN_CHANCE, MAX_DECORATIONS


class Decoration:
    """Represents a decoration on the seafloor."""
    def __init__(self, decoration_type, decoration_data, x_pos, width, height, background_color, aquarium_manager):
        self.type = decoration_type
        self.category, self.art = decoration_data
        self.x = x_pos
        self.width = width
        self.aquarium_height = height
        self.background_color = background_color
        self.aquarium_manager = aquarium_manager
        
        # Ensure art is a tuple for consistent processing
        if isinstance(self.art, str):
            self.art = (self.art,)
            
        self.art_height = len(self.art)
        self.art_width = max(len(line) for line in self.art)
        
        # Position on seafloor (above the floor line)
        self.y = height - 1 - self.art_height
        
        # Special state for treasure chest
        self.state = 'closed' if decoration_type == 'treasure' else None
        
        # Get colors for this decoration category
        self.colors = DECORATION_CATEGORIES.get(self.category, [Fore.WHITE])
        self.base_color = random.choice(self.colors)
    
    def draw(self, buffer):
        """Draws the decoration onto the provided scene buffer."""
        x, y = self.x, self.y
        color = self.get_current_color()
        for line_idx, line_art in enumerate(self.art):
            current_y = y + line_idx
            if 0 <= current_y < self.aquarium_height:
                trimmed_line = line_art.strip()
                if not trimmed_line:
                    continue
                
                art_start_index = line_art.find(trimmed_line)
                art_end_index = art_start_index + len(trimmed_line)

                for char_idx, char_art in enumerate(line_art):
                    if art_start_index <= char_idx < art_end_index:
                        current_x = x + char_idx
                        if 0 <= current_x < self.width:
                            if char_art != ' ':
                                buffer[current_y][current_x] = (char_art, color)
                            else:
                                buffer[current_y][current_x] = (' ', Fore.RESET)

    def get_adjusted_color(self, color):
        """Adjusts color based on current background mode."""
        from colorama import Back
        if self.background_color == Back.LIGHTCYAN_EX:  # Light mode
            return COLOR_ADJUSTMENTS.get('light_mode', {}).get(color, color)
        return color

    def get_current_color(self):
        """Gets a random color from the decoration's color set, adjusted for background mode."""
        base_color = random.choice(self.colors)
        return self.get_adjusted_color(self.base_color)

    def open_chest(self):
        """Opens a treasure chest (changes state and art)."""
        if self.type == 'treasure' and self.state == 'closed':
            self.aquarium_manager.play_chest_sound()
            self.state = 'open'
            # Get the open chest art
            self.category, self.art = DECORATIONS['treasure']['open'][0]
            if isinstance(self.art, str):
                self.art = (self.art,)
            self.art_height = len(self.art)
            self.art_width = max(len(line) for line in self.art)
            # Reposition if needed
            self.y = self.aquarium_height - 1 - self.art_height

    def is_near_point(self, x, y, radius=10):
        """Checks if a point is within radius of this decoration."""
        center_x = self.x + self.art_width / 2
        center_y = self.y + self.art_height / 2
        distance = math.sqrt((center_x - x)**2 + (center_y - y)**2)
        return distance <= radius


def generate_decorations(width, height, background_color, aquarium_manager):
    """Generates random decorations for the seafloor without overlapping."""
    decorations = []
    
    # Check if we should spawn decorations
    if random.random() > DECORATION_SPAWN_CHANCE:
        return decorations
        
    num_decorations = random.randint(1, MAX_DECORATIONS)
    
    # Get all available decoration types
    all_decoration_options = []
    for decoration_type, states in DECORATIONS.items():
        if decoration_type == 'treasure':
            # For treasure, use closed state by default
            all_decoration_options.append((decoration_type, states['closed'][0]))
        else:
            # For other decorations, add all variants
            for decoration_data in states:
                all_decoration_options.append((decoration_type, decoration_data))
    
    # Try to place decorations without overlapping
    placed_decorations = []
    attempts = 0
    max_attempts = 50
    
    while len(placed_decorations) < num_decorations and attempts < max_attempts:
        attempts += 1
        
        # Choose a random decoration
        decoration_type, decoration_data = random.choice(all_decoration_options)
        
        # Get art dimensions
        _, art = decoration_data
        if isinstance(art, str):
            art = (art,)
        art_width = max(len(line) for line in art)
        
        # Try to find a position
        x_pos = random.randint(0, width - art_width - 1)
        
        # Check for overlap with existing decorations
        overlaps = False
        for existing_decoration in placed_decorations:
            # Simple overlap check - if decorations are too close horizontally
            if abs(x_pos - existing_decoration.x) < (art_width + existing_decoration.art_width + 5):
                overlaps = True
                break
        
        if not overlaps:
            decoration = Decoration(decoration_type, decoration_data, x_pos, width, height, background_color, aquarium_manager)
            placed_decorations.append(decoration)
    
    return placed_decorations