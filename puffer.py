import random
import math
from fish import Fish
from ascii_art import FISH_ART_STYLES, FISH_COLOR_SETS
from config import (
    FRAME_RATE, PUFFER_NORMAL_SPEED_RANGE, PUFFER_STATE_DURATION,
    PUFFER_PUFF_ANIMATION_SPEED, PUFFER_SWIM_ANIMATION_SPEED
)

class PufferFish(Fish):
    """
    Represents a PufferFish that inherits from Fish but has unique behavior.
    It swims slowly and puffs up into an animated state when startled.
    """
    def __init__(self, width, height, background_color, aquarium_manager):
        #parent
        super().__init__(width, height, background_color)
        self.aquarium_manager = aquarium_manager

        # --- Override specific PufferFish attributes ---
        self.fish_type = 'puffer'
        self.base_color = random.choice(FISH_COLOR_SETS[self.fish_type])

        # Store all animation frames from ascii_art.py
        self.puff_frames = [art for _, art in FISH_ART_STYLES['puffer'][self.direction]]
        self.swim_frames = [art for _, art in FISH_ART_STYLES['puffer'][f"{self.direction}_swim"]]

        # Set the initial art to the smallest frame
        self.art = self.puff_frames[0]

        # Slower speed than normal fish
        self.normal_speed = random.uniform(*PUFFER_NORMAL_SPEED_RANGE)
        self.speed = self.normal_speed if self.direction == 'forward' else -self.normal_speed

        # State management for puffing behavior
        self.state = 'normal'
        self.animation_frame_index = 0
        self.animation_timer = 0.0
        self.puffed_duration_timer = 0.0

        # Sine wave movement attributes
        self.wave_amplitude = random.uniform(4.0, 6.0)
        self.wave_frequency = random.uniform(0.01, 0.04)
        
        # --- MODIFIED: Override Y position to prevent floor clipping ---
        # This is a tweakable range to ensure the sine wave motion is safe.
        safe_top_margin = int(self.wave_amplitude) + 1
        safe_bottom_margin = int(self.wave_amplitude) + self.art_height + 14 # +2 for floor & buffer

        # Define the valid spawn range for the center of the wave
        min_y = safe_top_margin
        max_y = height - safe_bottom_margin

        # Failsafe for very small terminal windows where the range might be invalid
        if min_y >= max_y:
            min_y, max_y = height // 2, height // 2
        
        # Set the new, safe Y position
        self.y = random.randint(min_y, max_y)
        self.center_y = self.y  # The central line for the wave is now this safe Y
        # --- END MODIFICATION ---

    def update(self):
        """
        Overrides the base Fish update method to handle state-based animation.
        """
        # --- State Machine Logic ---
        if self.state == 'puffing':
            self.animation_timer += FRAME_RATE
            if self.animation_timer >= PUFFER_PUFF_ANIMATION_SPEED:
                self.animation_timer = 0
                if self.animation_frame_index < len(self.puff_frames) - 1:
                    self.animation_frame_index += 1
                else:
                    self.state = 'puffed'
                    self.puffed_duration_timer = PUFFER_STATE_DURATION
                    self.animation_frame_index = 0

        elif self.state == 'puffed':
            self.puffed_duration_timer -= FRAME_RATE
            self.animation_timer += FRAME_RATE
            if self.animation_timer >= PUFFER_SWIM_ANIMATION_SPEED:
                self.animation_timer = 0
                self.animation_frame_index = (self.animation_frame_index + 1) % len(self.swim_frames)

            if self.puffed_duration_timer <= 0:
                self.state = 'deflating'
                self.animation_frame_index = len(self.puff_frames) - 1

        elif self.state == 'deflating':
            self.animation_timer += FRAME_RATE
            if self.animation_timer >= PUFFER_PUFF_ANIMATION_SPEED:
                self.animation_timer = 0
                if self.animation_frame_index > 0:
                    self.animation_frame_index -= 1
                else:
                    self.state = 'normal'

        # Update the current art based on the state and frame index
        if self.state == 'puffed':
            self.art = self.swim_frames[self.animation_frame_index]
        else:
            self.art = self.puff_frames[self.animation_frame_index]

        # --- Movement Logic ---
        if self.state in ['normal', 'puffed']:
            self.x += self.speed
            self.speed = self.normal_speed if self.direction == 'forward' else -self.normal_speed
            
            # Sine wave vertical movement
            offset = self.wave_amplitude * math.sin(self.x * self.wave_frequency)
            self.y = self.center_y + offset
        else:
            self.speed = 0

        # Update art dimensions for wrapping logic
        self.art_height = len(self.art)
        self.art_width = max(len(line) for line in self.art) if self.art else 0

        # Handle screen wrapping
        if self.speed > 0 and self.x >= self.width:
            self.x = -self.art_width
        elif self.speed < 0 and self.x <= -self.art_width:
            self.x = self.width - 1

    def startle(self):
        """
        Overrides the base Fish startle method to trigger the puffing animation.
        """
        if self.state == 'normal':
            self.aquarium_manager.play_puffer_sound()
            self.state = 'puffing'
            self.animation_frame_index = 0
            self.animation_timer = 0.0

