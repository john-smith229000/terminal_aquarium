import random
from colorama import Fore
from ascii_art import BUBBLE_CHARS
from config import (
    BUBBLE_SPEED_RANGE, CLICK_BUBBLE_SPEED_RANGE, CLICK_BUBBLE_LIFETIME_RANGE
)


class Bubble:
    """Represents a single bubble rising from the floor."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.color = Fore.CYAN
        self.art = random.choice(BUBBLE_CHARS)
        self.reset()

    def reset(self):
        """Resets the bubble to a new position at the bottom."""
        self.x = random.randint(0, self.width - 1)
        self.y = random.uniform(self.height - 5, self.height - 2)
        self.speed = random.uniform(*BUBBLE_SPEED_RANGE)

    def update(self):
        """Moves the bubble upwards."""
        self.y -= self.speed
        if self.y <= 0:
            self.reset()

    def draw(self, buffer):
        """Draws the bubble onto the provided buffer."""
        x, y = int(self.x), int(self.y)
        if 0 <= y < self.height and 0 <= x < self.width:
            # Only draw if the space is empty
            if buffer[y][x][0] == ' ':
                buffer[y][x] = (self.art, self.color)


class ClickBubble:
    """Represents a temporary bubble created from a key press."""
    def __init__(self, x, y, width, height):
        self.width = width
        self.height = height
        self.color = random.choice([Fore.CYAN, Fore.LIGHTCYAN_EX, Fore.WHITE, Fore.LIGHTBLUE_EX])
        self.art = random.choice(BUBBLE_CHARS)
        self.x = float(x)
        self.y = float(y)
        self.speed = random.uniform(*CLICK_BUBBLE_SPEED_RANGE)
        self.lifetime = random.uniform(*CLICK_BUBBLE_LIFETIME_RANGE)
        self.age = 0.0

    def update(self):
        """Moves the bubble upwards and ages it."""
        self.y -= self.speed
        self.age += 0.1  # Increment by frame rate
        return self.age < self.lifetime and self.y > 0  # Return False when should be removed

    def draw(self, buffer):
        """Draws the click-generated bubble onto the provided buffer."""
        x, y = int(self.x), int(self.y)
        if 0 <= y < self.height and 0 <= x < self.width:
            # Only draw if the space is empty
            if buffer[y][x][0] == ' ':
                buffer[y][x] = (self.art, self.color)