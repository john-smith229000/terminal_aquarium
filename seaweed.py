import random
import math
from ascii_art import SEAWEED_SEGMENTS
from config import SEAWEED_HEIGHT_RANGE, SEAWEED_SWAY_SPEED


class Seaweed:
    """Represents a swaying stalk of seaweed."""
    def __init__(self, x_pos, width, height):
        self.x = x_pos
        self.aquarium_height = height
        self.width = width
        self.height = random.randint(*SEAWEED_HEIGHT_RANGE)
        self.segments = []
        self.sway_offset = random.uniform(0, math.pi * 2)  # Randomize sway cycle

        # Build the seaweed from bottom up using imported segment types
        for i in range(self.height):
            if i == 0:
                self.segments.append(random.choice(SEAWEED_SEGMENTS['base_types']))
            elif i == self.height - 1:
                self.segments.append(random.choice(SEAWEED_SEGMENTS['top_types']))
            else:
                self.segments.append(random.choice(SEAWEED_SEGMENTS['mid_types']))
    
    def draw(self, buffer, time_step):
        """Draws the swayed seaweed onto the provided buffer."""
        for segment in self.get_swayed_segments(time_step):
            x, y, art, color = segment['x'], segment['y'], segment['art'], segment['color']
            if 0 <= y < self.aquarium_height:
                for i, char_art in enumerate(art):
                    current_x = x + i
                    if 0 <= current_x < self.width:
                        buffer[y][current_x] = (char_art, color)

    def get_swayed_segments(self, time_step):
        """Calculates the current sway and returns segments with their positions."""
        swayed_data = []
        for i, (art, color) in enumerate(self.segments):
            sway_amount = int(math.sin(time_step * SEAWEED_SWAY_SPEED + self.sway_offset + i * 0.5) * (i / 2))
            actual_x = self.x + sway_amount
            y_pos = self.aquarium_height - 2 - i
            swayed_data.append({'x': actual_x, 'y': y_pos, 'art': art, 'color': color})
        return swayed_data