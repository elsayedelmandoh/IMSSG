import pygame
import random
import sys
import os

pygame.init()

# Screen setup (fullscreen)
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Catch the Falling Stars - Bomb Edition")

clock = pygame.time.Clock()
FPS = 60

# Colors
COLOR_BG = (5, 5, 25)
COLOR_PLAYER = (0, 230, 255)
COLOR_STAR_YELLOW = (255, 255, 100)
COLOR_STAR_WHITE = (255, 255, 255)
COLOR_BOMB = (255, 50, 50)
COLOR_SHIELD = (50, 255, 50)
COLOR_TEXT = (255, 255, 255)
COLOR_TEXT_ALERT = (255, 100, 100)
COLOR_PARTICLE_RED = (255, 80, 80)
COLOR_PARTICLE_WHITE = (255, 255, 255)

PLAYER_SIZE = 50
STAR_SIZE = 30
BOMB_SIZE = 40
PARTICLE_COUNT = 40
HIGHSCORE_FILE = "highscore.txt"

# Fonts
font_large = pygame.font.SysFont("Arial", 64, bold=True)
font_medium = pygame.font.SysFont("Arial", 36)
font_small = pygame.font.SysFont("Arial", 24)

# Load highscore
def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read())
        except:
            return 0
    else:
        return 0

def save_highscore(score):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))
    except:
        pass

highscore = load_highscore()

# Classes
class Particle:
    def __init__(self, pos):
        self.pos = [pos[0], pos[1]]
        self.radius = random.randint(4, 7)
        self.color = random.choice([COLOR_PARTICLE_RED, COLOR_PARTICLE_WHITE])
        self.vel = [random.uniform(-4, 4), random.uniform(-8, -2)]
        self.life = random.randint(20, 40)

    def update(self):
        self.vel[1] += 0.3  # gravity
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.life -= 1
        self.radius = max(0, self.radius - 0.15)

    def draw(self, surf):
        if self.radius > 0:
            pygame.draw.circle(surf, self.color, (int(self.pos[0]), int(self.pos[1])), int(self.radius))

