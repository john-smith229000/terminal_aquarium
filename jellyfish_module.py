import random
from colorama import Fore, Back
from ascii_art import COLOR_ADJUSTMENTS

# --- Jellyfish Configuration ---
COLOR_CHOICES = [Fore.MAGENTA, Fore.CYAN, Fore.LIGHTBLUE_EX, Fore.LIGHTMAGENTA_EX, Fore.LIGHTCYAN_EX]

JELLYFISH_ART = [
    (
    "         .-;':'-.",
    "        {'.'.'.'.}",
    "        '-. ._.-='",
    "          ). ( ')",
    "          (' ) (",
    "           ).(.)",
    "          ( .').'",
    "          .)' (" ,
    "           '  ).",
    ),
#// Tentacles expanding outward
    (
    "         .-;':'-.",
    "        {'.'.'.'.}",
    "        '-. ._.-='",
    "          ). ( ')",
    "         (  ' )  )",
    "        (   ).(   )",
    "         (  .').'  )",
    "          .)'   (",  
    "            '    ).", 
    ),
    (
    "         .-;':'-.",
    "        {'.'.'.'.}",
    "        '-. ._.-='",
    "         ( ). ( )",
    "        ( (' ) (') )",
    "       (   ).(.)   )",
    "        (  .').'  )",
    "          .)'   (",   
    "            '    ).", 
    ),

#// Tentacles fully ballooned
    (
    "         .-;':'-.",
    "        {'.'.'.'.}",
    "        '-. ._.-='",
    "        (( ). ( ))",
    "      (   (' ) (') )",
    "     (    ).(.)     )",
    "       (   .').'   )",
    "         ( .)' ( )",
    "          '    ).",   
    ),

    (
    "         .-;':'-.",
    "        {'.'.'.'.}",
    "        '-. ._.-='",
    "         ( ). ( )",
    "        ( (' ) (') )",
    "       (   ).(.)    )",
    "         ( .').' )",
    "          .)'  (",   
    "            '   ).", 
    ),

    (
    "         .-;':'-.",
    "        {'.'.'.'.}",
    "        '-. ._.-='",
    "          ). ( ')",
    "         (  ' )  )",
    "        (   ).(   )",
    "         (  .').'  )",
    "          .)'   (",  
    "            '    ).", 
    ),

    (
    "         .-;':'-.",
    "        {'.'.'.'.}",
    "        '-. ._.-='",
    "          ). ( ')",
    "          (' ) (",
    "           ).(.)",
    "          ( .').'",
    "          .)' (" ,
    "           '  ).",
    ),

#// Tentacles contracting inward
    (
    "         .-;':'-.",
    "        {'.'.'.'.}",
    "        '-. ._.-='",
    "          ). ( ')",
    "          (' ) (",
    "           ).(.)",
    "          ( .').'",
    "           .)' (",
    "            '  ).",
    ),
]



class Jellyfish:
    """Represents a single, animated jellyfish. Designed to be imported."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.speed = random.uniform(0.1, 0.4)

        self.animation_speed = random.uniform(0.1, 0.5) 
        self.animation_counter = 0.0

        self.bell_color = random.choice(COLOR_CHOICES)
        self.tentacle_color = random.choice(COLOR_CHOICES)
        while self.tentacle_color == self.bell_color:
            self.tentacle_color = random.choice(COLOR_CHOICES)

        self.current_frame_index = random.randint(0, len(JELLYFISH_ART) - 1)
        self.animation_frames = self._process_frames()
        self.art_height = len(self.animation_frames[0])
        self.art_width = max(len(line) for line in self.animation_frames[0])
        self.x = float(random.randint(0, width - self.art_width))
        self.y = float(random.randint(0, height - self.art_height))

    def _process_frames(self):
        processed_frames = []
        for frame_art in JELLYFISH_ART:
            colored_frame = []
            for i, line in enumerate(frame_art):
                colored_line = []
                color = self.bell_color if i < 3 else self.tentacle_color
                for char in line:
                    colored_line.append((char, color))
                colored_frame.append(colored_line)
            processed_frames.append(colored_frame)
        return processed_frames

    def update(self):
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.current_frame_index = (self.current_frame_index + 1) % len(self.animation_frames)
            self.animation_counter -= 1 # Reset counter, keeping remainder
        self.y -= self.speed
        if self.y < -self.art_height:
            self.y = self.height
            self.x = float(random.randint(0, self.width - self.art_width))

    def get_current_art(self, background_color):
        """
        Returns the current animation frame.
        If in light mode, it dynamically adjusts colors before returning.
        """
        frame_with_original_colors = self.animation_frames[self.current_frame_index]

        # If we are not in light mode, return the pre-calculated frame
        if background_color != Back.LIGHTCYAN_EX:
            return frame_with_original_colors

        # If we are in light mode, create a new frame with adjusted colors
        adjusted_frame = []
        for line in frame_with_original_colors:
            adjusted_line = []
            for char, original_color in line:
                # Look up the adjustment, defaulting to original color if no adjustment is needed
                adjusted_color = COLOR_ADJUSTMENTS.get('light_mode', {}).get(original_color, original_color)
                adjusted_line.append((char, adjusted_color))
            adjusted_frame.append(adjusted_line)

        return adjusted_frame
    
    def draw(self, buffer, background_color):
        """Draws the jellyfish onto the provided buffer."""
        x, y = int(self.x), int(self.y)
        # Get the correctly colored art for the current background
        art_grid = self.get_current_art(background_color)
        
        for line_idx, line_data in enumerate(art_grid):
            current_y = y + line_idx
            if 0 <= current_y < self.height:
                for char_idx, (char_art, color) in enumerate(line_data):
                    current_x = x + char_idx
                    if char_art != ' ' and 0 <= current_x < self.width:
                        # This rule makes jellyfish appear behind other creatures
                        if buffer[current_y][current_x][0] == ' ':
                            buffer[current_y][current_x] = (char_art, color)