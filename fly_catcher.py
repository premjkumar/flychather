import pygame
import random
import sys
import os

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

# Load images (using placeholders since we can't download from internet)
# In a real implementation, you would load actual fly images
def create_fly_image(color=(255, 255, 0), size=30):
    """Create a simple fly image using pygame"""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surface, color, (size//2, size//2), size//2)
    pygame.draw.circle(surface, BLACK, (size//2, size//2), size//4)
    return surface

def create_dead_fly_image():
    """Create a simple dead fly image"""
    surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(surface, (150, 75, 0), (15, 15), 15)
    pygame.draw.circle(surface, BLACK, (15, 15), 7)
    return surface

# Fly class
class Fly:
    def __init__(self):
        self.alive = True
        self.x = random.randint(50, SCREEN_WIDTH - 50)
        self.y = random.randint(50, SCREEN_HEIGHT - 50)
        self.speed_x = random.choice([-3, -2, -1, 1, 2, 3])
        self.speed_y = random.choice([-3, -2, -1, 1, 2, 3])
        self.image = create_fly_image()
        self.dead_image = create_dead_fly_image()
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
