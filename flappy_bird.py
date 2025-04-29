import pygame
import random
import sys
import json
from pygame import gfxdraw

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Game constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.25
FLAP_STRENGTH = -7
BASE_PIPE_SPEED = 3
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # milliseconds
DIFFICULTY_INCREASE = 0.1  # Speed increase per point

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)
GROUND_COLOR = (139, 69, 19)
PIPE_COLOR = (0, 160, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# High score system
def load_high_score():
    try:
        with open("highscore.json", "r") as f:
            return json.load(f).get("high_score", 0)
    except:
        return 0

def save_high_score(score):
    with open("highscore.json", "w") as f:
        json.dump({"high_score": score}, f)

high_score = load_high_score()

class Bird:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.radius = 15
        self.animation_state = 0  # For wing flapping
        self.animation_counter = 0
        
    def flap(self):
        self.velocity = FLAP_STRENGTH
        
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Wing animation
        self.animation_counter += 1
        if self.animation_counter >= 10:
            self.animation_counter = 0
            self.animation_state = (self.animation_state + 1) % 3
        
    def draw(self):
        # Body
        pygame.draw.circle(screen, YELLOW, (self.x, int(self.y)), self.radius)
        
        # Eye
        pygame.draw.circle(screen, BLACK, (self.x + 8, int(self.y) - 5), 3)
        
        # Beak (changes with velocity)
        beak_length = 15 + abs(self.velocity)
        beak_points = [
            (self.x + self.radius, self.y),
            (self.x + self.radius + beak_length, self.y - 5),
            (self.x + self.radius + beak_length, self.y + 5)
        ]
        pygame.draw.polygon(screen, (255, 165, 0), beak_points)
        
        # Wings (animated)
        wing_y_offset = [0, -5, 0][self.animation_state]  # Different positions for animation
        wing_points = [
            (self.x - 10, self.y + wing_y_offset),
            (self.x - 20, self.y - 10 + wing_y_offset),
            (self.x - 15, self.y + wing_y_offset)
        ]
        pygame.draw.polygon(screen, YELLOW, wing_points)
        
    def check_collision(self, pipes):
        # Check if bird hits ground or ceiling
        if self.y <= 0 or self.y >= SCREEN_HEIGHT - GROUND_HEIGHT:
            return True
            
        # Check pipe collisions
        for pipe in pipes:
            if (self.x + self.radius > pipe.x and self.x - self.radius < pipe.x + pipe.width):
                if self.y - self.radius < pipe.top_height or self.y + self.radius > pipe.top_height + PIPE_GAP:
                    return True
        return False

class Pipe:
    def __init__(self, speed):
        self.x = SCREEN_WIDTH
        self.width = 60
        self.top_height = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 100)
        self.passed = False
        self.speed = speed
        
    def update(self):
        self.x -= self.speed
        
    def draw(self):
        # Top pipe
        pygame.draw.rect(screen, PIPE_COLOR, (self.x, 0, self.width, self.top_height))
        # Add pipe rim
        pygame.draw.rect(screen, GREEN, (self.x - 3, self.top_height - 20, self.width + 6, 20))
        
        # Bottom pipe
        bottom_pipe_top = self.top_height + PIPE_GAP
        pygame.draw.rect(screen, PIPE_COLOR, (self.x, bottom_pipe_top, self.width, SCREEN_HEIGHT - bottom_pipe_top))
        # Add pipe rim
        pygame.draw.rect(screen, GREEN, (self.x - 3, bottom_pipe_top, self.width + 6, 20))
        
    def is_off_screen(self):
        return self.x + self.width < 0

# Ground dimensions
GROUND_HEIGHT = 50

