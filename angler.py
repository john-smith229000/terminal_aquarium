import random
import math
from fish import Fish
from ascii_art import FISH_ART_STYLES
from config import (
    FRAME_RATE, NORMAL_SPEED_RANGE, FAST_SPEED_RANGE, FAST_FISH_PROBABILITY
)
from colorama import Back

class AnglerFish(Fish):
    """
    Represents an AnglerFish that inherits from Fish but has unique deep-sea behavior.
    It illuminates a cone-shaped area in front of it with a lure.
    """

    def __init__(self, width, height, background_color):
        # Set unique properties BEFORE calling the parent __init__
        self.fish_type = 'angler'
        self.category = 'angler'
        
        # Call the parent initializer
        super().__init__(width, height, background_color)
        
        # Process animation frames
        raw_forward_frames = [art for _, art in FISH_ART_STYLES['angler']['forward']]
        raw_backward_frames = [art for _, art in FISH_ART_STYLES['angler']['backward']]
        
        self.forward_frames = [self._process_single_color_art(frame) for frame in raw_forward_frames]
        self.backward_frames = [self._process_single_color_art(frame) for frame in raw_backward_frames]
        
        # Anglerfish speed
        if random.random() < 0.7:
            self.normal_speed = random.uniform(0.1, 0.3)
        else:
            self.normal_speed = random.uniform(*NORMAL_SPEED_RANGE)
        self.speed = self.normal_speed if self.direction == 'forward' else -self.normal_speed
        
        # Anglerfish depth
        self.art_height = len(self.art)
        min_depth = height // 3
        max_depth = height - self.art_height - 5
        if min_depth >= max_depth:
            min_depth, max_depth = height // 2, height // 2
        self.y = random.randint(min_depth, max_depth)
        
        self._update_art_frame()
        
        # --- ASCII Art for the Light Cone ---
        # A list of strings made of spaces. The length of each string
        # determines the width of the cone at that row.
        self.light_cone_art = [
            "   .      ",
            "   ....      ",
            "   .......      ",
            "   ...........      ",
            "   .........      ",
            "   .....      ",
            "   .      ",
        ]
        # ------------------------------------

        self.light_active = True
        self.light_color = Back.YELLOW # A single, stable color for the light
        
    def _update_art_frame(self):
        """Updates the current art frame based on direction."""
        if self.direction == 'forward':
            self.art = self.forward_frames[0] if self.forward_frames else [[('?', self.base_color)]]
        else:
            self.art = self.backward_frames[0] if self.backward_frames else [[('?', self.base_color)]]
            
        self.art_height = len(self.art)
        self.art_width = max(len(line) for line in self.art) if self.art and self.art[0] else 1

    def turn_around(self):
        """Overrides parent turn_around."""
        if self.direction == 'forward':
            self.direction = 'backward'
            self.speed = -abs(self.speed)
        else:
            self.direction = 'forward'
            self.speed = abs(self.speed)
        self._update_art_frame()

    def startle(self):
        """Anglerfish have a muted startle response."""
        if not self.is_startled:
            self.is_startled = True
            self.startle_timer = 0.8
            startle_multiplier = random.uniform(2.0, 3.0)
            self.peak_startle_speed = abs(self.normal_speed * startle_multiplier)
            self.speed = self.peak_startle_speed if self.direction == 'forward' else -self.peak_startle_speed
        self.state = 'swimming'
        self.target_food = None

    def update(self):
        """Updates the anglerfish's position."""
        if self.is_startled:
            self._update_startled()
            return
            
        if self.state == 'seeking':
            self._update_seeking()
        else:
            self.speed = self.normal_speed if self.direction == 'forward' else -self.normal_speed
            self.x += self.speed
            
        # Handle screen wrapping
        if self.speed > 0 and self.x >= self.width:
            self.x = -self.art_width
        elif self.speed < 0 and self.x <= -self.art_width:
            self.x = self.width - 1

    def draw_body(self, buffer):
        """Draws the fish body with special handling for the lure."""
        x, y = int(self.x), int(self.y)
        processed_art = self.get_current_processed_art()
        
        for line_idx, line_data in enumerate(processed_art):
            current_y = y + line_idx
            if 0 <= current_y < self.height:
                for char_idx, (char_art, color) in enumerate(line_data):
                    current_x = x + char_idx
                    if char_art != ' ' and 0 <= current_x < self.width:
                        # The lure '*' is part of the body but won't be lit here.
                        # It gets its light from the draw_light_effect pass.
                        buffer[current_y][current_x] = (char_art, color + self.background_color)

    # --- CHANGE: New method to ONLY draw the light effect ---
    def draw_light_effect(self, buffer):
        """
        Draws the light cone and lure light as a final pass over the buffer,
        illuminating whatever is already there.
        """
        if not self.light_active:
            return

        # 1. Illuminate the external light cone
        cone_height = len(self.light_cone_art)
        lure_y_approx = int(self.y + 1) + 5
        start_y = lure_y_approx - (cone_height // 2)
        if self.direction == 'forward': base_x = int(self.x + self.art_width) -7
        else: base_x = int(self.x) + 10

        for i, line in enumerate(self.light_cone_art):
            draw_y = start_y + i
            if not (0 <= draw_y < self.height): continue
            for char_offset, cone_char in enumerate(line):
                if cone_char != ' ':
                    if self.direction == 'forward': draw_x = base_x + char_offset
                    else: draw_x = base_x - len(line) + char_offset
                    if 0 <= draw_x < self.width:
                        current_char, current_color = buffer[draw_y][draw_x]
                        buffer[draw_y][draw_x] = (current_char, current_color + self.light_color)

        # 2. Illuminate the lure '*' on the fish's body
        x, y = int(self.x), int(self.y)
        for line_idx, line_data in enumerate(self.art):
            current_y = y + line_idx
            if 0 <= current_y < self.height:
                for char_idx, (char_art, _) in enumerate(line_data):
                    current_x = x + char_idx
                    if char_art == '*' and 0 <= current_x < self.width:
                        # Read what's there and add the light to it
                        existing_char, existing_color = buffer[current_y][current_x]
                        buffer[current_y][current_x] = (existing_char, existing_color + self.light_color)


        # 2. Finally, draw the fish itself over the light
        super().draw(buffer)