################### Part 0 - Game description ###################
"""
Write Python code to build a Python game using Pygame where the player controls a paddle at the bottom of the screen
to catch falling stars, with increasing score for every caught star and a count of missed stars.
The game should include smooth movement using keyboard controls (left/right), random star spawning from the top, 
collision detection between the paddle and stars, score tracking, and dynamic drawing of stars and text on the screen.
Also, the game loop should maintain consistent frame rates, and the game window should close cleanly when the user exits."
"""

# run this command in the terminal to install pygame: python -m pip install pygame
################### Part 1 - Import necessary modules ###################
import pygame
import random
import sys
# Initialize pygame
pygame.init()
# Constants - these values don't change during the game
WIDTH, HEIGHT = 800, 600          # The width and height of the game window in pixels
FPS = 60                          # Frames Per Second - controls how smooth the game runs
PLAYER_WIDTH, PLAYER_HEIGHT = 100, 20  # Size of the player's paddle
STAR_SIZE = 20                    # Size of the falling stars
WHITE = (255, 255, 255)           # RGB color codes (Red, Green, Blue) for white
BLACK = (0, 0, 0)                 # RGB color for black
STAR_COLOR = (255, 215, 0)        # RGB color for gold/yellow stars
PLAYER_COLOR = (0, 255, 0)        # RGB color for green player
# Screen setup - creates the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))      # Creates the game window with specified dimensions
pygame.display.set_caption("Catch the Falling Stars")  # Sets the title of the game window
clock = pygame.time.Clock()                            # Creates a clock to control game timing and framerate

################### Part 2 - Game setup - initialize game variables ###################
font = pygame.font.SysFont(None, 36)            # Sets up a system font with size 36 for displaying text on screen
# Creates a rectangle for the player's paddle at the bottom center of screen
player = pygame.Rect(WIDTH // 2 - PLAYER_WIDTH // 2, HEIGHT - 50, PLAYER_WIDTH, PLAYER_HEIGHT)
player_speed = 7                  # How fast the player moves left/right when keys are pressed
# Stars - setup for falling star objects
stars = []                        # Empty list to store all active stars
star_fall_speed = 5               # How fast stars fall down the screen
score = 0                         # Player's current score (starts at 0)
missed = 0                        # Count   of missed stars (starts at 0)
running = True
# Function to create a new star
def create_star():
    x = random.randint(0, WIDTH - STAR_SIZE)        # Random x position within screen width
    rect = pygame.Rect(x, 0, STAR_SIZE, STAR_SIZE)  # Create rectangle at top of screen with random x position
    return rect                                     # Return the new star object

################### Part 3 - Main game loop ###################
while running:
    screen.fill(BLACK)                                # Fill the screen with black color (clears previous frame)
    # Events handling - check for user input like closing the window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:                  # If user clicks the close button
            running = False                            # Stop the game loop
    # Controls - handle keyboard input for moving the player
    keys = pygame.key.get_pressed()                    # Get the current state of all keyboard keys
    if keys[pygame.K_LEFT] and player.left > 0:        # If left arrow key is pressed and player isn't at left edge
        player.x -= player_speed                       # Move player left
    if keys[pygame.K_RIGHT] and player.right < WIDTH:  # If right arrow key is pressed and player isn't at right edge
        player.x += player_speed                       # Move player right
    # Create new stars randomly
    if random.randint(1, 10) == 1:                     # 10% chance each frame to create a star
        stars.append(create_star())                    # Add a new star to the list
    # Move stars down the screen
    for star in stars[:]:                              # Loop through a copy of the stars list
        star.y += star_fall_speed                      # Move the star downward by adding to its y position
        if star.colliderect(player):                   # Check if star touches the player paddle
            stars.remove(star)                         # Remove the star from the game
            score += 1                                 # Increase player's score
        elif star.y > HEIGHT:                          # If star goes below the bottom of the screen
            stars.remove(star)                         # Remove the star from the game
            missed += 1                                # Increase missed count

################### Part 4 - Draw everything on the screen ###################
    pygame.draw.rect(screen, PLAYER_COLOR, player)     # Draw player paddle on screen
    for star in stars:                                 # Loop through all stars in the list 
        pygame.draw.rect(screen, STAR_COLOR, star)
    # Draw score and missed count text
    score_text = font.render(f"Score: {score}", True, WHITE)     # Create text image for score
    missed_text = font.render(f"Missed: {missed}", True, WHITE)  # Create text image for missed count
    screen.blit(score_text, (10, 10))                            # Draw score text at top-left position
    screen.blit(missed_text, (10, 40))                           # Draw missed text below score
    # Update display with everything we've drawn
    pygame.display.flip()
    # Maintain consistent game speed
    clock.tick(FPS)                             # Wait until it's time for next frame, targeting our FPS rate
# Clean up and exit when game loop ends
pygame.quit()
sys.exit()