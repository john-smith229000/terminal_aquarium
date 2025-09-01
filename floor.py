import math
import random
from colorama import Fore

class Floor:
    """
    Represents a static, naturalistic seafloor with dunes and variations.
    The floor pattern is generated once and does not animate.
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.floor_y = height - 1
        
        # The character sequence for building the wave/dune shapes.
        wave_chars_up = ['_', ',', '.', '-', '~', '=', '"', "'", '`', '‾']
        # The downward slope starts from the second-highest character for a smoother peak
        wave_chars_down = wave_chars_up[:-1][::-1] 

        self.floor_pattern = []
        current_x = 0
        while current_x < self.width:
            # 1. Determine the height (amplitude) of the next dune.
            max_amp = random.randint(2, len(wave_chars_up))
            
            # 2. Determine the width of each step in the dune.
            step_width = random.randint(1, 3)

            # 3. Build the upward slope of the dune
            for i in range(max_amp):
                char = wave_chars_up[i]
                for _ in range(step_width):
                    if current_x < self.width:
                        self.floor_pattern.append(char)
                        current_x += 1
            
            # 4. Add a rounded peak to avoid sharp points
            peak_width = random.randint(1, 5)
            peak_char = wave_chars_up[max_amp - 1]
            for _ in range(peak_width):
                 if current_x < self.width:
                    self.floor_pattern.append(peak_char)
                    current_x += 1

            # 5. Build the downward slope of the dune
            # We iterate through a slice of the full downward slope
            for i in range(len(wave_chars_up) - max_amp, len(wave_chars_down)):
                char = wave_chars_down[i]
                for _ in range(step_width):
                    if current_x < self.width:
                        self.floor_pattern.append(char)
                        current_x += 1

            # 6. Add a shorter, varied flat area between dunes
            if current_x < self.width:
                flat_length = random.randint(2, 8)
                for _ in range(flat_length):
                    if current_x < self.width:
                        # Add a chance for a slight dip in the flat area
                        char = '_' if random.random() > 0.1 else '.'
                        self.floor_pattern.append(char)
                        current_x += 1

    def draw(self, buffer):
        """Draws the pre-generated seafloor pattern onto the buffer."""
        if not (0 <= self.floor_y < self.height):
            return

        for x in range(self.width):
            if x < len(self.floor_pattern):
                char_to_draw = self.floor_pattern[x]
                buffer[self.floor_y][x] = (char_to_draw, Fore.YELLOW)

