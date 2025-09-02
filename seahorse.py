import random
import math
from fish import Fish
from ascii_art import FISH_ART_STYLES
from config import (
    FRAME_RATE, SEAHORSE_NORMAL_SPEED_RANGE, SEAHORSE_ANIMATION_SPEED, 
    SEAHORSE_SPAWN_CHANCE, BABY_SEAHORSE_SPAWN_CHANCE, BABY_SEAHORSE_COUNT_RANGE,
    BABY_SEAHORSE_FOLLOW_DISTANCE, BABY_SEAHORSE_WAVE_AMPLITUDE_RANGE, 
    BABY_SEAHORSE_SPEED_RANGE
)

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

    def spawn_babies(self):
        """
        Creates baby seahorses that will follow this adult seahorse.
        Returns a list of BabySeahorse objects.
        """
        babies = []
        
        # Check if babies should spawn based on chance
        if random.random() < BABY_SEAHORSE_SPAWN_CHANCE:
            num_babies = random.randint(*BABY_SEAHORSE_COUNT_RANGE)
            
            for i in range(num_babies):
                baby = BabySeahorse(self.width, self.height, self.background_color, self)
                babies.append(baby)
                
        return babies

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

class BabySeahorse(Fish):
    """
    Represents a baby seahorse that follows its parent around with smaller movements.
    """
    
    def __init__(self, width, height, background_color, parent_seahorse):
        # Set unique properties BEFORE calling the parent __init__
        self.fish_type = 'seahorse'
        self.category = 'seahorse'
        
        # Call the parent initializer
        super().__init__(width, height, background_color)
        
        # Store reference to parent
        self.parent = parent_seahorse
        
        # Process baby-specific animation frames
        raw_forward_frames = [art for _, art in FISH_ART_STYLES['seahorse']['baby_forward']]
        raw_backward_frames = [art for _, art in FISH_ART_STYLES['seahorse']['baby_backward']]
        
        self.forward_frames = [self._process_single_color_art(frame) for frame in raw_forward_frames]
        self.backward_frames = [self._process_single_color_art(frame) for frame in raw_backward_frames]
        
        # Baby-specific properties
        self.normal_speed = random.uniform(*BABY_SEAHORSE_SPEED_RANGE)
        self.speed = self.normal_speed if self.direction == 'forward' else -self.normal_speed
        
        # Animation state (faster animation for cute effect)
        self.animation_timer = 0.0
        self.animation_sequence = [0, 1, 0]  # Simpler animation for babies
        self.sequence_index = 0
        
        # Smaller wave motion
        self.wave_amplitude = random.uniform(*BABY_SEAHORSE_WAVE_AMPLITUDE_RANGE)
        self.wave_frequency = random.uniform(0.08, 0.2)  # Slightly more energetic than adult
        
        # Position near parent
        self.offset_x = random.uniform(-BABY_SEAHORSE_FOLLOW_DISTANCE, BABY_SEAHORSE_FOLLOW_DISTANCE)
        self.offset_y = random.uniform(-BABY_SEAHORSE_FOLLOW_DISTANCE/2, BABY_SEAHORSE_FOLLOW_DISTANCE/2)
        
        # Set initial position relative to parent
        self.x = parent_seahorse.x + self.offset_x
        self.y = parent_seahorse.y + self.offset_y
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
        """Overrides parent turn_around to handle baby seahorse animation frames."""
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
        Baby seahorses follow their parent while maintaining their own gentle movement.
        """
        # Handle startled state using parent logic
        if self.is_startled:
            self._update_startled()
            return
            
        # Babies don't seek food - they follow parent instead
        if self.state == 'seeking':
            self.state = 'swimming'
            self.target_food = None
            
        # Follow parent behavior
        if self.parent:
            # Calculate desired position near parent
            target_x = self.parent.x + self.offset_x
            target_y = self.parent.center_y + self.offset_y
            
            # Gently move toward target position
            x_diff = target_x - self.x
            y_diff = target_y - self.center_y
            
            # Follow parent's direction generally but with some independence
            if abs(x_diff) > BABY_SEAHORSE_FOLLOW_DISTANCE * 1.5:
                if x_diff > 0 and self.direction == 'backward':
                    self.turn_around()
                elif x_diff < 0 and self.direction == 'forward':
                    self.turn_around()
            
            # Gentle movement toward parent
            self.x += self.speed * 0.8  # Slightly slower than normal speed
            self.center_y += y_diff * 0.1  # Gentle vertical following
            
        else:
            # If parent is gone, behave like a normal seahorse
            self.speed = self.normal_speed if self.direction == 'forward' else -self.normal_speed
            self.x += self.speed
            
        # Apply sine wave motion (smaller amplitude than adult)
        wave_offset = self.wave_amplitude * math.sin(self.x * self.wave_frequency)
        self.y = self.center_y + wave_offset
        
        # Handle screen wrapping
        if self.speed > 0 and self.x >= self.width:
            self.x = -self.art_width
        elif self.speed < 0 and self.x <= -self.art_width:
            self.x = self.width - 1
            
        # Update animation (faster than adult for cute effect)
        self.animation_timer += FRAME_RATE
        if self.animation_timer >= SEAHORSE_ANIMATION_SPEED * 0.7:  # 30% faster animation
            self.animation_timer = 0.0
            
            # Move to next frame in sequence
            self.sequence_index = (self.sequence_index + 1) % len(self.animation_sequence)
            self._update_art_frame()

    def startle(self):
        """
        Baby seahorses get more startled than adults and move erratically.
        """
        if not self.is_startled:
            self.is_startled = True
            self.startle_timer = 0.8  # Shorter startle duration than adults
            # Babies get more startled
            startle_multiplier = random.uniform(3.0, 4.0)  
            self.peak_startle_speed = abs(self.normal_speed * startle_multiplier)
            self.speed = self.peak_startle_speed if self.direction == 'forward' else -self.peak_startle_speed
            
        # Reset seeking state if startled
        self.state = 'swimming'
        self.target_food = None