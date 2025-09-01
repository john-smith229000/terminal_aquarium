import random
from colorama import Fore
from ascii_art import CRAB
from config import (
    CRAB_IDLE_DURATION_RANGE, CRAB_WALK_DURATION_RANGE,
    CRAB_WALK_SPEED_RANGE, CRAB_ANIMATION_SPEED
)


class Crab:
    """Represents a crab that walks along the seafloor."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Crab art and animation
        self.animation_frames = CRAB
        self.current_frame = 0
        self.art_height = len(self.animation_frames[0])
        self.art_width = max(len(line) for line in self.animation_frames[0])
        
        # Position on seafloor
        self.x = float(random.randint(0, width - self.art_width))
        self.y = height - 1 - self.art_height  # On seafloor
        
        # Movement state
        self.state = 'idle'  # 'idle' or 'walking'
        self.speed = 0
        self.walk_direction = 1  # 1 for right, -1 for left
        self.idle_timer = 0
        self.walk_timer = 0
        self.animation_timer = 0
        
        # Timing parameters
        self.idle_duration = random.uniform(*CRAB_IDLE_DURATION_RANGE)
        self.walk_duration = random.uniform(*CRAB_WALK_DURATION_RANGE)
        self.walk_speed = random.uniform(*CRAB_WALK_SPEED_RANGE)

    def update(self):
        """Updates crab state and position."""
        if self.state == 'idle':
            # Reset to first frame when idle
            self.current_frame = 0
            self.idle_timer += 0.1  # Increment by frame rate
            
            if self.idle_timer >= self.idle_duration:
                # Start walking
                self.state = 'walking'
                self.idle_timer = 0
                self.walk_timer = 0
                self.walk_direction = random.choice([-1, 1])  # Random direction
                self.walk_duration = random.uniform(*CRAB_WALK_DURATION_RANGE)
                self.speed = self.walk_speed * self.walk_direction
                
        elif self.state == 'walking':
            # Animate walking (rapidly switch between frames)
            self.animation_timer += 0.1
            if self.animation_timer >= CRAB_ANIMATION_SPEED:
                self.current_frame = 1 - self.current_frame  # Toggle between 0 and 1
                self.animation_timer = 0
            
            # Move crab
            self.x += self.speed
            self.walk_timer += 0.1
            
            # Check if walk duration is over or hit boundary
            if (self.walk_timer >= self.walk_duration or 
                self.x <= 0 or 
                self.x >= self.width - self.art_width):
                
                # Stop walking and go idle
                self.state = 'idle'
                self.speed = 0
                self.walk_timer = 0
                self.idle_duration = random.uniform(*CRAB_IDLE_DURATION_RANGE)
                self.current_frame = 0  # Reset to idle frame
                
                # Keep crab in bounds
                self.x = max(0, min(self.x, self.width - self.art_width))

    def get_current_art(self):
        """Returns the current frame's art."""
        return self.animation_frames[self.current_frame]
    
    def draw(self, buffer):
        """Draws the crab onto the provided buffer."""
        x, y = int(self.x), int(self.y)
        art_grid = self.get_current_art()
        for line_idx, line_art in enumerate(art_grid):
            current_y = y + line_idx
            if 0 <= current_y < self.height:
                for char_idx, char_art in enumerate(line_art):
                    current_x = x + char_idx
                    if char_art != ' ' and 0 <= current_x < self.width:
                        buffer[current_y][current_x] = (char_art, Fore.RED)