import random
import math
from colorama import Fore, Back, Style
from ascii_art import FISH_ART_STYLES, FISH_COLOR_SETS, COLOR_ADJUSTMENTS
from config import (
    NORMAL_SPEED_RANGE, FAST_SPEED_RANGE, FAST_FISH_PROBABILITY,
    STARTLE_MULTIPLIER_RANGE, STARTLE_DURATION, FRAME_RATE,
    FOOD_SEEK_SPEED_MULTIPLIER, MED_FISH_CHANCE, LARGE_FISH_CHANCE
)


class Fish:
    """Represents a single fish in the aquarium with AI for feeding."""
    def __init__(self, width, height, background_color):
        self.width = width
        self.height = height
        self.background_color = background_color
        self.direction = random.choice(['forward', 'backward'])

        # If a child class (like PufferFish) hasn't already set these, set them now.
        if not hasattr(self, 'category') or not hasattr(self, 'fish_type'):
            self.category, self.fish_type = self._get_random_fish_details()

        self._init_art_and_color()
        self._init_position_and_speed()
        
        self.state = 'swimming'
        self.target_food = None
        
        self.is_startled = False
        self.startle_timer = 0.0
        self.peak_startle_speed = 0.0

    def _get_random_fish_details(self):
        """Selects a random category and fish type from that category."""
        spawn_chance = random.random()
        if spawn_chance < LARGE_FISH_CHANCE: category = 'multi_line_large'
        elif spawn_chance <     MED_FISH_CHANCE: category = 'multi_line_small'
        else: category = 'single_line'
        
        arts_list = FISH_ART_STYLES[category]['forward']
        fish_type, _ = random.choice(arts_list)
        return category, fish_type

    def _init_art_and_color(self):
        """
        Initializes art and color using the stored category for a direct lookup.
        """
        try:
            forward_arts = FISH_ART_STYLES[self.category]['forward']
            backward_arts = FISH_ART_STYLES[self.category]['backward']
            
            forward_template = next((art for type, art in forward_arts if type == self.fish_type), None)
            backward_template = next((art for type, art in backward_arts if type == self.fish_type), None)
            
            if not forward_template: raise ValueError(f"No forward art found for {self.fish_type} in category {self.category}")
            if not backward_template: backward_template = forward_template

            color_data = FISH_COLOR_SETS.get(self.fish_type)
            is_multicolor = isinstance(color_data, dict)

            self.color_map = {}
            self.base_color = None
            if is_multicolor:
                for key, colors in color_data.items():
                    self.color_map[key] = random.choice(colors)
            else:
                self.base_color = random.choice(color_data if color_data else [Fore.WHITE])

            self.forward_art = self._process_art_template(forward_template)
            self.backward_art = self._process_art_template(backward_template)
            
            self.art = self.forward_art if self.direction == 'forward' else self.backward_art

        except Exception as e:
            print(f"{Fore.RED}Critical Error initializing fish '{getattr(self, 'fish_type', 'unknown')}': {e}{Style.RESET_ALL}")
            self.art = [[('X', Fore.RED)]]

    def _process_art_template(self, template):
        """Determines the art format and processes it into a final drawable grid."""
        if isinstance(template, dict):
            return self._process_multicolor_art(template['art'])
        else:
            art_tuple = (template,) if isinstance(template, str) else template
            return self._process_single_color_art(art_tuple)

    def _process_multicolor_art(self, art_template):
        """Converts a run-length encoded art template into a drawable grid."""
        processed_grid = []
        for line_template in art_template:
            line = []
            for color_key, chars in line_template:
                color = self.color_map.get(color_key, Fore.WHITE)
                for char in chars:
                    line.append((char, color))
            processed_grid.append(line)
        return processed_grid

    def _process_single_color_art(self, art_tuple):
        """Converts a simple tuple of strings into a drawable grid."""
        processed_grid = []
        for line_str in art_tuple:
            line = []
            for char in line_str:
                line.append((char, self.base_color))
            processed_grid.append(line)
        return processed_grid

    def _init_position_and_speed(self):
        if not hasattr(self, 'art') or not self.art:
             self.art = [[('?', Fore.RED)]]

        self.art_height = len(self.art)
        self.art_width = max(len(line) for line in self.art) if self.art and self.art[0] else 1
        self.x = float(random.randint(0, self.width - 1))
        self.y = random.randint(1, self.height - self.art_height - 3)

        if random.random() < (1.0 - FAST_FISH_PROBABILITY):
            self.normal_speed = random.uniform(*NORMAL_SPEED_RANGE)
        else:
            self.normal_speed = random.uniform(*FAST_SPEED_RANGE)
        self.speed = self.normal_speed if self.direction == 'forward' else -self.normal_speed

    def turn_around(self):
        """Flips the fish's direction and updates its art and speed."""
        if self.direction == 'forward':
            self.direction = 'backward'
            self.art = self.backward_art
            self.speed = -abs(self.speed)
        else:
            self.direction = 'forward'
            self.art = self.forward_art
            self.speed = abs(self.speed)
        self.art_width = max(len(line) for line in self.art) if self.art and self.art[0] else 1

    def seek_food(self, food_pellet):
        """Assigns a food pellet and triggers the seeking state with a speed boost."""
        if self.state == 'swimming':
            self.state = 'seeking'
            self.target_food = food_pellet
            self.speed *= FOOD_SEEK_SPEED_MULTIPLIER

    def update(self):
        """The main AI brain for the fish."""
        if self.is_startled:
            self._update_startled()
            return

        if self.state == 'seeking':
            self._update_seeking()
        else:
            self._update_swimming()

    def _update_swimming(self):
        """Default behavior: swim back and forth at normal speed."""
        self.speed = self.normal_speed if self.direction == 'forward' else -self.normal_speed
        self.x += self.speed
        if self.speed > 0 and self.x >= self.width: self.x = -self.art_width
        elif self.speed < 0 and self.x <= -self.art_width: self.x = self.width - 1
    
    def _update_seeking(self):
        """Behavior for rushing towards food, with anti-oscillation logic."""
        if not self.target_food or not self.target_food.lifetime > 0:
            self.state = 'swimming'
            self.target_food = None
            return

        dist_x = self.target_food.x - self.x
        
        # Determine which way the fish should be facing
        is_food_to_right = dist_x > 0
        is_facing_right = self.speed > 0

        # If the fish is facing the wrong direction, turn around.
        if (is_food_to_right and not is_facing_right) or \
           (not is_food_to_right and is_facing_right):
            self.turn_around()
        
        # Calculate the movement for this frame.
        movement = self.speed

        # --- THE CORE FIX ---
        # If the planned movement would overshoot the target, just move exactly
        # onto the target and stop seeking. This prevents flickering.
        if abs(movement) >= abs(dist_x):
            self.x = self.target_food.x
            self.state = 'swimming' # Revert to normal swimming behavior
        else:
            # Otherwise, move normally.
            self.x += movement


    def _update_startled(self):
        """Handles the startled state countdown and deceleration."""
        self.startle_timer -= FRAME_RATE
        if self.startle_timer <= 0:
            self.is_startled = False
            self.speed = self.normal_speed if self.direction == 'forward' else -self.normal_speed
        else:
            progress = self.startle_timer / STARTLE_DURATION
            speed_range = self.peak_startle_speed - self.normal_speed
            current_speed_magnitude = self.normal_speed + (speed_range * progress)
            self.speed = current_speed_magnitude if self.direction == 'forward' else -current_speed_magnitude
        
        self.x += self.speed

    def startle(self):
        """Temporarily multiplies the fish's speed, interrupting feeding."""
        self.state = 'swimming'
        self.target_food = None

        if not self.is_startled:
            self.is_startled = True
            self.startle_timer = STARTLE_DURATION
            startle_multiplier = random.uniform(*STARTLE_MULTIPLIER_RANGE)
            self.peak_startle_speed = abs(self.normal_speed * startle_multiplier)
            self.speed = self.peak_startle_speed if self.direction == 'forward' else -self.peak_startle_speed

    def get_adjusted_color(self, color):
        """Adjusts a single color based on the current background mode."""
        if self.background_color == Back.LIGHTCYAN_EX:
            return COLOR_ADJUSTMENTS.get('light_mode', {}).get(color, color)
        return color

    def get_current_processed_art(self):
        """Returns the pre-processed art with colors adjusted for the current background."""
        adjusted_art = []
        for line in self.art:
            adjusted_line = []
            if line:
                for item in line:
                    # Defensive check to prevent crashes on malformed data
                    if isinstance(item, tuple) and len(item) == 2:
                        char, color = item
                        adjusted_line.append((char, self.get_adjusted_color(color)))
            adjusted_art.append(adjusted_line)
        return adjusted_art

    def draw(self, buffer):
        """Draws the pre-processed fish art onto the scene buffer."""
        x, y = int(self.x), int(self.y)
        processed_art_for_drawing = self.get_current_processed_art()
        
        for line_idx, line_data in enumerate(processed_art_for_drawing):
            current_y = y + line_idx
            if 0 <= current_y < self.height:
                for char_idx, item in enumerate(line_data):
                    # --- NEW: Final failsafe to prevent crashes ---
                    if isinstance(item, tuple) and len(item) == 2:
                        char_art, color = item
                        current_x = x + char_idx
                        if char_art != ' ' and 0 <= current_x < self.width:
                            buffer[current_y][current_x] = (char_art, color)
          

