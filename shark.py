import random
import math
import re
from colorama import Fore, Back, Style
from fish import Fish
from config import FRAME_RATE, STARTLE_RADIUS

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
        
        # Load shark animation frames
        self.shark_frames = self._load_shark_frames()
        self.current_frame = 0
        self.frame_counter = 0
        self.frames_per_animation = 3  # Change frame every 3 update cycles
        
        # Shark positioning and movement
        self.direction = 'forward'  # Sharks always swim forward
        self.x = float(-50)  # Start off-screen to the left
        self.y = random.randint(2, min(8, height // 4))  # Near top of screen
        self.speed = random.uniform(0.3, 0.6)  # Slow, menacing speed
        self.normal_speed = self.speed
        
        # Shark doesn't use the normal fish art system
        self.art = self._get_current_frame_art()
        self.art_height = len(self.art)
        self.art_width = max(len(line) for line in self.art) if self.art else 1
        
        # Shark state
        self.state = 'swimming'
        self.target_food = None  # Sharks don't eat pellets
        self.is_startled = False  # Sharks don't get startled
        self.startle_timer = 0.0
        self.active = True  # Whether shark is still in scene
        
        # Startle effect properties
        self.startle_radius = 25  # Larger than normal fish startle radius
        self.last_startle_x = -100  # Track where we last startled fish
        
    def _load_shark_frames(self):
        """Load shark animation frames from mockups.txt file."""
        try:
            with open("mockups.txt", "r", encoding="utf-8") as f:
                content = f.read()
            
            # Find shark section
            start_marker = "-SHARK-"
            end_marker = "-END SHARK-"
            
            start = content.find(start_marker)
            end = content.find(end_marker)
            
            if start == -1 or end == -1:
                print("Warning: Shark frames not found in mockups.txt, using fallback")
                return self._get_fallback_frames()
            
            shark_content = content[start:end]
            
            # Extract frames with regex
            pattern = re.compile(r"frame \d+\n(.*?)(?=\nframe|\Z)", re.DOTALL)
            matches = pattern.findall(shark_content)
            
            if not matches:
                print("Warning: No shark frames found, using fallback")
                return self._get_fallback_frames()
            
            # Process frames into the format expected by the fish drawing system
            processed_frames = []
            for frame_text in matches:
                frame_lines = frame_text.strip().split('\n')
                # Filter out empty lines
                frame_lines = [line for line in frame_lines if line.strip()]
                processed_frames.append(frame_lines)
            
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
                # Make shark dark gray/white for visibility
                color = Fore.LIGHTWHITE_EX if char != ' ' else Fore.RESET
                processed_line.append((char, color))
            processed_art.append(processed_line)
        
        return processed_art
    
    def update(self):
        """Update shark position and animation."""
        if not self.active:
            return
        
        # Update animation frame
        self.frame_counter += 1
        if self.frame_counter >= self.frames_per_animation:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.shark_frames)
            self.art = self._get_current_frame_art()
            self.art_width = max(len(line) for line in self.art) if self.art else 1
        
        # Move shark forward
        self.x += self.speed
        
        # Check if shark has moved far enough to startle new fish
        if self.x - self.last_startle_x > 15:  # Startle every 15 units moved
            self._startle_nearby_fish()
            self.last_startle_x = self.x
        
        # Remove shark when it's completely off screen
        if self.x > self.width + 20:
            self.active = False
    
    def _startle_nearby_fish(self):
        """Startle all fish within radius of the shark."""
        shark_center_x = self.x + (self.art_width / 2)
        shark_center_y = self.y + (self.art_height / 2)
        
        # Startle individual fish
        for fish in self.aquarium_ref.fishes:
            if fish == self:  # Don't startle self
                continue
                
            fish_center_x = fish.x + (fish.art_width / 2)
            fish_center_y = fish.y + (fish.art_height / 2)
            distance = math.sqrt((fish_center_x - shark_center_x)**2 + 
                               (fish_center_y - shark_center_y)**2)
            
            if distance <= self.startle_radius:
                fish.startle()
        
        # Startle schools
        for school in self.aquarium_ref.schools:
            school_center_x = school.x + school.formation_width / 2
            school_center_y = school.y + school.formation_height / 2
            distance = math.sqrt((school_center_x - shark_center_x)**2 + 
                               (school_center_y - shark_center_y)**2)
            
            if distance <= self.startle_radius:
                school.startle()
    
    def startle(self):
        """Sharks don't get startled - they're apex predators!"""
        pass
    
    def seek_food(self, food_pellet):
        """Sharks don't eat pellets."""
        pass
    
    def turn_around(self):
        """Sharks don't turn around - they swim in one direction."""
        pass
    
    def is_active(self):
        """Check if shark is still active in the scene."""
        return self.active
    
    @staticmethod
    def should_spawn():
        """Determine if a shark should spawn this scene (low probability)."""
        return random.random() < 0.15  # 15% chance per scene generation