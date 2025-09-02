# Configuration file for the aquarium simulation

import random
from colorama import Back

# --- Scene Generation Parameters ---
MIN_FISH = 25
MAX_FISH = 50
NUM_BUBBLES = 20
NUM_JELLYFISH = random.randint(0, 4)
NUM_SEAWEED = random.randint(10, 15)
NUM_SCHOOLS = random.randint(1, 2)
CRAB_SPAWN_CHANCE = 5.0  # 50% chance to spawn a crab
DECORATION_SPAWN_CHANCE = 0.6  # 60% chance to spawn decorations
MAX_DECORATIONS = 4  # Maximum decorations at once
PUFFER_SPAWN_CHANCE = 0.3 # 30% chance for a puffer fish to spawn

# --- Animation Parameters ---
FRAME_RATE = 0.1  # Seconds per frame

# --- Display Parameters ---
BACKGROUND_COLOR = Back.BLACK
DEFAULT_TERMINAL_SIZE = (120, 30)

# --- Fish Behavior Parameters ---
STARTLE_RADIUS = 30.0
NORMAL_SPEED_RANGE = (0.5, 1.0)
FAST_SPEED_RANGE = (2.5, 4.5)
FAST_FISH_PROBABILITY = 0.08  # 8% chance for fast fish
STARTLE_MULTIPLIER_RANGE = (8.0, 11.0)
STARTLE_DURATION = 1.2

# --- PufferFish Behavior Parameters ---
PUFFER_NORMAL_SPEED_RANGE = (0.4, 0.7)  # Slower speed
PUFFER_STATE_DURATION = 10.0  # How long it stays puffed (in seconds)
PUFFER_PUFF_ANIMATION_SPEED = 0.6  # Time between each puff/deflate frame
PUFFER_SWIM_ANIMATION_SPEED = 0.15  # Time between swim frames while puffed

# --- Food Mechanic Parameters ---
FOOD_SINK_SPEED = 0.5  # Cells per frame
FOOD_LIFETIME = 4.0   # Seconds
FOOD_NOTICE_DELAY = 1.1 # Seconds before fish notice food
FOOD_NOTICE_RADIUS = 200.0 # Radius for fish to notice food
FOOD_SEEK_SPEED_MULTIPLIER = random.randint(2,4) # Speed boost when seeking

# --- School Behavior Parameters ---
SCHOOL_SIZE_RANGE = (15, 25)
FORMATION_WIDTH_RANGE = (6, 10)
FORMATION_HEIGHT_RANGE = (4, 7)
SCHOOL_SPEED_RANGE = (0.3, 0.8)
SCHOOL_STARTLE_MULTIPLIER_RANGE = (10, 14)
SCHOOL_STARTLE_DURATION = 1.3

# --- Bubble Parameters ---
BUBBLE_SPEED_RANGE = (0.1, 0.5)
CLICK_BUBBLE_SPEED_RANGE = (0.4, 1.2)
CLICK_BUBBLE_LIFETIME_RANGE = (4.0, 8.0)
BUBBLE_BURST_COUNT_RANGE = (30, 40)
BUBBLE_BURST_SPREAD = 8

# --- Crab Parameters ---
CRAB_IDLE_DURATION_RANGE = (3.0, 8.0)
CRAB_WALK_DURATION_RANGE = (1.0, 3.0)
CRAB_WALK_SPEED_RANGE = (0.5, 1.2)
CRAB_ANIMATION_SPEED = 0.2

# --- Seaweed Parameters ---
SEAWEED_HEIGHT_RANGE = (2, 11)
SEAWEED_SWAY_SPEED = 0.3

# --- Jellyfish Parameters ---
JELLYFISH_SPEED_RANGE = (0.05, 2)
JELLYFISH_ANIMATION_SPEED_RANGE = (0.3, 0.8)

# --- Sound Configuration ---
DEFAULT_SOUND_PATH = "underwater-ambience-6201.wav"
BUBBLE_SOUND_PATH = "bubbles-69893.mp3" # Assumed filename for your new sound
BUBBLE_SOUND_CLIP_DURATION = 1.5 # Play a 3-second clip
PUFFER_INFLATE_SOUND_PATH = "balloon-inflate-4-184055.mp3" # Assumed filename
CHEST_OPEN_SOUND_PATH = "material-chest-open-394472.mp3"
