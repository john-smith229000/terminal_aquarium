import random
import math
from colorama import Fore
from perlin_noise import PerlinNoise
from config import EEL_SPEED_RANGE

# Mock objects for standalone execution
class MockAscii:
    COLOR_ADJUSTMENTS = {'light_mode': {Fore.LIGHTGREEN_EX: Fore.BLACK}}
COLOR_ADJUSTMENTS = MockAscii.COLOR_ADJUSTMENTS
FRAME_RATE = 1 / 30.0


class Eel:
    """
    Represents an eel with a head that drags a flowing, segmented body,
    creating realistic curves based on movement and inertia with enhanced ASCII art.
    """
    
    def __init__(self, width, height, background_color):
        # --- Enhanced Tuning Parameters ---
        self.WAVELENGTH = 120.0
        self.WAVE_SPEED = 1.8
        self.BASE_AMPLITUDE = 0.25
        self.NOISE_SPEED = 0.08      
        self.AMP_VARIATION = 0.35
        self.SEGMENT_SPACING = 0.6
        self.FLOW_SMOOTHNESS = 0.88
        self.ORGANIC_VARIATION = 0.15
        # --- End of Tuning Parameters ---

        self.width = width
        self.height = height
        self.background_color = background_color
        
        self.wave_phase_step = (math.pi * 2) / self.WAVELENGTH

        # Enhanced noise generators for more organic movement
        self.noise_amp = PerlinNoise(octaves=3, seed=random.randint(101, 200))
        self.noise_lateral = PerlinNoise(octaves=2, seed=random.randint(201, 300))
        self.noise_head_amp = PerlinNoise(octaves=4, seed=random.randint(301, 400))
        self.noise_head_freq = PerlinNoise(octaves=3, seed=random.randint(401, 500))
        self.noise_thickness = PerlinNoise(octaves=2, seed=random.randint(501, 600))
        self.noise_micro = PerlinNoise(octaves=5, seed=random.randint(601, 700))
        self.animation_time = 0

        # Enhanced ASCII character sets for outline only
        self.outline_chars = {
            'top': {
                'steep_up': '/',
                'moderate_up': '`',
                'slight_up': "=",
                'flat': '-',
                'slight_down': '.',
                'moderate_down': '.',
                'steep_down': '\\',
                'very_steep': '|'
            },
            'bottom': {
                'steep_up': '/',
                'moderate_up': '.',
                'slight_up': '.',
                'flat': '_',
                'slight_down': '.',
                'moderate_down': ',',
                'steep_down': '\\',
                'very_steep': '|'
            }
        }

        self.head_art = {
            'forward': [
                """  _      """,
                """-'`_"-._ """,
                """  (@)   \\""",
                """  _.,,.,-'""",
                """-="-\\;,_; """,
            ],
            'backward': [
                """      _   """,
                """ _.-'" _''-""",      
                """/    (@)   '""",
                """`-,.,,._   """,      
                """ ;_,;/-"=-""",
            ],
        }        
        
        self.processed_head = {}
        for direction, art in self.head_art.items():
            processed_lines = []
            for line in art:
                processed_line = []
                for char in line:
                    color = Fore.LIGHTGREEN_EX if char != ' ' else Fore.RESET
                    processed_line.append((char, color))
                processed_lines.append(processed_line)
            self.processed_head[direction] = processed_lines
        
        self.head_width = max(len(line) for line in self.head_art['forward'])
        self.head_height = len(self.head_art['forward'])
        
        self.body_length = random.randint(50, 75)
        self.body_segments = []
        
        self.direction = random.choice(['forward', 'backward'])
        self.speed = random.uniform(0.9, 1.4)
        self.normal_speed = self.speed
        
        self.base_head_y = random.randint(5, height - self.head_height - 10)
        #self.head_x = float(random.randint(0, width - self.head_width))

        if self.direction == 'forward':
            # Moving right, so start on the left.
            # Place the head's left edge far enough left that the whole body is also off-screen.
            total_eel_length = self.head_width + (self.body_length * self.SEGMENT_SPACING)
            self.head_x = float(-total_eel_length)
        else:
            # Moving left, so start on the right.
            # Place the head's left edge at the screen's width. The body will trail off-screen to the right.
            self.head_x = float(self.width)
            
        self.head_y = self.base_head_y
        self.prev_head_y = self.head_y
        self.head_y_delta = 0

        self.head_wave_amplitude = 0.0
        self.head_wave_frequency = 0.0
        self.lateral_drift = 0.0

        self.is_wrapping = False

        self.active = True
        
        self._initialize_body()
        
        self.is_startled = False
        self.startle_timer = 0.0
        self.peak_startle_speed = 0.0

    def is_active(self):
        """Returns False if the eel should be removed."""
        return self.active
        
    def _get_body_connection_points(self):
        """Get the precise coordinates where the body should attach to the head."""
        if self.direction == 'forward':
            connection_x = self.head_x - 1.2 
            connection_y_start = self.head_y + 2
            connection_y_end = self.head_y + 4
        else:
            connection_x = self.head_x + self.head_width + 0.2
            connection_y_start = self.head_y + 2
            connection_y_end = self.head_y + 4
        return connection_x, connection_y_start, connection_y_end
        
    def _calculate_body_thickness(self, segment_index):
        """Calculate the body thickness with organic variation, tapering toward the tail."""
        progress = segment_index / (self.body_length - 1)
        
        # Base thickness with smoother tapering
        base_thickness = max(1, int(4.0 * (1 - progress) ** 0.4))
        
        # Add organic thickness variation
        thickness_variation = self.noise_thickness(segment_index * 0.08 + self.animation_time * 0.03)
        varied_thickness = base_thickness + int(thickness_variation * 1.5)
        
        return max(1, varied_thickness)
        
    def _initialize_body(self):
        """Initialize body segments in a smooth curve behind the head."""
        self.body_segments = []
        connection_x, y_start, y_end = self._get_body_connection_points()
        y_center = (y_start + y_end) / 2
        
        for i in range(self.body_length):
            segment_offset = (i + 1) * self.SEGMENT_SPACING
            if self.direction == 'forward':
                seg_x = connection_x - segment_offset
            else:
                seg_x = connection_x + segment_offset
            
            # Add slight initial curve for more natural initialization
            initial_curve = math.sin(i * 0.1) * 0.5
            segment_data = {'x': seg_x, 'y': y_center + initial_curve}
            self.body_segments.append(segment_data)
    
    def update(self):
        """Update the eel's state, including position and body animation."""
        if not self.active:
            return
        self.animation_time += FRAME_RATE
        if self.is_startled:
            self._update_startled_speed()
        self._move_head()
        self._update_body_flow()

    def _move_head(self):
        """Handle head movement with enhanced organic motion."""
        self.prev_head_y = self.head_y
        
        # Horizontal movement
        if self.direction == 'forward':
            self.head_x += self.speed
        else:
            self.head_x -= self.speed
            
        """# Enhanced screen wrapping logic
        if not self.is_wrapping:
            if self.direction == 'forward' and self.head_x > self.width:
                self.is_wrapping = True
            elif self.direction == 'backward' and self.head_x < -self.head_width:
                self.is_wrapping = True
        else:
            tail = self.body_segments[-1]
            if self.direction == 'forward' and tail['x'] > self.width:
                self.head_x = -self.head_width
                self.base_head_y = random.randint(5, self.height - self.head_height - 10)
                self._initialize_body()
                self.is_wrapping = False
            elif self.direction == 'backward' and tail['x'] < 0:
                self.head_x = self.width
                self.base_head_y = random.randint(5, self.height - self.head_height - 10)
                self._initialize_body()
                self.is_wrapping = False"""
        
        # Despawning logic: check if the entire eel is off-screen
        if self.body_segments:
            # If moving forward, the head is the last part to leave the left side.
            # We check if the tail (the first part to leave the right side) is off-screen.
            if self.direction == 'forward':
                leftmost_point = self.body_segments[-1]['x']
                if leftmost_point > self.width:
                    self.active = False
            # If moving backward, the head is the last part to leave the right side.
            # We check if the tail (the first part to leave the left side) is off-screen.
            elif self.direction == 'backward':
                rightmost_point = self.body_segments[-1]['x']
                if rightmost_point < 0:
                    self.active = False

        # Enhanced head wave motion with multiple noise layers
        MIN_HEAD_AMP, MAX_HEAD_AMP = 0.5, 5.0
        MIN_HEAD_FREQ, MAX_HEAD_FREQ = 0.03, 0.25
        
        # Primary amplitude variation
        noise_amp = self.noise_head_amp(self.animation_time * 0.08)
        normalized_noise_amp = noise_amp + 0.5
        self.head_wave_amplitude = MIN_HEAD_AMP + (normalized_noise_amp * (MAX_HEAD_AMP - MIN_HEAD_AMP))
        
        # Primary frequency variation
        noise_freq = self.noise_head_freq(self.animation_time * 0.06)
        normalized_noise_freq = noise_freq + 0.5
        self.head_wave_frequency = MIN_HEAD_FREQ + (normalized_noise_freq * (MAX_HEAD_FREQ - MIN_HEAD_FREQ))
        
        # Add micro-movements for more organic feel
        micro_variation = self.noise_micro(self.animation_time * 0.5) * 0.3
        
        # Calculate final head position
        primary_wave = self.head_wave_amplitude * math.sin(self.head_x * self.head_wave_frequency)
        lateral_drift = self.noise_lateral(self.animation_time * 0.04) * 1.2
        
        self.head_y = self.base_head_y + primary_wave + lateral_drift + micro_variation
        self.head_y_delta = self.head_y - self.prev_head_y
        
    def _update_body_flow(self):
        """Update body segments with enhanced organic flow and distance maintenance."""
        connection_x, y_start, y_end = self._get_body_connection_points()
        leader_x = connection_x
        leader_y = (y_start + y_end) / 2.0 + (self.head_y_delta * 0.6)
        
        # Multi-layered amplitude noise for complex movement
        primary_amp_noise = self.noise_amp(self.animation_time * self.NOISE_SPEED)
        secondary_amp_noise = self.noise_lateral(self.animation_time * self.NOISE_SPEED * 1.5) * 0.3

        for i, segment in enumerate(self.body_segments):
            progress = i / self.body_length
            
            # Calculate ideal target position
            if self.direction == 'forward':
                ideal_x = leader_x - self.SEGMENT_SPACING
            else:
                ideal_x = leader_x + self.SEGMENT_SPACING
            
            # Enhanced amplitude calculation with organic variation
            segment_amplitude = self.BASE_AMPLITUDE * (1 - progress * 0.8)
            current_amp = segment_amplitude + primary_amp_noise * self.AMP_VARIATION + secondary_amp_noise
            
            # Time-based wave with organic micro-variations
            phase = (self.animation_time * self.WAVE_SPEED) - (i * self.wave_phase_step)
            base_wave = current_amp * math.sin(phase)
            
            # Add organic micro-oscillations
            micro_wave = self.noise_micro(i * 0.3 + self.animation_time * 0.3) * current_amp * 0.2
            wave_y_offset = base_wave + micro_wave
            
            ideal_y = leader_y + wave_y_offset
            
            # Calculate distance to maintain proper spacing
            current_distance = math.sqrt((segment['x'] - leader_x)**2 + (segment['y'] - leader_y)**2)
            desired_distance = self.SEGMENT_SPACING
            
            # Dynamic lerp factor based on distance to prevent compression
            min_distance = 0.8  # Minimum distance between segments
            if current_distance < min_distance:
                # Force separation if too close
                distance_factor = 0.9
            elif current_distance > desired_distance * 2:
                # Pull closer if too far
                distance_factor = 0.8
            else:
                # Normal following behavior
                base_lerp = self.FLOW_SMOOTHNESS * (1 - progress * 0.2) + 0.25 * progress
                lerp_variation = self.noise_micro(i * 0.2 + self.animation_time * 0.1) * 0.05
                distance_factor = max(0.15, min(0.85, base_lerp + lerp_variation))
            
            # Apply smooth interpolation with distance maintenance
            new_x = segment['x'] + (ideal_x - segment['x']) * distance_factor
            new_y = segment['y'] + (ideal_y - segment['y']) * distance_factor
            
            # Ensure minimum distance is maintained
            actual_distance = math.sqrt((new_x - leader_x)**2 + (new_y - leader_y)**2)
            if actual_distance < min_distance and actual_distance > 0:
                # Normalize and push to minimum distance
                norm_x = (new_x - leader_x) / actual_distance
                norm_y = (new_y - leader_y) / actual_distance
                new_x = leader_x + norm_x * min_distance
                new_y = leader_y + norm_y * min_distance
            
            segment['x'], segment['y'] = new_x, new_y
            leader_x, leader_y = new_x, new_y
            
    def _update_startled_speed(self):
        """Update speed during startled state."""
        self.startle_timer -= FRAME_RATE
        if self.startle_timer <= 0:
            self.is_startled = False
            self.speed = self.normal_speed
        else:
            progress = self.startle_timer / 2.0
            speed_range = self.peak_startle_speed - self.normal_speed
            self.speed = self.normal_speed + (speed_range * progress)
    
    def startle(self):
        """Trigger startled behavior."""
        if not self.is_startled:
            self.is_startled = True
            self.startle_timer = 2.0
            startle_multiplier = random.uniform(3.0, 5.0)
            self.peak_startle_speed = self.normal_speed * startle_multiplier
            self.speed = self.peak_startle_speed
            
    def get_adjusted_color(self, color):
        """Adjust color based on background."""
        from colorama import Back
        if self.background_color == Back.LIGHTCYAN_EX:
            return COLOR_ADJUSTMENTS.get('light_mode', {}).get(color, color)
        return color
        
    def _get_char_for_outline(self, y_delta, is_top, segment_index):
        """Get the appropriate character for the outline based on slope and position."""
        # Add some organic variation using segment position
        variation = math.sin(segment_index * 0.3) * 0.1
        adjusted_delta = y_delta + variation
        
        char_set = self.outline_chars['top'] if is_top else self.outline_chars['bottom']
        
        if adjusted_delta < -2.0:
            return char_set['very_steep']
        elif adjusted_delta < -1.5:
            return char_set['steep_up']
        elif adjusted_delta < -0.8:
            return char_set['moderate_up']
        elif adjusted_delta < -0.2:
            return char_set['slight_up']
        elif adjusted_delta <= 0.2:
            return char_set['flat']
        elif adjusted_delta <= 0.8:
            return char_set['slight_down']
        elif adjusted_delta <= 1.5:
            return char_set['moderate_down']
        elif adjusted_delta <= 2.0:
            return char_set['steep_down']
        else:
            return char_set['very_steep']

    def draw(self, buffer):
        """Draw the eel with head and hollow body outline."""
        # Draw head
        head_x, head_y = int(self.head_x), int(self.head_y)
        for line_idx, line_data in enumerate(self.processed_head[self.direction]):
            y = head_y + line_idx
            if 0 <= y < self.height:
                for char_idx, (char, color) in enumerate(line_data):
                    x = head_x + char_idx
                    if char != ' ' and 0 <= x < self.width:
                        buffer[y][x] = (char, self.get_adjusted_color(color))

        # Draw body outline only
        body_color = self.get_adjusted_color(Fore.LIGHTGREEN_EX)
        
        for i, segment in enumerate(self.body_segments):
            seg_x, seg_y = int(segment['x']), int(segment['y'])
            thickness = self._calculate_body_thickness(i)
            
            # Calculate slope for organic character selection
            if i > 0:
                prev_seg_y = self.body_segments[i-1]['y']
                y_delta = seg_y - prev_seg_y
            else:
                # For the first segment, use head connection
                connection_x, y_start, y_end = self._get_body_connection_points()
                y_center = (y_start + y_end) / 2
                y_delta = seg_y - y_center

            # Add subtle thickness variation using noise
            thickness_noise = self.noise_thickness(i * 0.1 + self.animation_time * 0.05)
            dynamic_thickness = max(1, thickness + int(thickness_noise * 0.5))

            if dynamic_thickness > 1:
                half_thickness = dynamic_thickness / 2.0
                top_y = int(seg_y - half_thickness + 0.5)
                bottom_y = int(seg_y + half_thickness - 0.5)

                # Draw top outline
                if 0 <= top_y < self.height and 0 <= seg_x < self.width:
                    char = self._get_char_for_outline(y_delta, is_top=True, segment_index=i)
                    buffer[top_y][seg_x] = (char, body_color)
                
                # Draw bottom outline (only if different from top)
                if top_y != bottom_y and 0 <= bottom_y < self.height and 0 <= seg_x < self.width:
                    char = self._get_char_for_outline(y_delta, is_top=False, segment_index=i)
                    buffer[bottom_y][seg_x] = (char, body_color)
            else:
                # For thin segments, draw a single line
                y = int(seg_y)
                if 0 <= y < self.height and 0 <= seg_x < self.width:
                    char = self._get_char_for_outline(y_delta, is_top=True, segment_index=i)
                    # Use a more subtle character for thin tail segments
                    if i > self.body_length * 0.7:  # Tail region
                        char = '.' if char in ['-', '_'] else char
                    buffer[y][seg_x] = (char, body_color)