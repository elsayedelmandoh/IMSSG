import pygame
import random
import sys
import os
from pygame.locals import *

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Setup fullscreen
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), FULLSCREEN)
pygame.display.set_caption("Catch the Falling Stars - Bomb Edition")

# Constants
FPS = 60
PLAYER_SIZE = 40  
STAR_SIZE = 30
BOMB_SIZE = 40
PARTICLE_COUNT = 50
HIGHSCORE_FILE = "highscore.txt"

# Load high score
if os.path.exists(HIGHSCORE_FILE):
    with open(HIGHSCORE_FILE, "r") as f:
        try:
            highscore = int(f.read())
        except:
            highscore = 0
else:
    highscore = 0

# Power-up states
shield_active = False
slow_time_active = False
slow_time_duration = 0

# Power-up counts
shield_count = 0
slow_time_count = 0

# Game objects
player = pygame.Rect(WIDTH//2, HEIGHT-100, PLAYER_SIZE, PLAYER_SIZE)
stars = []
bombs = []
particles = []
clock = pygame.time.Clock()
font_large = pygame.font.SysFont("Arial", 48, bold=True)
font_medium = pygame.font.SysFont("Arial", 36)
font_small = pygame.font.SysFont("Arial", 24)

# Create falling objects
def create_star():
    x = random.randint(0, WIDTH - STAR_SIZE)
    color = random.choice([(255, 255, 0), (255, 255, 255)])
    base_speed = 3 + min(score / 100, 12)
    return {
        "rect": pygame.Rect(x, -STAR_SIZE, STAR_SIZE, STAR_SIZE),
        "color": color,
        "speed": random.uniform(base_speed, base_speed + 2),
        "type": "star"
    }

def create_bomb():
    x = random.randint(0, WIDTH - BOMB_SIZE)
    base_speed = 4 + min(score / 80, 16)
    return {
        "rect": pygame.Rect(x, -BOMB_SIZE, BOMB_SIZE, BOMB_SIZE),
        "color": (255, 0, 0),
        "speed": random.uniform(base_speed, base_speed + 2),
        "type": "bomb"
    }

def create_explosion(pos):
    for _ in range(PARTICLE_COUNT * 3):
        particles.append({
            "pos": [pos[0], pos[1]],
            "color": random.choice([(255, 0, 0), (255, 255, 255)]),
            "size": random.randint(3, 8),
            "speed": [random.uniform(-5, 5), random.uniform(-10, 2)],
            "life": random.randint(20, 40)
        })

# Game state
score = 0
missed = 0
game_over = False
running = True
in_menu = True  # Start in menu state

def reset_game():
    global score, missed, game_over, shield_active, slow_time_active, shield_count, slow_time_count
    score = 0
    missed = 0
    game_over = False
    shield_active = False
    slow_time_active = False
    shield_count = 0
    slow_time_count = 0
    stars.clear()
    bombs.clear()
    particles.clear()

def draw_menu():
    screen.fill((0, 0, 20))
    title = font_large.render("Catch the Falling Stars", True, (255, 255, 255))
    subtitle = font_medium.render("Bomb Edition", True, (255, 0, 0))
    start = font_medium.render("Press SPACE to Start", True, (255, 255, 255))
    controls = font_small.render("Controls: Mouse to move, S for Shield, T for Slow Time", True, (200, 200, 200))
    
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//2 - 40))
    screen.blit(start, (WIDTH//2 - start.get_width()//2, HEIGHT//2 + 40))
    screen.blit(controls, (WIDTH//2 - controls.get_width()//2, HEIGHT//2 + 100))
    pygame.display.flip()

# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            running = False
        
        if in_menu and event.type == KEYDOWN and event.key == K_SPACE:
            in_menu = False
            reset_game()
            
        if game_over and event.type == KEYDOWN:
            if event.key == K_r:
                reset_game()
            if event.key == K_m:
                in_menu = True

        # Activate shield (S key)
        if not in_menu and event.type == KEYDOWN and event.key == K_s:
            if shield_count > 0 and not shield_active:
                shield_active = True
                shield_count -= 1

        # Activate slow time (T key)
        if not in_menu and event.type == KEYDOWN and event.key == K_t:
            if slow_time_count > 0 and not slow_time_active:
                slow_time_active = True
                slow_time_duration = 180
                slow_time_count -= 1

    if in_menu:
        draw_menu()
        clock.tick(FPS)
        continue

    if not game_over:
        # Gameplay logic
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player.center = (mouse_x, mouse_y)

        # Keep player on screen
        player.left = max(0, player.left)
        player.right = min(WIDTH, player.right)
        player.top = max(0, player.top)
        player.bottom = min(HEIGHT, player.bottom)

        # Spawn stars and bombs
        star_spawn_chance = 0.03 + min(score / 2000, 0.07)
        bomb_spawn_chance = 0.005 + min(score / 4000, 0.02)

        if random.random() < star_spawn_chance:
            stars.append(create_star())
            # 10% chance to get a power-up when a star spawns
            if random.random() < 0.1:
                if random.choice([True, False]):
                    shield_count += 1
                else:
                    slow_time_count += 1

        if random.random() < bomb_spawn_chance:
            bombs.append(create_bomb())

        # Update stars
        for star in stars[:]:
            star["rect"].y += star["speed"] * (0.5 if slow_time_active else 1.0)
            if star["rect"].colliderect(player):
                create_explosion(star["rect"].center)
                stars.remove(star)
                score += 10
            elif star["rect"].top > HEIGHT:
                stars.remove(star)
                missed += 1

        # Update bombs
        for bomb in bombs[:]:
            bomb["rect"].y += bomb["speed"] * (0.5 if slow_time_active else 1.0)
            if bomb["rect"].colliderect(player):
                if not shield_active:
                    create_explosion(bomb["rect"].center)
                    bombs.remove(bomb)
                    game_over = True
                else:
                    bombs.remove(bomb)
                    shield_active = False
            elif bomb["rect"].top > HEIGHT:
                bombs.remove(bomb)

        # Update slow time
        if slow_time_active:
            slow_time_duration -= 1
            if slow_time_duration <= 0:
                slow_time_active = False

    # Update particles
    for particle in particles[:]:
        particle["pos"][0] += particle["speed"][0]
        particle["pos"][1] += particle["speed"][1]
        particle["life"] -= 1
        if particle["life"] <= 0:
            particles.remove(particle)

    # Drawing
    screen.fill((0, 0, 20))  # Dark background

    # Draw particles
    for particle in particles:
        pygame.draw.circle(screen, particle["color"], 
                          [int(particle["pos"][0]), int(particle["pos"][1])], 
                          particle["size"])

    # Draw stars and bombs
    for star in stars:
        pygame.draw.rect(screen, star["color"], star["rect"])
    for bomb in bombs:
        pygame.draw.rect(screen, bomb["color"], bomb["rect"])

    # Draw player if not in menu or game over
    if not game_over:
        pygame.draw.rect(screen, (0, 255, 255), player, border_radius=5)

    # Draw UI
    score_text = font_medium.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (20, 20))

    highscore_text = font_small.render(f"High Score: {highscore}", True, (255, 255, 255))
    screen.blit(highscore_text, (20, 60))

    # Draw power-up indicators
    shield_icon = font_small.render(f"Shields: {shield_count}", True, (0, 255, 0))
    slow_icon = font_small.render(f"Slow Time: {slow_time_count}", True, (255, 255, 0))
    screen.blit(shield_icon, (20, 100))
    screen.blit(slow_icon, (20, 130))

    if shield_active:
        active_text = font_small.render("SHIELD ACTIVE!", True, (0, 255, 0))
        screen.blit(active_text, (WIDTH//2 - active_text.get_width()//2, 20))

    if slow_time_active:
        active_text = font_small.render("SLOW TIME ACTIVE!", True, (255, 255, 0))
        screen.blit(active_text, (WIDTH//2 - active_text.get_width()//2, 50))

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        game_over_text = font_large.render("GAME OVER!", True, (255, 0, 0))
        final_score = font_medium.render(f"Final Score: {score}", True, (255, 255, 255))
        restart = font_small.render("Press R to restart or M for menu", True, (255, 255, 255))
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 60))
        screen.blit(final_score, (WIDTH//2 - final_score.get_width()//2, HEIGHT//2))
        screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 60))

    pygame.display.flip()
    clock.tick(FPS)

    # Update high score
    if score > highscore:
        highscore = score
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(highscore))

pygame.quit()
sys.exit()