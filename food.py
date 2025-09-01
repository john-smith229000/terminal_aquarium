import random
from colorama import Fore
from config import FRAME_RATE, FOOD_SINK_SPEED, FOOD_LIFETIME

class FoodPellet:
    """
    Represents a cluster of food particles falling from the top.
    While visually complex, it's treated as a single object by other classes.
    """
    def __init__(self, x, y, width, height):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        
        self.speed = FOOD_SINK_SPEED
        self.lifetime = FOOD_LIFETIME

        # Create a cluster of particles 
        self.particles = []
        num_particles = random.randint(15, 20)
        for _ in range(num_particles):
            particle = {
                'art': random.choice(['●', '•', '.','.','.','.','•','•','•','•','•','•','•','•','•']),
                'color': random.choice([Fore.RED, Fore.LIGHTRED_EX, Fore.MAGENTA, Fore.LIGHTMAGENTA_EX]),
                # Give each particle a slight, fixed offset from the center
                'x_offset': random.uniform(-3.5, 3.5),
                'y_offset': random.uniform(-2.5, 2.5)
            }
            self.particles.append(particle)

    def update(self):
        """Moves the pellet downwards with a slight wobble and ages it."""
        # Vertical movement
        self.y += self.speed
        
        # Add a gentle horizontal drift 
        self.x += random.uniform(-0.4, 0.4)

        self.lifetime -= FRAME_RATE
        # Return True if the pellet is still active
        return self.lifetime > 0 and self.y < self.height - 1

    def draw(self, buffer):
        """Draws each particle in the cluster onto the provided buffer."""
        # Loop through particles to draw the cluster
        for particle in self.particles:
            # Calculate the absolute position of each particle
            x = int(self.x + particle['x_offset'])
            y = int(self.y + particle['y_offset'])
            
            if 0 <= y < self.height and 0 <= x < self.width:
                buffer[y][x] = (particle['art'], particle['color'])

