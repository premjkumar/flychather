import pygame
import random
import sys
import os
import glob
import math

# Initialize pygame
pygame.init()

# Screen dimensions
infoObject = pygame.display.Info()
SCREEN_WIDTH = infoObject.current_w if infoObject.current_w > 0 else 800
SCREEN_HEIGHT = infoObject.current_h if infoObject.current_h > 0 else 600

# Set screen mode (supports desktop and mobile scaling)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fly Catcher - Deluxe Edition")

# Colors
BG_COLOR = (240, 248, 255)       # Alice Blue
HUD_COLOR = (40, 44, 52)         # Dark slate
HUD_TEXT = (255, 255, 255)       # White
ACCENT_GREEN = (46, 204, 113)
ACCENT_RED = (231, 76, 60)
ACCENT_GOLD = (241, 196, 15)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Possible directories containing fly images
POSSIBLE_DIRS = [
    os.path.join(os.getcwd(), "assets"),
    os.path.join(os.getcwd()),
    "/home/sharon/downloads"
]

def load_fly_status_images(size=(45, 45)):
    """
    Search directories for images starting with fly_* 
    and return images for different fly statuses.
    """
    fly_images = {}
    
    for dir_path in POSSIBLE_DIRS:
        if os.path.exists(dir_path):
            pattern = os.path.join(dir_path, "fly_*")
            matching_files = glob.glob(pattern)
            
            for filepath in matching_files:
                filename = os.path.basename(filepath).lower()
                name_part = os.path.splitext(filename)[0]
                status_key = name_part.replace("fly_", "", 1)
                
                if status_key not in fly_images:
                    try:
                        img = pygame.image.load(filepath).convert_alpha()
                        img = pygame.transform.scale(img, size)
                        fly_images[status_key] = img
                    except Exception as e:
                        print(f"Could not load image {filepath}: {e}")

    return fly_images

LOADED_IMAGES = load_fly_status_images(size=(45, 45))

def get_fly_image(status):
    """Retrieve status image by key or fallback to procedural graphics"""
    if status in LOADED_IMAGES:
        return LOADED_IMAGES[status]
    
    for key in LOADED_IMAGES:
        if status in key:
            return LOADED_IMAGES[key]
            
    return None

def draw_procedural_fly(color=(40, 40, 40), size=45, wing_angle=0):
    """Fallback drawing function if image files are missing"""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    
    # Wings
    wing_offset = math.sin(wing_angle) * 6
    pygame.draw.ellipse(surface, (200, 230, 255, 180), (cx - 14, cy - 12 + wing_offset, 12, 18))
    pygame.draw.ellipse(surface, (200, 230, 255, 180), (cx + 2, cy - 12 - wing_offset, 12, 18))
    
    # Body & Head
    pygame.draw.ellipse(surface, color, (cx - 8, cy - 10, 16, 20))
    pygame.draw.circle(surface, (180, 0, 0), (cx - 4, cy - 8), 3)  # Left eye
    pygame.draw.circle(surface, (180, 0, 0), (cx + 4, cy - 8), 3)  # Right eye
    
    return surface