def draw_ground():
    pygame.draw.rect(screen, GROUND_COLOR, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
    # Draw some grass on top
    for x in range(0, SCREEN_WIDTH, 5):
        height = random.randint(1, 5)
        pygame.draw.line(screen, (0, 150, 0), 
                        (x, SCREEN_HEIGHT - GROUND_HEIGHT),
                        (x, SCREEN_HEIGHT - GROUND_HEIGHT - height), 2)

def draw_clouds():
    for i in range(3):
        x = (pygame.time.get_ticks() // 20 + i * 200) % (SCREEN_WIDTH + 100) - 50
        y = 50 + i * 80
        pygame.draw.ellipse(screen, WHITE, (x, y, 60, 40))
        pygame.draw.ellipse(screen, WHITE, (x + 30, y - 10, 60, 40))
        pygame.draw.ellipse(screen, WHITE, (x + 60, y, 60, 40))

def show_start_screen():
    font_large = pygame.font.SysFont('Arial', 50, bold=True)
    font_small = pygame.font.SysFont('Arial', 30)
    
    title = font_large.render("FLAPPY BIRD", True, BLACK)
    instruction = font_small.render("Press SPACE to start", True, BLACK)
    quit_text = font_small.render("Q to quit", True, BLACK)
    
    screen.fill(SKY_BLUE)
    draw_clouds()
    draw_ground()
    
    # Draw title with shadow
    pygame.draw.rect(screen, (200, 200, 200), (SCREEN_WIDTH//2 - title.get_width()//2 - 5, 145, title.get_width() + 10, title.get_height() + 10), border_radius=5)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
    
    # Draw instruction box
    pygame.draw.rect(screen, (200, 200, 200), (SCREEN_WIDTH//2 - instruction.get_width()//2 - 10, 245, instruction.get_width() + 20, instruction.get_height() + 10), border_radius=5)
    screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, 250))
    
    # Draw quit box
    pygame.draw.rect(screen, (200, 200, 200), (SCREEN_WIDTH//2 - quit_text.get_width()//2 - 10, 295, quit_text.get_width() + 20, quit_text.get_height() + 10), border_radius=5)
    screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, 300))
    
    # Draw example bird
    example_bird = Bird()
    example_bird.x = SCREEN_WIDTH // 2
    example_bird.y = 400
    example_bird.draw()
    
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        clock.tick(60)

def main():
    global high_score
    
    show_start_screen()
    
    bird = Bird()
    pipes = []
    last_pipe = pygame.time.get_ticks()
    score = 0
    font = pygame.font.SysFont('Arial', 30, bold=True)
    game_active = True
    current_pipe_speed = BASE_PIPE_SPEED
    
    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_active:
                    bird.flap()
                if event.key == pygame.K_SPACE and not game_active:
                    # Reset game
                    bird = Bird()
                    pipes = []
                    score = 0
                    game_active = True
                    current_pipe_speed = BASE_PIPE_SPEED
                    last_pipe = pygame.time.get_ticks()
                if event.key == pygame.K_r and not game_active:
                    # Reset game
                    bird = Bird()
                    pipes = []
                    score = 0
                    game_active = True
                    current_pipe_speed = BASE_PIPE_SPEED
                    last_pipe = pygame.time.get_ticks()
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        
        # Clear screen
        screen.fill(SKY_BLUE)
        draw_clouds()
        
        if game_active:
            # Bird update
            bird.update()
            
            # Generate pipes
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > PIPE_FREQUENCY:
                pipes.append(Pipe(current_pipe_speed))
                last_pipe = time_now
                
            # Pipe update
            for pipe in pipes:
                pipe.update()
                
                # Score increment
                if not pipe.passed and pipe.x + pipe.width < bird.x:
                    pipe.passed = True
                    score += 1
                    # Increase difficulty
                    current_pipe_speed += DIFFICULTY_INCREASE
                    
                # Remove off-screen pipes
                if pipe.is_off_screen():
                    pipes.remove(pipe)
            
            # Collision check
            if bird.check_collision(pipes):
                game_active = False
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
            
            # Draw pipes
            for pipe in pipes:
                pipe.draw()
            
            # Draw bird
            bird.draw()
            
            # Draw ground
            draw_ground()
            
            # Draw score with background
            score_surface = font.render(f"{score}", True, WHITE)
            pygame.draw.rect(screen, (0, 0, 0, 128), (SCREEN_WIDTH//2 - score_surface.get_width()//2 - 10, 10, 
                                                     score_surface.get_width() + 20, score_surface.get_height() + 10), 
                                                     border_radius=5)
            screen.blit(score_surface, (SCREEN_WIDTH//2 - score_surface.get_width()//2, 15))
            
        else:
            # Game over screen
            game_over_text = font.render("GAME OVER", True, BLACK)
            score_text = font.render(f"Score: {score}", True, BLACK)
            high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
            restart_text = font.render("Press SPACE or R to restart", True, BLACK)
            quit_text = font.render("Q to quit", True, BLACK)
            
            # Draw semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((200, 200, 200, 200))
            screen.blit(overlay, (0, 0))
            
            # Draw game over box
            box_height = 300
            pygame.draw.rect(screen, (240, 240, 240), (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - box_height//2, 300, box_height), border_radius=10)
            pygame.draw.rect(screen, (180, 180, 180), (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - box_height//2, 300, box_height), 3, border_radius=10)
            
            # Draw texts
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 120))
            screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
            screen.blit(high_score_text, (SCREEN_WIDTH//2 - high_score_text.get_width()//2, SCREEN_HEIGHT//2 - 20))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 40))
            screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, SCREEN_HEIGHT//2 + 80))
            
            # Draw dead bird
            dead_bird = Bird()
            dead_bird.x = SCREEN_WIDTH // 2
            dead_bird.y = SCREEN_HEIGHT // 2 + 120
            dead_bird.velocity = 0
            dead_bird.draw()
        
        # Update display
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()