import random
import math
from fish import Fish
from ascii_art import FISH_ART_STYLES
from config import FRAME_RATE, SEAHORSE_NORMAL_SPEED_RANGE, SEAHORSE_ANIMATION_SPEED


class Seahorse(Fish):
    """
    Represents a Seahorse that inherits from Fish but has unique gentle movement
    and a 1-2-3-2-1 animation cycle.
    """

    def __init__(self, width, height, background_color):
        # Set unique properties BEFORE calling the parent __init__
        self.fish_type = 'seahorse'
        self.category = 'seahorse'  # The category in ascii_art.py
        
        # Call the parent initializer
        super().__init__(width, height, background_color)
        
        # Process animation frames for both directions
        raw_forward_frames = [art for _, art in FISH_ART_STYLES['seahorse']['forward']]
        raw_backward_frames = [art for _, art in FISH_ART_STYLES['seahorse']['backward']]
        
        self.forward_frames = [self._process_single_color_art(frame) for frame in raw_forward_frames]
        self.backward_frames = [self._process_single_color_art(frame) for frame in raw_backward_frames]
        
        # Override speed for gentle movement
        self.normal_speed = random.uniform(*SEAHORSE_NORMAL_SPEED_RANGE)
        self.speed = self.normal_speed if self.direction == 'forward' else -self.normal_speed
        
        # Animation state
        self.animation_timer = 0.0
        self.animation_sequence = [0, 1, 2, 1]  # 1st, 2nd, 3rd, 2nd (0-indexed)
        self.sequence_index = 0  # Current position in the sequence
        
        # Sine wave movement attributes for gentle floating
        self.wave_amplitude = random.uniform(1.5, 2.5)
        self.wave_frequency = random.uniform(0.05, 0.15)  # Very gentle waves
        
        # Set a safe Y position to prevent floor clipping
        self.art_height = len(self.art)
        safe_top_margin = int(self.wave_amplitude) + 1
        safe_bottom_margin = int(self.wave_amplitude) + self.art_height + 5
        min_y = safe_top_margin
        max_y = height - safe_bottom_margin
        if min_y >= max_y:
            min_y, max_y = height // 3, height // 2
        self.y = random.randint(min_y, max_y)
        self.center_y = self.y
        
        # Set initial art frame
        self._update_art_frame()

    def _update_art_frame(self):
        """Updates the current art frame based on direction and animation sequence."""
        current_frames = self.forward_frames if self.direction == 'forward' else self.backward_frames
        frame_index = self.animation_sequence[self.sequence_index]
        
        # Safety check
        if frame_index < len(current_frames):
            self.art = current_frames[frame_index]
        else:
            self.art = current_frames[0]  # Fallback to first frame
            
        # Update art dimensions
        self.art_height = len(self.art)
        self.art_width = max(len(line) for line in self.art) if self.art and self.art[0] else 1

    def turn_around(self):
        """Overrides parent turn_around to handle seahorse-specific animation frames."""
        if self.direction == 'forward':
            self.direction = 'backward'
            self.speed = -abs(self.speed)
        else:
            self.direction = 'forward'
            self.speed = abs(self.speed)
        
        # Update art for new direction
        self._update_art_frame()

    def update(self):
        """
        Overrides the base Fish update method to handle gentle movement and animation.
        """
        # Handle startled state using parent logic
        if self.is_startled:
            self._update_startled()
            return
            
        # Handle seeking state using parent logic
        if self.state == 'seeking':
            self._update_seeking()
        else:
            # Normal gentle movement
            self.speed = self.normal_speed if self.direction == 'forward' else -self.normal_speed
            self.x += self.speed
            
        # Gentle sine wave vertical movement
        wave_offset = self.wave_amplitude * math.sin(self.x * self.wave_frequency)
        self.y = self.center_y + wave_offset
        
        # Handle screen wrapping
        if self.speed > 0 and self.x >= self.width:
            self.x = -self.art_width
        elif self.speed < 0 and self.x <= -self.art_width:
            self.x = self.width - 1
            
        # Update animation
        self.animation_timer += FRAME_RATE
        if self.animation_timer >= SEAHORSE_ANIMATION_SPEED:
            self.animation_timer = 0.0
            
            # Move to next frame in sequence
            self.sequence_index = (self.sequence_index + 1) % len(self.animation_sequence)
            self._update_art_frame()

    def startle(self):
        """
        Overrides the base Fish startle method. Seahorses don't change behavior much when startled,
        just speed up slightly while maintaining their gentle nature.
        """
        if not self.is_startled:
            self.is_startled = True
            self.startle_timer = 1.0  # Shorter startle duration
            # Only a modest speed increase for seahorses
            startle_multiplier = random.uniform(2.0, 3.0)  
            self.peak_startle_speed = abs(self.normal_speed * startle_multiplier)
            self.speed = self.peak_startle_speed if self.direction == 'forward' else -self.peak_startle_speed
            
        # Reset seeking state if startled
        self.state = 'swimming'
        self.target_food = None