import random
import math
from colorama import Fore
from perlin_noise import PerlinNoise

# Mock objects for standalone execution
class MockAscii:
    COLOR_ADJUSTMENTS = {'light_mode': {Fore.GREEN: Fore.BLACK}}
COLOR_ADJUSTMENTS = MockAscii.COLOR_ADJUSTMENTS
FRAME_RATE = 1 / 30.0


class Eel:
    """
    Represents an eel with a head that drags a flowing, segmented body,
    creating realistic curves based on movement and inertia.
    """
    
    def __init__(self, width, height, background_color):
        # --- NEW Easy Tuning Parameters ---
        # WAVELENGTH: Controls the length of the wave. Higher number = longer, stretched-out wave.
        self.WAVELENGTH = 150.0
        
        # WAVE_SPEED: Controls the speed of the undulation. Higher number = faster wiggle.
        self.WAVE_SPEED = 2.0
        
        # Amplitude: Controls the height of the waves (powerful at the neck, fading to the tail).
        self.BASE_AMPLITUDE = 0.2
        
        # Variability: Controls the Perlin noise effect for a more organic feel.
        self.NOISE_SPEED = 0.1      
        self.AMP_VARIATION = 1.5    
        # --- End of Tuning Parameters ---

        self.width = width
        self.height = height
        self.background_color = background_color
        
        # This calculates the internal phase step needed to achieve the desired wavelength
        self.wave_phase_step = (math.pi * 2) / self.WAVELENGTH

        # Initialize Perlin noise generators
        self.noise_amp = PerlinNoise(octaves=2, seed=random.randint(101, 200))
        self.animation_time = 0

        self.head_art = {
            'forward': [
                """  _       """,
                """-'`_"`-._ """,
                """   (@)   \\""",
                """   _.,,.,-'""",
                """-="-\\;,_; """,
            ],
            'backward':[
                """      _""",
                """ _.-'" _''-""" ,      
                """/    (@)   '""",
                """`-,.,,._   """,      
                """ ;_,;/-"=-""" ,
            ],
        }        
        
        self.processed_head = {}
        for direction, art in self.head_art.items():
            processed_lines = []
            for line in art:
                processed_line = []
                for char in line:
                    color = Fore.GREEN if char != ' ' else Fore.RESET
                    processed_line.append((char, color))
                processed_lines.append(processed_line)
            self.processed_head[direction] = processed_lines
        
        self.head_width = max(len(line) for line in self.head_art['forward'])
        self.head_height = len(self.head_art['forward'])
        
        self.body_length = random.randint(50, 65)
        self.body_segments = []
        
        self.direction = random.choice(['forward', 'backward'])
        self.speed = random.uniform(0.5, 1.0)
        self.normal_speed = self.speed
        
        self.base_head_y = random.randint(5, height - self.head_height - 10)
        self.head_x = float(random.randint(0, width - self.head_width))
        self.head_y = self.base_head_y
        self.prev_head_y = self.head_y
        self.head_y_delta = 0

        self.head_wave_amplitude = random.uniform(0.2, 1.0)
        self.head_wave_frequency = random.uniform(0.04, 0.08)
        
        self._initialize_body()
        
        self.is_startled = False
        self.startle_timer = 0.0
        self.peak_startle_speed = 0.0
        
    def _get_body_connection_points(self):
        """Get the precise coordinates where the body should attach to the head."""
        if self.direction == 'forward':
            connection_x = self.head_x - 1 
            connection_y_start = self.head_y + 2
            connection_y_end = self.head_y + 4
        else:
            connection_x = self.head_x + self.head_width
            connection_y_start = self.head_y + 2
            connection_y_end = self.head_y + 4
        return connection_x, connection_y_start, connection_y_end
        
    def _calculate_body_thickness(self, segment_index):
        """Calculate the body thickness, tapering toward the tail."""
        progress = segment_index / (self.body_length - 1)
        thickness = max(1, int(4.5 * (1 - progress) ** 0.5))
        return thickness
        
    def _initialize_body(self):
        """Initialize body segments in a straight line behind the head."""
        self.body_segments = []
        connection_x, y_start, y_end = self._get_body_connection_points()
        y_center = (y_start + y_end) / 2
        
        for i in range(self.body_length):
            if self.direction == 'forward':
                seg_x = connection_x - (i + 1)
            else:
                seg_x = connection_x + (i + 1)
            
            segment_data = {'x': seg_x, 'y': y_center}
            self.body_segments.append(segment_data)
    
    def update(self):
        """Update the eel's state, including position and body animation."""
        self.animation_time += FRAME_RATE
        if self.is_startled:
            self._update_startled_speed()
        self._move_head()
        self._update_body_flow()

    def _move_head(self):
        """Handle head movement, including horizontal travel and vertical wave motion."""
        self.prev_head_y = self.head_y
        
        if self.direction == 'forward':
            self.head_x += self.speed
            if self.head_x >= self.width:
                self.head_x = -self.head_width
                self._initialize_body()
        else:
            self.head_x -= self.speed
            if self.head_x <= -self.head_width:
                self.head_x = self.width
                self._initialize_body()
                
        y_offset = self.head_wave_amplitude * math.sin(self.head_x * self.head_wave_frequency)
        self.head_y = self.base_head_y + y_offset
        self.head_y_delta = self.head_y - self.prev_head_y
        
    def _update_body_flow(self):
        """Update body segments to follow the head, simulating inertia and drag."""
        connection_x, y_start, y_end = self._get_body_connection_points()
        leader_x = connection_x
        leader_y = (y_start + y_end) / 2.0 + (self.head_y_delta * 2.0)
        
        amp_noise = self.noise_amp(self.animation_time * self.NOISE_SPEED)

        for i, segment in enumerate(self.body_segments):
            progress = i / self.body_length
            
            lerp_factor = 0.8 * (1 - progress) + 0.35 * progress
            
            # Amplitude is large at the neck and small at the tail
            base_amp = self.BASE_AMPLITUDE * (1 - progress)
            current_amp = base_amp + amp_noise * self.AMP_VARIATION
            
            target_x, target_y = leader_x, leader_y
            
            # ** NEW TIME-BASED WAVE CALCULATION **
            # This creates the wave in time and space, independent of forward speed.
            phase = (self.animation_time * self.WAVE_SPEED) - (i * self.wave_phase_step)
            wave_y_offset = current_amp * math.sin(phase)
            target_y += wave_y_offset
            
            new_x = segment['x'] + (target_x - segment['x']) * lerp_factor
            new_y = segment['y'] + (target_y - segment['y']) * lerp_factor
            
            segment['x'], segment['y'] = new_x, new_y
            leader_x, leader_y = new_x, new_y
            
    def _update_startled_speed(self):
        # ... (rest of the class is unchanged) ...
        self.startle_timer -= FRAME_RATE
        if self.startle_timer <= 0:
            self.is_startled = False
            self.speed = self.normal_speed
        else:
            progress = self.startle_timer / 2.0
            speed_range = self.peak_startle_speed - self.normal_speed
            self.speed = self.normal_speed + (speed_range * progress)
    
    def startle(self):
        if not self.is_startled:
            self.is_startled = True
            self.startle_timer = 2.0
            startle_multiplier = random.uniform(3.0, 5.0)
            self.peak_startle_speed = self.normal_speed * startle_multiplier
            self.speed = self.peak_startle_speed
            
    def get_adjusted_color(self, color):
        from colorama import Back
        if self.background_color == Back.LIGHTCYAN_EX:
            return COLOR_ADJUSTMENTS.get('light_mode', {}).get(color, color)
        return color
        
    def _get_char_for_slope(self, y_delta, is_top):
        if is_top:
            if y_delta < -1.2: return "/"
            if y_delta < -0.3: return "'"
            if y_delta <= 0.3: return "-"
            if y_delta <= 1.2: return '"'
            return "\\"
        else:
            if y_delta < -1.2: return "/"
            if y_delta < -0.3: return "-"
            if y_delta <= 0.3: return "_"
            if y_delta <= 1.2: return "/"
            return "\\"

    def draw(self, buffer):
        head_x, head_y = int(self.head_x), int(self.head_y)
        for line_idx, line_data in enumerate(self.processed_head[self.direction]):
            y = head_y + line_idx
            if 0 <= y < self.height:
                for char_idx, (char, color) in enumerate(line_data):
                    x = head_x + char_idx
                    if char != ' ' and 0 <= x < self.width:
                        buffer[y][x] = (char, self.get_adjusted_color(color))

        body_color = self.get_adjusted_color(Fore.GREEN)
        
        for i, segment in enumerate(self.body_segments):
            seg_x, seg_y = int(segment['x']), segment['y']
            thickness = self._calculate_body_thickness(i)
            
            prev_seg_y = self.body_segments[i-1]['y'] if i > 0 else seg_y
            y_delta = seg_y - prev_seg_y

            if thickness > 1:
                half_thickness = thickness / 2.0
                top_y = int(seg_y - half_thickness + 0.5)
                bottom_y = int(seg_y + half_thickness - 0.5)

                if 0 <= top_y < self.height and 0 <= seg_x < self.width:
                    char = self._get_char_for_slope(y_delta, is_top=True)
                    buffer[top_y][seg_x] = (char, body_color)
                
                if top_y != bottom_y and 0 <= bottom_y < self.height and 0 <= seg_x < self.width:
                    char = self._get_char_for_slope(y_delta, is_top=False)
                    buffer[bottom_y][seg_x] = (char, body_color)
            else:
                y = int(seg_y)
                if 0 <= y < self.height and 0 <= seg_x < self.width:
                    buffer[y][seg_x] = ('.', body_color)