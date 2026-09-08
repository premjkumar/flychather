import pygame
import random
import sys
import os
import glob

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fly Catcher")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Directory containing fly images
DOWNLOADS_DIR = "/home/sharon/downloads"

def load_fly_status_images(size=(40, 40)):
    """
    Search /home/sharon/downloads for images starting with fly_* 
    and return images for different fly statuses (alive, dead, etc.).
    """
    fly_images = {}
    
    if os.path.exists(DOWNLOADS_DIR):
        # Look for image files starting with fly_
        pattern = os.path.join(DOWNLOADS_DIR, "fly_*")
        matching_files = glob.glob(pattern)
        
        for filepath in matching_files:
            filename = os.path.basename(filepath).lower()
            # Extract status from filename (e.g., fly_alive.png -> alive, fly_dead.png -> dead)
            name_part = os.path.splitext(filename)[0]  # remove extension
            status_key = name_part.replace("fly_", "", 1)
            
            try:
                img = pygame.image.load(filepath).convert_alpha()
                img = pygame.transform.scale(img, size)
                fly_images[status_key] = img
            except Exception as e:
                print(f"Could not load image {filepath}: {e}")

    return fly_images

# Fallback shape generators if images are missing
def create_fallback_fly_image(color=(255, 255, 0), size=40):
    """Create a simple fly image using pygame drawing"""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surface, color, (size // 2, size // 2), size // 2)
    pygame.draw.circle(surface, BLACK, (size // 2, size // 2), size // 4)
    return surface

def create_fallback_dead_fly_image(size=40):
    """Create a simple dead fly image"""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surface, (150, 75, 0), (size // 2, size // 2), size // 2)
    pygame.draw.circle(surface, BLACK, (size // 2, size // 2), size // 4)
    return surface

# Preload loaded status images or create fallbacks
LOADED_IMAGES = load_fly_status_images(size=(40, 40))

def get_fly_image(status):
    """Retrieve status image by key (e.g. 'alive', 'dead') or fallback"""
    if status in LOADED_IMAGES:
        return LOADED_IMAGES[status]
    
    # Try finding matching key containing the status word
    for key in LOADED_IMAGES:
        if status in key:
            return LOADED_IMAGES[key]
            
    # Default fallbacks
    if status in ['alive', 'fly']:
        return create_fallback_fly_image()
    else:
        return create_fallback_dead_fly_image()

# Fly class
class Fly:
    def __init__(self):
        self.alive = True
        self.x = random.randint(50, SCREEN_WIDTH - 50)
        self.y = random.randint(50, SCREEN_HEIGHT - 50)
        self.speed_x = random.choice([-3, -2, -1, 1, 2, 3])
        self.speed_y = random.choice([-3, -2, -1, 1, 2, 3])
        
        # Load status images
        self.image = get_fly_image('alive')
        self.dead_image = get_fly_image('dead')
        
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.buzz_timer = 0
        self.buzz_interval = 30  # frames between buzzes
        
    def update(self):
        if not self.alive:
            return
            
        # Move the fly
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Bounce off walls
        if self.x <= 0 or self.x >= SCREEN_WIDTH:
            self.speed_x *= -1
        if self.y <= 0 or self.y >= SCREEN_HEIGHT:
            self.speed_y *= -1
            
        # Update rect position
        self.rect.center = (self.x, self.y)
        
        # Buzzing effect
        self.buzz_timer += 1
        if self.buzz_timer > self.buzz_interval:
            self.buzz_timer = 0
            # Randomly change direction slightly
            self.speed_x += random.uniform(-0.5, 0.5)
            self.speed_y += random.uniform(-0.5, 0.5)
            
            # Keep speed within reasonable bounds
            self.speed_x = max(-5, min(5, self.speed_x))
            self.speed_y = max(-5, min(5, self.speed_y))
    
    def draw(self, surface):
        if self.alive:
            surface.blit(self.image, self.rect)
        else:
            surface.blit(self.dead_image, self.rect)
    
    def is_clicked(self, pos):
        if self.alive and self.rect.collidepoint(pos):
            self.alive = False
            return True
        return False

# Game class
class FlyCatcherGame:
    def __init__(self):
        self.flies = []
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.spawn_timer = 0
        self.spawn_interval = 60  # frames between spawns
        
    def spawn_fly(self):
        self.flies.append(Fly())
        
    def update(self):
        # Spawn new flies
        self.spawn_timer += 1
        if self.spawn_timer > self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_fly()
            
        # Update all flies
        for fly in self.flies[:]:
            fly.update()
            # Remove dead flies that are off-screen
            if not fly.alive and (fly.x < -50 or fly.x > SCREEN_WIDTH + 50 or 
                                 fly.y < -50 or fly.y > SCREEN_HEIGHT + 50):
                self.flies.remove(fly)
    
    def draw(self, surface):
        # Draw background
        surface.fill(WHITE)
        
        # Draw all flies
        for fly in self.flies:
            fly.draw(surface)
            
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        surface.blit(score_text, (10, 10))
        
        # Draw instructions
        instructions = self.font.render("Tap on flies to catch them!", True, BLACK)
        surface.blit(instructions, (SCREEN_WIDTH//2 - instructions.get_width()//2, 10))

# Main game loop
def main():
    clock = pygame.time.Clock()
    game = FlyCatcherGame()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if any fly was clicked
                pos = pygame.mouse.get_pos()
                for fly in game.flies[:]:
                    if fly.is_clicked(pos):
                        game.score += 10
                        break
        
        # Update game state
        game.update()
        
        # Draw everything
        game.draw(screen)
        
        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