def draw_procedural_splat(size=45):
    """Fallback splat effect"""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    pygame.draw.circle(surface, (100, 50, 0, 200), (cx, cy), size // 3)
    for _ in range(6):
        ox = random.randint(-15, 15)
        oy = random.randint(-15, 15)
        pygame.draw.circle(surface, (120, 60, 0, 180), (cx + ox, cy + oy), random.randint(3, 7))
    return surface

# Particle effect for swatting
class SplatEffect:
    def __init__(self, x, y, text="+10", color=ACCENT_GREEN):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.alpha = 255
        self.lifetime = 30
        self.image = get_fly_image('splat') or draw_procedural_splat()
        
    def update(self):
        self.y -= 1
        self.lifetime -= 1
        self.alpha = max(0, int((self.lifetime / 30) * 255))
        
    def draw(self, surface, font):
        # Draw splat image
        splat_img = self.image.copy()
        splat_img.fill((255, 255, 255, self.alpha), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(splat_img, splat_img.get_rect(center=(self.x, self.y)))
        
        # Floating point popup
        txt_surf = font.render(self.text, True, self.color)
        txt_surf.set_alpha(self.alpha)
        surface.blit(txt_surf, (self.x - txt_surf.get_width() // 2, self.y - 30))

# Fly class with status support and animations
class Fly:
    def __init__(self, level=1):
        self.fly_type = random.choices(['normal', 'fast', 'gold'], weights=[70, 20, 10])[0]
        self.alive = True
        self.x = random.randint(60, SCREEN_WIDTH - 60)
        self.y = random.randint(100, SCREEN_HEIGHT - 60)
        
        # Base speed adjusted by level & fly type
        speed_mult = 1.0 + (level - 1) * 0.2
        if self.fly_type == 'fast':
            speed_mult *= 1.8
            self.points = 25
            self.color = (30, 144, 255)
        elif self.fly_type == 'gold':
            speed_mult *= 1.3
            self.points = 50
            self.color = ACCENT_GOLD
        else:
            self.points = 10
            self.color = (40, 40, 40)
            
        base_speed = random.uniform(2, 4) * speed_mult
        angle = random.uniform(0, 2 * math.pi)
        self.speed_x = math.cos(angle) * base_speed
        self.speed_y = math.sin(angle) * base_speed
        
        self.size = 45
        self.wing_angle = 0
        
        # Try status image or fallback
        self.image = get_fly_image(self.fly_type) or get_fly_image('alive')
        self.dead_image = get_fly_image('dead') or get_fly_image('splat')
        
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.rect.center = (self.x, self.y)
        
    def update(self):
        if not self.alive:
            return
            
        self.wing_angle += 0.5
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Bounce off edges (considering HUD height at top = 60)
        if self.x <= 25 or self.x >= SCREEN_WIDTH - 25:
            self.speed_x *= -1
        if self.y <= 85 or self.y >= SCREEN_HEIGHT - 25:
            self.speed_y *= -1
            
        # Subtle erratic movements
        if random.random() < 0.05:
            self.speed_x += random.uniform(-0.5, 0.5)
            self.speed_y += random.uniform(-0.5, 0.5)
            
        self.rect.center = (int(self.x), int(self.y))
    
    def draw(self, surface):
        if self.alive:
            if self.image:
                surface.blit(self.image, self.rect)
            else:
                procedural = draw_procedural_fly(self.color, self.size, self.wing_angle)
                surface.blit(procedural, self.rect)
        else:
            if self.dead_image:
                surface.blit(self.dead_image, self.rect)

    def is_clicked(self, pos):
        if self.alive and self.rect.collidepoint(pos):
            self.alive = False
            return True
        return False

# Game Controller Class
class FlyCatcherGame:
    def __init__(self):
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        pygame.mouse.set_visible(False)  # Hide default cursor for custom swatter
        self.last_touch_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.reset_game()
        
    def reset_game(self):
        self.flies = []
        self.effects = []
        self.score = 0
        self.level = 1
        self.time_left = 30  # 30-second round
        self.spawn_timer = 0
        self.spawn_interval = 40  # Frames between spawns
        self.game_over = False
        self.swatter_angle = 0
        
    def spawn_fly(self):
        if len(self.flies) < 12:  # Cap max flies on screen
            self.flies.append(Fly(self.level))
        
    def update(self, delta_time):
        if self.game_over:
            return

        # Timer countdown
        self.time_left -= delta_time
        if self.time_left <= 0:
            self.time_left = 0
            self.game_over = True
            
        # Level progression every 100 points
        self.level = 1 + (self.score // 100)
        self.spawn_interval = max(15, 45 - (self.level * 3))

        # Spawn flies
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_fly()
            
        # Update flies
        for fly in self.flies:
            fly.update()

        # Update splat effects
        for effect in self.effects[:]:
            effect.update()
            if effect.lifetime <= 0:
                self.effects.remove(effect)

    def handle_click(self, pos):
        self.last_touch_pos = pos
        if self.game_over:
            self.reset_game()
            return
            
        self.swatter_angle = -25  # Swat animation tilt
        hit = False
        
        for fly in reversed(self.flies):  # Check topmost fly first
            if fly.is_clicked(pos):
                self.score += fly.points
                self.effects.append(SplatEffect(fly.x, fly.y, f"+{fly.points}", ACCENT_GREEN))
                self.flies.remove(fly)
                hit = True
                break
                
        if not hit:
            # Clicked empty space
            self.effects.append(SplatEffect(pos[0], pos[1], "Miss!", ACCENT_RED))

    def draw_hud(self, surface):
        # Draw top HUD bar
        pygame.draw.rect(surface, HUD_COLOR, (0, 0, SCREEN_WIDTH, 60))
        pygame.draw.line(surface, ACCENT_GREEN, (0, 60), (SCREEN_WIDTH, 60), 3)

        # Score
        score_surf = self.font_medium.render(f"Score: {self.score}", True, HUD_TEXT)
        surface.blit(score_surf, (20, 18))

        # Level
        level_surf = self.font_medium.render(f"Level: {self.level}", True, ACCENT_GOLD)
        surface.blit(level_surf, (SCREEN_WIDTH // 2 - level_surf.get_width() // 2, 18))

        # Timer
        time_color = ACCENT_RED if self.time_left < 6 else HUD_TEXT
        timer_surf = self.font_medium.render(f"Time: {int(self.time_left)}s", True, time_color)
        surface.blit(timer_surf, (SCREEN_WIDTH - 140, 18))

    def draw_swatter_cursor(self, surface, pos):
        """Draw interactive Fly Swatter cursor"""
        cx, cy = pos
        # Animate tilt bounce back
        if self.swatter_angle < 0:
            self.swatter_angle += 5

        # Handle
        pygame.draw.line(surface, (120, 80, 40), (cx, cy), (cx + 20, cy + 35), 5)
        # Mesh head
        swat_surf = pygame.Surface((30, 35), pygame.SRCALPHA)
        pygame.draw.rect(swat_surf, (200, 50, 50, 180), (0, 0, 30, 35), border_radius=4)
        pygame.draw.rect(swat_surf, BLACK, (0, 0, 30, 35), 2, border_radius=4)
        
        # Grid pattern
        for x in range(5, 30, 6):
            pygame.draw.line(swat_surf, BLACK, (x, 0), (x, 35), 1)
        for y in range(5, 35, 6):
            pygame.draw.line(swat_surf, BLACK, (0, y), (30, y), 1)

        rotated_swat = pygame.transform.rotate(swat_surf, self.swatter_angle)
        surface.blit(rotated_swat, (cx - 15, cy - 35))

    def draw(self, surface):
        surface.fill(BG_COLOR)

        # Draw flies
        for fly in self.flies:
            fly.draw(surface)

        # Draw swat effects & score popups
        for effect in self.effects:
            effect.draw(surface, self.font_small)

        # Draw HUD
        self.draw_hud(surface)

        # Draw Game Over Overlay
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))

            go_title = self.font_large.render("TIME'S UP!", True, ACCENT_RED)
            final_score = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
            restart_msg = self.font_medium.render("Tap Screen or Press 'R' to Restart", True, ACCENT_GREEN)

            surface.blit(go_title, (SCREEN_WIDTH // 2 - go_title.get_width() // 2, 200))
            surface.blit(final_score, (SCREEN_WIDTH // 2 - final_score.get_width() // 2, 270))
            surface.blit(restart_msg, (SCREEN_WIDTH // 2 - restart_msg.get_width() // 2, 330))

        # Draw cursor swatter
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos == (0, 0):
            mouse_pos = self.last_touch_pos
        self.draw_swatter_cursor(surface, mouse_pos)

# Main game loop
def main():
    clock = pygame.time.Clock()
    game = FlyCatcherGame()
    
    running = True
    while running:
        delta_time = clock.tick(60) / 1000.0  # seconds passed per frame
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click or touch
                    game.handle_click(pygame.mouse.get_pos())
            elif event.type == pygame.FINGERDOWN:
                touch_pos = (int(event.x * SCREEN_WIDTH), int(event.y * SCREEN_HEIGHT))
                game.handle_click(touch_pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game.game_over:
                    game.reset_game()

        # Update game logic
        game.update(delta_time)
        
        # Render frame
        game.draw(screen)
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
