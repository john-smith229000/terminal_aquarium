# Updated shark.py

import random
import math
import re
from colorama import Fore, Back, Style
from fish import Fish
from config import FRAME_RATE, STARTLE_RADIUS, SHARK_CHANCE

# TWEAK: Define a list of possible colors for the shark
SHARK_COLORS = [
    Fore.LIGHTBLACK_EX,
    Fore.LIGHTWHITE_EX,
    Fore.WHITE,
    Fore.LIGHTCYAN_EX,
    Fore.CYAN,
    Fore.LIGHTWHITE_EX,
    Fore.LIGHTBLUE_EX
]

class Shark(Fish):
    """A special event shark that swims across the top of the screen with animation."""
    
    def __init__(self, width, height, background_color, aquarium_ref):
        self.width = width
        self.height = height
        self.background_color = background_color
        self.aquarium_ref = aquarium_ref
        
        # Set shark-specific properties before calling parent init
        self.category = 'shark'
        self.fish_type = 'shark'
        
        # TWEAK: Assign a random color to this shark instance
        self.shark_color = random.choice(SHARK_COLORS)
        
        # Load shark animation frames
        self.shark_frames = self._load_shark_frames()
        self.current_frame = 0
        self.frame_counter = 0
        self.frames_per_animation = 2  # Change frame every 3 update cycles
        
        # Shark positioning and movement
        self.direction = 'backward'
        # BUGFIX: Start the shark completely off-screen to the right
        self.x = float(self.width + 5)
        self.y = random.randint(2, min(8, height // 4))  # Near top of screen
        self.speed = random.uniform(0.5, 1) # A bit faster
        self.normal_speed = self.speed
        
        # Shark doesn't use the normal fish art system
        self.art = self._get_current_frame_art()
        self.art_height = len(self.art)
        self.art_width = max(len(line) for line in self.art) if self.art else 1
        
        # Shark state
        self.state = 'swimming'
        self.target_food = None
        self.is_startled = False
        self.startle_timer = 0.0
        self.active = True
        
        # Startle effect properties
        self.startle_radius = 28
        self.last_startle_x = self.x # Initialize last startle position
        
    def _load_shark_frames(self):
        """Load and normalize shark animation frames from mockups.txt file."""
        try:
            with open("mockups.txt", "r", encoding="utf-8") as f:
                content = f.read()
            
            start_marker = "-SHARK-"
            end_marker = "-END SHARK-"
            
            start = content.find(start_marker)
            end = content.find(end_marker)
            
            if start == -1 or end == -1:
                return self._get_fallback_frames()
            
            shark_content = content[start:end]
            pattern = re.compile(r"frame \d+\n(.*?)(?=\nframe|\Z)", re.DOTALL)
            matches = pattern.findall(shark_content)
            
            if not matches:
                return self._get_fallback_frames()
            
            processed_frames = []
            for frame_text in matches:
                frame_lines = frame_text.strip('\n').split('\n')
                
                # BUGFIX: Normalize the ASCII art to fix alignment
                # 1. Filter out empty lines
                non_empty_lines = [line for line in frame_lines if line.strip()]
                if not non_empty_lines:
                    continue

                # 2. Find the minimum indentation of the frame
                min_indent = min(len(line) - len(line.lstrip(' ')) for line in non_empty_lines)

                # 3. Create the new frame with the minimum indentation removed
                normalized_lines = [line[min_indent:] for line in frame_lines]
                processed_frames.append(normalized_lines)
            
            return processed_frames
            
        except Exception as e:
            print(f"Error loading shark frames: {e}, using fallback")
            return self._get_fallback_frames()
    
    def _get_fallback_frames(self):
        """Fallback shark frames if loading fails."""
        return [
            [
                "    /|    /|  ",
                "   /  \\__/  \\ ",
                "  /  SHARK   \\",
                " <_____________>",
                "   \\  ____  /",
                "    \\/    \\/",
            ]
        ]
    
    def _get_current_frame_art(self):
        """Convert current shark frame to the art format used by Fish class."""
        if not self.shark_frames:
            return [[('S', Fore.RED)]]
        
        frame_lines = self.shark_frames[self.current_frame % len(self.shark_frames)]
        processed_art = []
        
        for line in frame_lines:
            processed_line = []
            for char in line:
                # TWEAK: Use the randomly selected shark color
                color = self.shark_color if char != ' ' else Fore.RESET
                processed_line.append((char, color))
            processed_art.append(processed_line)
        
        return processed_art
    
    def update(self):
        """Update shark position and animation."""
        if not self.active:
            return
        
        self.frame_counter += 1
        if self.frame_counter >= self.frames_per_animation:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.shark_frames)
            self.art = self._get_current_frame_art()
            self.art_width = max(len(line) for line in self.art) if self.art else 1
        
        self.x -= self.speed
        
        # Check if shark has moved far enough to startle new fish
        if abs(self.x - self.last_startle_x) > 1:
            self._startle_nearby_fish()
            self.last_startle_x = self.x
        
        # BUGFIX: Correctly remove shark when it's off the left side of the screen
        if self.x + self.art_width < 0:
            self.active = False
    
    def _startle_nearby_fish(self):
        """Startle all fish within radius of the shark."""
        shark_center_x = self.x + (self.art_width / 2)
        shark_center_y = self.y + (self.art_height / 2)
        
        for fish in self.aquarium_ref.fishes:
            if fish == self: continue
            fish_center_x = fish.x + (fish.art_width / 2)
            fish_center_y = fish.y + (fish.art_height / 2)
            distance = math.sqrt((fish_center_x - shark_center_x)**2 + 
                               (fish_center_y - shark_center_y)**2)
            if distance <= self.startle_radius:
                fish.startle()
        
        for school in self.aquarium_ref.schools:
            school_center_x = school.x + school.formation_width / 2
            school_center_y = school.y + school.formation_height / 2
            distance = math.sqrt((school_center_x - shark_center_x)**2 + 
                               (school_center_y - shark_center_y)**2)
            if distance <= self.startle_radius:
                school.startle()
    
    def startle(self):
        pass
    
    def seek_food(self, food_pellet):
        pass
    
    def turn_around(self):
        pass
    
    def is_active(self):
        return self.active
    
    @staticmethod
    def should_spawn():
        return random.random() < SHARK_CHANCE