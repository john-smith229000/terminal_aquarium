import random
import math
from colorama import Fore
from ascii_art import FISH_ART_STYLES, FISH_COLOR_SETS, COLOR_ADJUSTMENTS
from config import (
    SCHOOL_SIZE_RANGE, FORMATION_WIDTH_RANGE, FORMATION_HEIGHT_RANGE,
    SCHOOL_SPEED_RANGE, SCHOOL_STARTLE_MULTIPLIER_RANGE, SCHOOL_STARTLE_DURATION,
    FRAME_RATE
)


class School:
    """Represents a school of fish that move together in formation."""
    def __init__(self, width, height, background_color):
        self.width = width
        self.height = height
        self.background_color = background_color
        self.direction = random.choice(['forward', 'backward'])
        
        # Choose a single fish type and color for the entire school
        fish_type, self.art = random.choice(FISH_ART_STYLES['single_line'][self.direction])
        self.base_color = random.choice(FISH_COLOR_SETS[fish_type])
        
        # School properties - larger and more spread out
        self.school_size = random.randint(*SCHOOL_SIZE_RANGE)
        self.formation_width = random.randint(*FORMATION_WIDTH_RANGE)
        self.formation_height = random.randint(*FORMATION_HEIGHT_RANGE)
        
        # School movement
        self.x = float(random.randint(0, width - 1))
        self.y = random.randint(1, height - self.formation_height - 2)
        
        # School speed
        self.normal_speed = random.uniform(*SCHOOL_SPEED_RANGE)
        if self.direction == 'forward':
            self.speed = self.normal_speed
        else:
            self.speed = -self.normal_speed
            
        self.is_startled = False
        self.startle_timer = 0.0
        self.peak_startle_speed = 0.0
            
        # Generate organic fish positions within the school formation
        self.fish_positions = []
        
        # Create more organic, oval-like distribution
        center_x = self.formation_width / 2
        center_y = self.formation_height / 2
        
        for _ in range(self.school_size):
            # Generate positions in an oval/elliptical pattern with randomness
            angle = random.uniform(0, 2 * math.pi)
            # Elliptical distribution (wider than tall)
            radius_x = random.uniform(0.3, 1.0) * (self.formation_width / 2.5)
            radius_y = random.uniform(0.3, 1.0) * (self.formation_height / 2.5)
            
            offset_x = center_x + radius_x * math.cos(angle) + random.uniform(-0.8, 0.8)
            offset_y = center_y + radius_y * math.sin(angle) + random.uniform(-0.5, 0.5)
            
            # Ensure positions stay within bounds
            offset_x = max(0, min(self.formation_width - 1, offset_x))
            offset_y = max(0, min(self.formation_height - 1, offset_y))
            
            self.fish_positions.append((offset_x, offset_y))

    def get_adjusted_color(self, color):
        """Adjusts color based on current background mode."""
        from colorama import Back
        if self.background_color == Back.LIGHTCYAN_EX:  # Light mode
            return COLOR_ADJUSTMENTS.get('light_mode', {}).get(color, color)
        return color

    def get_current_color(self):
        """Gets the current color adjusted for background mode."""
        return self.get_adjusted_color(self.base_color)

    def update(self):
        """Moves the entire school as a unit."""
        if self.is_startled:
            self.startle_timer -= FRAME_RATE
            if self.startle_timer <= 0:
                self.is_startled = False
                # Revert to normal speed
                self.speed = self.normal_speed if self.direction == 'forward' else -self.normal_speed
            else:
                # Interpolate speed for smooth deceleration
                progress = self.startle_timer / SCHOOL_STARTLE_DURATION
                speed_range = self.peak_startle_speed - self.normal_speed
                current_speed_magnitude = self.normal_speed + (speed_range * progress)
                self.speed = current_speed_magnitude if self.direction == 'forward' else -current_speed_magnitude

        self.x += self.speed
        art_width = len(self.art)
        school_total_width = self.formation_width + art_width
        if self.speed > 0 and self.x >= self.width:
            self.x = -school_total_width
        elif self.speed < 0 and self.x <= -school_total_width:
            self.x = self.width - 1

    def startle(self):
        """Temporarily speeds up the entire school."""
        if not self.is_startled:
            self.is_startled = True
            self.startle_timer = SCHOOL_STARTLE_DURATION
            
            startle_multiplier = random.uniform(*SCHOOL_STARTLE_MULTIPLIER_RANGE)
            self.peak_startle_speed = self.normal_speed * startle_multiplier

    def get_fish_positions(self):
        """Returns the absolute positions of all fish in the school."""
        positions = []
        for offset_x, offset_y in self.fish_positions:
            abs_x = self.x + offset_x
            abs_y = self.y + offset_y
            positions.append((abs_x, abs_y))
        return positions
    
    def draw(self, buffer):
        """Draws all the fish in the school onto the provided buffer."""
        current_color = self.get_current_color()
        for fish_x, fish_y in self.get_fish_positions():
            x, y = int(fish_x), int(fish_y)
            # Bounds check against aquarium height
            if 0 <= y < self.height:
                for char_idx, char_art in enumerate(self.art):
                    current_x = x + char_idx
                    # Bounds check against aquarium width
                    if char_art != ' ' and 0 <= current_x < self.width:
                        buffer[y][current_x] = (char_art, current_color)