class FallingObject:
    def __init__(self, x, y, size, speed, kind):
        self.rect = pygame.Rect(x, y, size, size)
        self.speed = speed
        self.kind = kind  # "star" or "bomb"
        self.color = COLOR_STAR_YELLOW if kind == "star" else COLOR_BOMB
        if kind == "star" and random.random() < 0.5:
            self.color = COLOR_STAR_WHITE

    def update(self, slow_time):
        self.rect.y += self.speed * (0.5 if slow_time else 1)

    def draw(self, surf):
        if self.kind == "star":
            pygame.draw.rect(surf, self.color, self.rect, border_radius=6)
        else:
            center = self.rect.center
            pygame.draw.circle(surf, COLOR_BOMB, center, self.rect.width // 2)
            # bomb fuse
            fuse_rect = pygame.Rect(0, 0, 6, 14)
            fuse_rect.center = (center[0], center[1] - self.rect.width // 2 - 7)
            pygame.draw.rect(surf, (255, 215, 0), fuse_rect)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT - 150, PLAYER_SIZE, PLAYER_SIZE)
        self.shield_active = False
        self.shield_timer = 0

    def update(self, pos):
        self.rect.center = pos
        # Keep inside screen
        self.rect.clamp_ip(screen.get_rect())
        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False

    def draw(self, surf):
        color = COLOR_SHIELD if self.shield_active else COLOR_PLAYER
        pygame.draw.rect(surf, color, self.rect, border_radius=10)
        if self.shield_active:
            pygame.draw.rect(surf, (0, 255, 100), self.rect.inflate(12, 12), 4, border_radius=16)

class Game:
    def __init__(self):
        self.player = Player()
        self.stars = []
        self.bombs = []
        self.particles = []
        self.score = 0
        self.missed = 0
        self.shield_count = 0
        self.slow_time_count = 0
        self.slow_time_active = False
        self.slow_time_timer = 0
        self.game_over = False
        self.paused = False
        self.highscore = highscore
        self.spawn_timer = 0

    def reset(self):
        self.__init__()

    def spawn_objects(self):
        self.spawn_timer += 1
        star_chance = 0.03 + min(self.score / 1500, 0.06)
        bomb_chance = 0.007 + min(self.score / 3000, 0.03)
        if random.random() < star_chance:
            x = random.randint(0, WIDTH - STAR_SIZE)
            speed = random.uniform(3 + min(self.score / 100, 12), 5 + min(self.score / 80, 14))
            self.stars.append(FallingObject(x, -STAR_SIZE, STAR_SIZE, speed, "star"))
            # 10% chance power-up spawn with star
            if random.random() < 0.1:
                if random.choice([True, False]):
                    self.shield_count += 1
                else:
                    self.slow_time_count += 1
        if random.random() < bomb_chance:
            x = random.randint(0, WIDTH - BOMB_SIZE)
            speed = random.uniform(4 + min(self.score / 80, 16), 6 + min(self.score / 60, 18))
            self.bombs.append(FallingObject(x, -BOMB_SIZE, BOMB_SIZE, speed, "bomb"))

    def activate_slow_time(self):
        if self.slow_time_count > 0 and not self.slow_time_active:
            self.slow_time_active = True
            self.slow_time_timer = FPS * 4  # 4 seconds
            self.slow_time_count -= 1

    def activate_shield(self):
        if self.shield_count > 0 and not self.player.shield_active:
            self.player.shield_active = True
            self.player.shield_timer = FPS * 5  # 5 seconds
            self.shield_count -= 1

    def create_explosion(self, pos):
        for _ in range(PARTICLE_COUNT):
            self.particles.append(Particle(pos))

    def update_particles(self):
        for p in self.particles[:]:
            p.update()
            if p.life <= 0 or p.radius <= 0:
                self.particles.remove(p)

    def update(self):
        if self.game_over or self.paused:
            return

        self.spawn_objects()

        mouse_pos = pygame.mouse.get_pos()
        self.player.update(mouse_pos)

        for star in self.stars[:]:
            star.update(self.slow_time_active)
            if star.rect.colliderect(self.player.rect):
                self.score += 10
                self.create_explosion(star.rect.center)
                self.stars.remove(star)
            elif star.rect.top > HEIGHT:
                self.stars.remove(star)
                self.missed += 1

        for bomb in self.bombs[:]:
            bomb.update(self.slow_time_active)
            if bomb.rect.colliderect(self.player.rect):
                if self.player.shield_active:
                    self.player.shield_active = False
                    self.create_explosion(bomb.rect.center)
                    self.bombs.remove(bomb)
                else:
                    self.create_explosion(bomb.rect.center)
                    self.bombs.remove(bomb)
                    self.game_over = True
            elif bomb.rect.top > HEIGHT:
                self.bombs.remove(bomb)

        self.update_particles()

        if self.slow_time_active:
            self.slow_time_timer -= 1
            if self.slow_time_timer <= 0:
                self.slow_time_active = False

        if self.score > self.highscore:
            self.highscore = self.score
            save_highscore(self.highscore)

    def draw_ui(self, surf):
        score_text = font_medium.render(f"Score: {self.score}", True, COLOR_TEXT)
        highscore_text = font_small.render(f"High Score: {self.highscore}", True, COLOR_TEXT)
        shield_text = font_small.render(f"Shields: {self.shield_count}", True, COLOR_SHIELD)
        slow_text = font_small.render(f"Slow Time: {self.slow_time_count}", True, (255, 255, 0))

        surf.blit(score_text, (20, 20))
        surf.blit(highscore_text, (20, 70))
        surf.blit(shield_text, (20, 110))
        surf.blit(slow_text, (20, 140))

        if self.player.shield_active:
            active = font_small.render("SHIELD ACTIVE!", True, COLOR_SHIELD)
            surf.blit(active, (WIDTH//2 - active.get_width()//2, 30))
        if self.slow_time_active:
            active = font_small.render("SLOW TIME ACTIVE!", True, (255, 255, 0))
            surf.blit(active, (WIDTH//2 - active.get_width()//2, 60))

    def draw(self, surf):
        surf.fill(COLOR_BG)

        for p in self.particles:
            p.draw(surf)

        for star in self.stars:
            star.draw(surf)

        for bomb in self.bombs:
            bomb.draw(surf)

        self.player.draw(surf)
        self.draw_ui(surf)

        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surf.blit(overlay, (0, 0))
            over_text = font_large.render("GAME OVER!", True, COLOR_TEXT_ALERT)
            score_text = font_medium.render(f"Final Score: {self.score}", True, COLOR_TEXT)
            restart_text = font_small.render("Press R to Restart or ESC to Quit", True, COLOR_TEXT)

            surf.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 100))
            surf.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 30))
            surf.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 40))

    def toggle_pause(self):
        self.paused = not self.paused

    def draw_pause(self, surf):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))
        pause_text = font_large.render("PAUSED", True, COLOR_TEXT)
        cont_text = font_medium.render("Press ESC to Resume", True, COLOR_TEXT)
        surf.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 50))
        surf.blit(cont_text, (WIDTH//2 - cont_text.get_width()//2, HEIGHT//2 + 20))

def main():
    game = Game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.game_over:
                        running = False
                    else:
                        game.toggle_pause()
                if event.key == pygame.K_r and game.game_over:
                    game.reset()
                if event.key == pygame.K_s and not game.game_over and not game.paused:
                    game.activate_shield()
                if event.key == pygame.K_t and not game.game_over and not game.paused:
                    game.activate_slow_time()

        if not game.paused:
            game.update()

        game.draw(screen)

        if game.paused and not game.game_over:
            game.draw_pause(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
