import random
import time
import os
import sys
import math
from colorama import Fore, Back, Style, init
import pygame
import atexit

# Import our modular classes
from jellyfish_module import Jellyfish
from fish import Fish
from puffer import PufferFish
from seahorse import Seahorse, BabySeahorse
from school import School
from crab import Crab
from shark import Shark
from bubble import Bubble, ClickBubble
from seaweed import Seaweed
from decoration import Decoration, generate_decorations
from floor import Floor
from food import FoodPellet
from cross_platform_input import create_input_handler

# Import configuration
from config import *

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame not available. Sound will be disabled.")

# Initialize colorama
init(autoreset=True)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Aquarium:
    """Manages the entire scene, all objects, and the animation loop."""
    def __init__(self):
        self.set_terminal_size()
        self.time_step = 0
        self.background_colors = [Back.BLACK, Back.LIGHTCYAN_EX]
        self.current_background = BACKGROUND_COLOR
        self.paused = False

        self.input_handler = create_input_handler()
        atexit.register(self.cleanup)

        self.sound_on = False  # Sound is off by default
        self.sound = None
        self.bubble_sound_buffer = None # <-- Will store raw audio data
        self.mixer_props = None
        self.puffer_sound = None

        try:
            pygame.mixer.init()
            sound_file_path = resource_path(DEFAULT_SOUND_PATH)
            self.sound = pygame.mixer.Sound(sound_file_path)
            print("Sound loaded successfully. Press 's' to play/stop.")
            try:
                bubble_sound_path = resource_path(BUBBLE_SOUND_PATH)
                bubble_sound_obj = pygame.mixer.Sound(bubble_sound_path)
                self.bubble_sound_buffer = bubble_sound_obj.get_raw()
                self.mixer_props = pygame.mixer.get_init() # Get frequency, bit size, channels
                print("Bubble sound effect loaded successfully.")
            except Exception:
                print(f"Could not load bubble sound effect.")
                self.bubble_sound_buffer = None
            try:
                puffer_sound_path = resource_path(PUFFER_INFLATE_SOUND_PATH)
                self.puffer_sound = pygame.mixer.Sound(puffer_sound_path)
                print("Pufferfish sound effect loaded successfully.")
            except Exception:
                print(f"Could not load pufferfish sound effect.")
                self.puffer_sound = None
            try:
                chest_sound_path = resource_path(CHEST_OPEN_SOUND_PATH)
                self.chest_sound = pygame.mixer.Sound(chest_sound_path)
                print("Chest sound effect loaded successfully.")
            except Exception:
                print(f"Could not load chest sound effect.")
                self.chest_sound = None
            try:
                shark_sound_path = resource_path('shark.wav') # <-- Use your file's name
                self.shark_sound = pygame.mixer.Sound(shark_sound_path)
                print("Shark sound effect loaded successfully.")
            except Exception as e:
                print(f"Could not load shark sound effect: {e}")
                self.shark_sound = None
        except Exception as e:
            print(f"Could not load sound file: {e}")
            print("Sound will be unavailable.")

        self.generate_new_scene()

    def generate_new_scene(self):
        """Generates a completely new scene with randomized elements."""
        # Randomize scene parameters
        num_fish = random.randint(MIN_FISH, MAX_FISH)
        num_bubbles = random.randint(15, 25)
        num_jellyfish = random.randint(0, 6)
        num_seaweed = random.randint(8, 18)
        num_schools = random.randint(0, 3)
        crab_spawn_chance = random.uniform(0.3, 0.8)  # 30-80% chance
        self.food_pellets = []
        self.food_notice_timer = 0 
        
        # Create new objects
        self.fishes = []

        self.shark = None
        if Shark.should_spawn():
            self.shark_will_spawn = True
            # Set a random countdown timer for the shark to appear
            self.shark_spawn_timer = random.randint(MIN_SHARK_SPAWN_DELAY, MAX_SHARK_SPAWN_DELAY)
        else:
            self.shark_will_spawn = False
            self.shark_spawn_timer = 0

        if random.random() < PUFFER_SPAWN_CHANCE:
            # --- MODIFIED: Pass 'self' to the PufferFish ---
            self.fishes.append(PufferFish(self.width, self.height, self.current_background, self))
            num_fish -= 1
        # Add seahorse spawn chance
        # Add seahorse spawn chance
        if num_fish > 0 and random.random() < SEAHORSE_SPAWN_CHANCE:
            adult_seahorse = Seahorse(self.width, self.height, self.current_background)
            self.fishes.append(adult_seahorse)
            num_fish -= 1
            
            # Spawn baby seahorses with the adult
            from seahorse import BabySeahorse
            baby_seahorses = adult_seahorse.spawn_babies()
            for baby in baby_seahorses:
                if num_fish > 0:
                    self.fishes.append(baby)
                    num_fish -= 1
        for _ in range(num_fish):
            self.fishes.append(Fish(self.width, self.height, self.current_background))
        self.schools = [School(self.width, self.height, self.current_background) for _ in range(num_schools)]
        self.bubbles = [Bubble(self.width, self.height) for _ in range(num_bubbles)]
        self.click_bubbles = []  # List for temporary click-generated bubbles
        self.jellyfishes = [Jellyfish(self.width, self.height) for _ in range(num_jellyfish)]
        
        # Spawn crab based on random chance
        if random.random() < crab_spawn_chance:
            self.crab = Crab(self.width, self.height)
        else:
            self.crab = None
            
        seaweed_positions = random.sample(range(0, self.width - 3), min(num_seaweed, self.width - 3))
        self.seaweeds = [Seaweed(pos, self.width, self.height) for pos in seaweed_positions]

        # Generate decorations
        self.decorations = generate_decorations(self.width, self.height, self.current_background, self)
        
        # Reset time step for new scene
        self.time_step = 0

        self.floor = Floor(self.width, self.height)

    def play_sound_segment(self, raw_buffer, duration_sec):
        """Plays a random segment of a raw audio buffer."""
        if not raw_buffer or not self.sound_on or not self.mixer_props:
            return

        frequency, size, channels = self.mixer_props
        bytes_per_sample = abs(size) // 8 # e.g., 16-bit audio -> 2 bytes
        bytes_per_second = frequency * channels * bytes_per_sample

        total_len_bytes = len(raw_buffer)
        clip_len_bytes = int(duration_sec * bytes_per_second)

        # Ensure we don't try to play a clip longer than the file
        if clip_len_bytes >= total_len_bytes:
            start_byte = 0
        else:
            max_start_byte = total_len_bytes - clip_len_bytes
            start_byte = random.randint(0, max_start_byte)

        # Align start byte to the sample frame to prevent clicks/pops
        sample_frame_size = bytes_per_sample * channels
        start_byte = (start_byte // sample_frame_size) * sample_frame_size

        # Slice the buffer to get our random clip
        clip_buffer = raw_buffer[start_byte : start_byte + clip_len_bytes]

        # Create a new, temporary sound object from the sliced buffer and play it
        temp_sound = pygame.mixer.Sound(buffer=clip_buffer)
        temp_sound.play()

    def play_puffer_sound(self):
        """Plays the pufferfish inflation sound if sound is on."""
        if self.sound_on and self.puffer_sound:
            self.puffer_sound.play()

    def play_chest_sound(self):
        """Plays the chest opening sound if sound is on."""
        if self.sound_on and self.chest_sound:
            self.chest_sound.play()

    def play_shark_sound(self):
        """Plays the shark appearance sound if sound is on."""
        if self.sound_on and self.shark_sound:
            self.shark_sound.play()

    def drop_food(self):
        """Creates a food pellet at the top of the screen."""
        if not self.food_pellets: # Only allow one pellet at a time for simplicity
            buffer_zone = 15
            x = random.randint(buffer_zone, self.width - (buffer_zone + 1))
            pellet = FoodPellet(x, 0, self.width, self.height)
            self.food_pellets.append(pellet)
            self.food_notice_timer = FOOD_NOTICE_DELAY

    def cleanup(self):
        """Clean up resources on exit."""
        if hasattr(self, 'input_handler'):
            self.input_handler.cleanup()
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.quit()
            except Exception:
                pass

    def set_terminal_size(self):
        """Gets the current terminal size with better error handling."""
        try:
            # Try the standard method first
            self.width, self.height = os.get_terminal_size()
        except OSError:
            # Fallback 1: Try environment variables
            try:
                self.width = int(os.environ.get('COLUMNS', DEFAULT_TERMINAL_SIZE[0]))
                self.height = int(os.environ.get('LINES', DEFAULT_TERMINAL_SIZE[1]))
            except (ValueError, TypeError):
                # Fallback 2: Use defaults
                self.width, self.height = DEFAULT_TERMINAL_SIZE
                print(f"Could not detect terminal size. Using default: {self.width}x{self.height}")

    def get_char_input(self):
        """Gets a single character from input using the cross-platform handler."""
        char = self.input_handler.get_char()
        
        # Handle special keys consistently across platforms
        if char in ['CTRL_C', 'EOF']:
            # Treat these as exit signals
            return 'ESC'
        elif char in ['ENTER']:
            # You could add enter key functionality here if needed
            return None
        elif char in ['BACKSPACE']:
            # You could add backspace functionality here if needed
            return None
        elif isinstance(char, str) and char.startswith('EXTENDED_'):
            # Extended keys (function keys, arrow keys on Windows)
            return None
        elif char in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            # Arrow keys - you could add functionality here if needed
            return None
        
        return char

    def create_bubble_burst(self, x, y):
        self.play_sound_segment(self.bubble_sound_buffer, BUBBLE_SOUND_CLIP_DURATION)
        """Creates a burst of bubbles at the specified location."""
        num_burst_bubbles = random.randint(*BUBBLE_BURST_COUNT_RANGE)
        for _ in range(num_burst_bubbles):
            # Much wider spread around the point
            bubble_x = x + random.uniform(-BUBBLE_BURST_SPREAD, BUBBLE_BURST_SPREAD)
            bubble_y = y + random.uniform(-5, 5)
            
            # Keep bubbles within bounds
            bubble_x = max(0, min(bubble_x, self.width - 1))
            bubble_y = max(1, min(bubble_y, self.height - 2))
            
            click_bubble = ClickBubble(bubble_x, bubble_y, self.width, self.height)
            self.click_bubbles.append(click_bubble)

        # Check if any treasure chests are near the burst and open them
        for decoration in self.decorations:
            if decoration.is_near_point(x, y, radius=20):
                decoration.open_chest()

        # Startle fish and schools
        for fish in self.fishes:
            fish_center_x = fish.x + (fish.art_width / 2)
            fish_center_y = fish.y + (fish.art_height / 2)
            distance = math.sqrt((fish_center_x - x)**2 + (fish_center_y - y)**2)

            if distance <= STARTLE_RADIUS:
                fish.startle()
        
        for school in self.schools:
            school_center_x = school.x + school.formation_width / 2
            school_center_y = school.y + school.formation_height / 2
            distance = math.sqrt((school_center_x - x)**2 + (school_center_y - y)**2)

            if distance <= STARTLE_RADIUS:
                school.startle()

    def toggle_background(self):
        """Switches to the next background color."""
        try:
            current_index = self.background_colors.index(self.current_background)
            next_index = (current_index + 1) % len(self.background_colors)
            self.current_background = self.background_colors[next_index]
            
            # Update background reference in all objects
            for fish in self.fishes:
                fish.background_color = self.current_background
            for school in self.schools:
                school.background_color = self.current_background
            for decoration in self.decorations:
                decoration.background_color = self.current_background
                
        except ValueError:
            self.current_background = self.background_colors[0]
    
    def toggle_sound(self):
        """Toggles the looping background sound on and off."""
        if not self.sound: # Do nothing if sound failed to load
            return
            
        self.sound_on = not self.sound_on
        if self.sound_on:
            self.sound.play(loops=-1)  # loops=-1 means loop forever
        else:
            self.sound.stop()
    
    def check_terminal_resize(self):
        #Checks if terminal size has changed and updates accordingly.
        try:
            new_width, new_height = os.get_terminal_size()
            if new_width != self.width or new_height != self.height:
                self.width, self.height = new_width, new_height
                # Regenerate scene with new dimensions
                self.generate_new_scene()
                return True
        except OSError:
            pass
        return False

    def run(self):
        """Starts the main animation loop."""
        try:
            while True:
                if self.time_step % 10 == 0:  # Check every 10 frames
                    self.check_terminal_resize()

                input_result = self.get_char_input()
                if input_result:
                    # --- MODIFIED: Restructure input handling ---
                    # Keys that should always work, even when paused
                    if input_result.lower() == 'h':
                        self.paused = not self.paused
                        if self.paused:
                            self.original_background = self.current_background
                            self.current_background = Back.BLUE
                        else:
                            self.current_background = self.original_background
                    elif input_result.lower() == 's':
                        self.toggle_sound()
                    elif input_result == 'ESC' or input_result == 'q':
                        if self.sound_on and self.sound:
                            self.sound.stop()
                        pygame.mixer.quit()
                        print(f"{Style.RESET_ALL}\nThanks for visiting the aquarium!")
                        print("Press any key to close the terminal...")
                        
                        # Restore terminal settings before waiting
                        self.input_handler.cleanup()
                        
                        # Wait for user input before closing
                        if sys.platform == "win32":
                            import msvcrt
                            msvcrt.getch()
                        else:
                            input()  # Simple blocking input
                        
                        pygame.mixer.quit()
                        sys.exit(0)
                    
                    # Keys that should ONLY work when the animation is running
                    elif not self.paused:
                        if input_result.lower() == 'm':
                            self.toggle_background()
                        elif input_result.lower() == 'r':
                            self.generate_new_scene()
                        elif input_result.lower() == 'b':
                            random_x = random.randint(5, self.width - 5)
                            random_y = random.randint(5, self.height - 5)
                            self.create_bubble_burst(random_x, random_y)
                        elif input_result.lower() == 'f':
                            self.drop_food()
                if not self.paused:
                    self.update()
                    self.time_step += 1
                    
                self.draw()
                time.sleep(FRAME_RATE)
        except KeyboardInterrupt:
            if self.sound_on and self.sound:
                self.sound.stop()
            pygame.mixer.quit()
            print(f"{Style.RESET_ALL}\nThanks for visiting the aquarium!")
            print("Press any key to close the terminal...")
            
            # Restore terminal settings
            self.input_handler.cleanup()
            
            # Wait for user input
            if sys.platform == "win32":
                import msvcrt
                msvcrt.getch()
            else:
                input()
            
            pygame.mixer.quit()
            sys.exit(0)

    def update(self):
        """Updates the state of all objects in the aquarium."""
        self.food_pellets = [p for p in self.food_pellets if p.update()]

        if self.food_notice_timer > 0:
            self.food_notice_timer -= FRAME_RATE
            if self.food_notice_timer <= 0 and self.food_pellets:
                self._notify_fish_of_food()

        for fish in self.fishes:
            fish.update()
        for school in self.schools:
            school.update()
        for bubble in self.bubbles:
            bubble.update()
        
        # Update click bubbles and remove expired ones
        self.click_bubbles = [bubble for bubble in self.click_bubbles if bubble.update()]
        
        for jelly in self.jellyfishes: 
            jelly.update()
        if self.crab:
            self.crab.update()            
        
        if self.shark and self.shark.is_active():
            self.shark.update()
        elif self.shark and not self.shark.is_active():
            self.shark = None
        
        if self.shark_will_spawn and not self.shark:
            self.shark_spawn_timer -= 1 # Countdown each frame
            if self.shark_spawn_timer <= 0:
                self.play_shark_sound()
                self.shark = Shark(self.width, self.height, self.current_background, self)
                self.shark_will_spawn = False # Ensure it only spawns once per scene

    def _notify_fish_of_food(self):
        """Finds all fish within a radius of the food and tells them to seek it."""
        if not self.food_pellets or not self.fishes:
            return

        pellet = self.food_pellets[0]
        
        for fish in self.fishes:
            if isinstance(fish, (PufferFish, BabySeahorse, Seahorse)): continue
            
            dist = math.sqrt((fish.x - pellet.x)**2 + (fish.y - pellet.y)**2)
            if dist < FOOD_NOTICE_RADIUS:
                fish.seek_food(pellet)

    def draw_help_screen(self, buffer):
        """Draws a help menu overlay onto the buffer."""
        help_text = [
            "╔══════════════════════════════╗",
            "║       AQUARIUM CONTROLS      ║",
            "╠══════════════════════════════╣",
            "║                              ║",
            "║   M - Toggle Day/Night Mode  ║",
            "║   R - Randomize New Scene    ║",
            "║   B - Create Bubble Burst    ║",
            "║   F - Drop Food Pellet       ║",
            "║   S - Toggle Sound On/Off    ║",
            "║   H - Toggle This Help Menu  ║",
            "║                              ║",
            "║    ESC/Q - Exit Aquarium     ║",
            "║                              ║",
            "╚══════════════════════════════╝",
        ]

        box_width = len(help_text[0])
        box_height = len(help_text)
        start_x = (self.width - box_width) // 2
        start_y = (self.height - box_height) // 2

        if start_x < 0 or start_y < 0: return # Failsafe for tiny terminals

        # Draw the solid background box
        for y in range(start_y, start_y + box_height):
            if 0 <= y < self.height:
                for x in range(start_x, start_x + box_width):
                    if 0 <= x < self.width:
                        buffer[y][x] = (' ', Back.BLUE)

        # Draw the text on top of the box
        for y_offset, line in enumerate(help_text):
            y = start_y + y_offset
            if 0 <= y < self.height:
                for x_offset, char in enumerate(line):
                    x = start_x + x_offset
                    if 0 <= x < self.width:
                        buffer[y][x] = (char, Fore.LIGHTYELLOW_EX + Back.BLUE)

    def draw(self):
        """Draws the entire scene to the terminal."""
        buffer = [[(' ', Fore.RESET) for _ in range(self.width)] for _ in range(self.height)]

        # 1. Draw Seaweed
        for seaweed in self.seaweeds:
            seaweed.draw(buffer, self.time_step)

        # 2. Draw Decorations
        for decoration in self.decorations:
            decoration.draw(buffer)

        # 3. Draw Bubbles (regular)
        for bubble in self.bubbles:
            bubble.draw(buffer)

        # 3b. Draw Click Bubbles (temporary)
        for bubble in self.click_bubbles:
            bubble.draw(buffer)

        for pellet in self.food_pellets: pellet.draw(buffer)

        # 4. Draw Jellyfish
        for jelly in self.jellyfishes:
            jelly.draw(buffer, self.current_background)

        # 5. Draw Schools
        for school in self.schools:
            school.draw(buffer)

        # 6. Draw Fish
        for fish in self.fishes:
            fish.draw(buffer)
        
        if self.shark and self.shark.is_active():
            self.shark.draw(buffer)

        # 7. Draw Crab (on seafloor, before ocean floor)
        if self.crab:
            self.crab.draw(buffer)

        # 8. Draw the ocean floor
        """floor_y = self.height - 1
        if 0 <= floor_y < self.height:
            for i in range(self.width):
                buffer[floor_y][i] = ('~', Fore.YELLOW)"""
        self.floor.draw(buffer)

        if self.paused:
            self.draw_help_screen(buffer)

        # Render the buffer to a single string
        output_lines = []
        for y in range(self.height):
            line_str = ""
            current_color = None
            for x in range(self.width):
                char, color = buffer[y][x]
                if color != current_color:
                    line_str += color
                    current_color = color
                line_str += char
            output_lines.append(line_str)
        final_output = "\n".join(output_lines)

        # Print the final frame
        clear_and_draw_command = f"{self.current_background}\033[2J\033[H{final_output}"
        sys.stdout.write(clear_and_draw_command)
        sys.stdout.flush()


if __name__ == "__main__":
    aquarium = Aquarium()
    aquarium.run()