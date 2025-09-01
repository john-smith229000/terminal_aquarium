import random
import math
from colorama import Fore, Back
from ascii_art import FISH_ART_STYLES, FISH_COLOR_SETS, COLOR_ADJUSTMENTS
from config import (
    NORMAL_SPEED_RANGE, FAST_SPEED_RANGE, FAST_FISH_PROBABILITY,
    STARTLE_MULTIPLIER_RANGE, STARTLE_DURATION, FRAME_RATE,
    FOOD_SEEK_SPEED_MULTIPLIER
)


class Fish:
    """Represents a single fish in the aquarium with AI for feeding."""
    def __init__(self, width, height, background_color):
        self.width = width
        self.height = height
        self.background_color = background_color
        self.direction = random.choice(['forward', 'backward'])

        self._init_art_and_color()
        self._init_position_and_speed()
        
        self.state = 'swimming' # swimming, seeking
        self.target_food = None
        
        self.is_startled = False
        self.startle_timer = 0.0
        self.peak_startle_speed = 0.0

    def _init_art_and_color(self):
        """Initializes the fish's appearance, storing both forward and backward art."""
        spawn_chance = random.random()
        if spawn_chance < 0.02: category = 'multi_line_large'
        elif spawn_chance < 0.30: category = 'multi_line_small'
        else: category = 'single_line'

        forward_arts = FISH_ART_STYLES[category]['forward']
        backward_arts = FISH_ART_STYLES[category]['backward']
        
        idx = random.randint(0, len(forward_arts) - 1)
        self.fish_type, self.forward_art = forward_arts[idx]
        _, self.backward_art = backward_arts[idx]

        if isinstance(self.forward_art, str): self.forward_art = (self.forward_art,)
        if isinstance(self.backward_art, str): self.backward_art = (self.backward_art,)

        self.art = self.forward_art if self.direction == 'forward' else self.backward_art
        self.base_color = random.choice(FISH_COLOR_SETS[self.fish_type])

    def _init_position_and_speed(self):
        """Sets the initial position and speed of the fish."""
        self.art_height = len(self.art)
        self.art_width = max(len(line) for line in self.art) if self.art else 0
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
        
        self.art_width = max(len(line) for line in self.art) if self.art else 0

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
        """Adjusts color based on current background mode."""
        if self.background_color == Back.LIGHTCYAN_EX:
            return COLOR_ADJUSTMENTS.get('light_mode', {}).get(color, color)
        return color

    def get_current_color(self):
        """Gets the current color adjusted for background mode."""
        return self.get_adjusted_color(self.base_color)

    def get_art_with_colors(self):
        """Returns the art with color information for drawing."""
        single_color = self.get_current_color()
        colored_art = []
        for line in self.art:
            colored_line = [(char, single_color) for char in line]
            colored_art.append(colored_line)
        return colored_art
        
    def draw(self, buffer):
        """Draws the fish onto the provided scene buffer."""
        x, y = int(self.x), int(self.y)
        colored_art = self.get_art_with_colors()
        
        for line_idx, line_data in enumerate(colored_art):
            current_y = y + line_idx
            if 0 <= current_y < self.height:
                for char_idx, (char_art, color) in enumerate(line_data):
                    current_x = x + char_idx
                    if char_art != ' ' and 0 <= current_x < self.width:
                        buffer[current_y][current_x] = (char_art, color)

