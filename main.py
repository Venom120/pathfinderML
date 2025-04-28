import pygame
import random
import sys
import pygame.event

# Initialize Pygame
pygame.init()

# Pause state flag
is_paused = False
is_pixelated = False

# Constants
OFFSET = 40
WIDTH, HEIGHT = 800, 800+OFFSET
GRID_SIZE = 10
CELL_SIZE = WIDTH // GRID_SIZE
WHITE = (255, 255, 255)
FONT = pygame.font.Font(None, 36)

# Load images
ICON_IMAGE = pygame.image.load("./static/agent.png")
STONE_IMAGE = pygame.image.load("./static/stone.jpg")
FIRE_IMAGE = pygame.image.load("./static/fire.jpg")
DIAMOND_IMAGE = pygame.image.load("./static/diamond.jpg")
AGENT_IMAGE = pygame.image.load("./static/agent.png")

AGENT_IMAGE = pygame.transform.scale(AGENT_IMAGE, (CELL_SIZE, CELL_SIZE))
STONE_IMAGE = pygame.transform.scale(STONE_IMAGE, (CELL_SIZE, CELL_SIZE))
FIRE_IMAGE = pygame.transform.scale(FIRE_IMAGE, (CELL_SIZE, CELL_SIZE))
DIAMOND_IMAGE = pygame.transform.scale(DIAMOND_IMAGE, (CELL_SIZE, CELL_SIZE))

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_icon(ICON_IMAGE)
pygame.display.set_caption("Pathfinder Game")

# Initialize variables
score = 0
level = 1
attempts = 0
max_levels = 100

# Winners file
WINNERS_FILE = "winners.txt"

# Agent class
class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = AGENT_IMAGE.get_rect()
        self.rect.x = x * CELL_SIZE
        self.rect.y = y * CELL_SIZE + OFFSET

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.x = self.x * CELL_SIZE
        self.rect.y = self.y * CELL_SIZE + OFFSET

    def reset(self):
        self.x = 0
        self.y = 0
        self.rect.x = self.x * CELL_SIZE
        self.rect.y = self.y * CELL_SIZE + OFFSET

# Function to generate the matrix
def generate_matrix(n, level):
    matrix = [['empty' for _ in range(n)] for _ in range(n)]

    # Place stone and fire, ensuring they are not on the edges
    stone_count = 5 + (level // 20) * 2
    fire_count = 5 + (level // 10) * 2 if level % 20 != 0 else 5

    while stone_count > 0:
        x = random.randint(1, n - 2)
        y = random.randint(1, n - 2)
        if matrix[x][y] == 'empty':
            matrix[x][y] = 'stone'
            stone_count -= 1

    while fire_count > 0:
        x = random.randint(1, n - 2)
        y = random.randint(1, n - 2)
        if matrix[x][y] == 'empty':
            matrix[x][y] = 'fire'
            fire_count -= 1

    # Ensure diamond has at least one open side
    matrix[n-1][n-1] = 'diamond'

    return matrix

# Draw the menu bar
def draw_menu_bar(score, level):
    pygame.draw.rect(screen, (200, 200, 200), (0, 0, WIDTH, OFFSET))
    restart_text = FONT.render("Restart", True, (0, 0, 0))
    reset_text = FONT.render("Reset", True, (0, 0, 0))
    score_text = FONT.render(f"Score: {score}", True, (0, 0, 0))
    level_text = FONT.render(f"Level: {level}", True, (0, 0, 0))

    screen.blit(restart_text, (10, 5))
    screen.blit(reset_text, (120, 5))
    screen.blit(score_text, (WIDTH // 2 - 50, 5))
    screen.blit(level_text, (WIDTH - 150, 5))

# Game loop
# Game loop variables
agent = None
matrix = None
running = True
agent_direction = (0, 0) # Desired agent movement (dx, dy)

# Main game loop
if __name__ == "__main__":
    agent = Agent(0, 0)
    matrix = generate_matrix(GRID_SIZE, level)
    clock = pygame.time.Clock()

    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    is_paused = not is_paused # Toggle pause state
                if not is_paused: # Process game actions only if not paused
                    if event.key == pygame.K_r:
                        score = 0
                        level = 1
                        attempts = 0
                        matrix = generate_matrix(GRID_SIZE, level)
                        agent.reset()
                    if event.key == pygame.K_q:
                        with open(WINNERS_FILE, "a") as file:
                            file.write(f"Score: {score}, Attempts: {attempts}\n")
                        running = False
                    # Agent movement keys
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        agent_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        agent_direction = (1, 0)
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        agent_direction = (0, -1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        agent_direction = (0, 1)

            if event.type == pygame.MOUSEBUTTONDOWN:
                 if not is_paused: # Process clicks only if not paused
                    x, y = pygame.mouse.get_pos()
                    if y < OFFSET:  # Menu bar click
                        if 10 <= x <= 100:  # Restart button
                            score = 0
                            level = 1
                            attempts = 0
                            matrix = generate_matrix(GRID_SIZE, level)
                            agent.reset()
                        elif 120 <= x <= 200:  # Reset button
                            # Reset score to start of level score? Need to track this.
                            # For now, just reset agent and matrix as per original logic
                            matrix = generate_matrix(GRID_SIZE, level) # Regenerates matrix, original comment was wrong
                            agent.reset()


        # --- Game State Update ---
        if not is_paused:
            # Apply movement
            dx, dy = agent_direction
            if dx != 0 or dy != 0:
                new_x, new_y = agent.x + dx, agent.y + dy
                if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and matrix[new_y][new_x] != 'stone':
                    agent.move(dx, dy)
                    score += 1

                    # Check for fire
                    if matrix[agent.y][agent.x] == 'fire':
                        agent.reset()
                        attempts += 1

                    # Check for diamond
                    if matrix[agent.y][agent.x] == 'diamond':
                        level += 1
                        if level > max_levels:
                            with open(WINNERS_FILE, "a") as file:
                                file.write(f"Score: {score}, Attempts: {attempts}\n")
                            running = False
                        if running: # Only generate new matrix if game continues
                            matrix = generate_matrix(GRID_SIZE, level)
                            agent.reset()

                agent_direction = (0, 0) # Reset direction after processing/attempting move

        if not is_paused:
            screen.fill(WHITE) # Fill screen with white before drawing
            # Draw grid and agent if not paused
            if matrix:
                for i in range(GRID_SIZE):
                    for j in range(GRID_SIZE):
                        x = j * CELL_SIZE
                        y = i * CELL_SIZE + OFFSET
                        if matrix[i][j] == 'stone':
                            screen.blit(STONE_IMAGE, (x, y))
                        elif matrix[i][j] == 'fire':
                            screen.blit(FIRE_IMAGE, (x, y))
                        elif matrix[i][j] == 'diamond':
                            screen.blit(DIAMOND_IMAGE, (x, y))
                        pygame.draw.rect(screen, (0, 0, 0), (x, y, CELL_SIZE, CELL_SIZE), 1)

                        # Add cell identifier
                        font = pygame.font.SysFont(None, 20)
                        text = font.render(f"S{i * GRID_SIZE + j + 1}", False, (0, 0, 0))
                        screen.blit(text, (x + 5, y + 5))

            if agent:
                screen.blit(AGENT_IMAGE, agent.rect)
            is_pixelated = False # Reset pixelation state when not paused

        elif is_paused and not is_pixelated:
            # Create pixelated effect for the game area when paused
            game_area_rect = pygame.Rect(0, OFFSET, WIDTH, HEIGHT - OFFSET)
            game_area_surface = screen.subsurface(game_area_rect).copy()

            # Scale down smoothly
            scale_factor = 20  # Lower factor = more pixelated
            small_surface = pygame.transform.smoothscale(
                game_area_surface,
                (WIDTH // scale_factor, (HEIGHT - OFFSET) // scale_factor)
            )
            # Scale back up without smoothing (pixelated)
            pixelated_surface = pygame.transform.scale(
                small_surface,
                (WIDTH, HEIGHT - OFFSET)
            )
            screen.blit(pixelated_surface, (0, OFFSET))

            # Draw pause symbol on top of the pixelated area
            pause_bar_width = CELL_SIZE // 4
            pause_bar_height = CELL_SIZE * 1.5
            pause_bar_color = (100, 100, 100)
            left_bar_x = WIDTH // 2 - pause_bar_width - 10
            right_bar_x = WIDTH // 2 + 10
            pause_bar_y = HEIGHT // 2 - pause_bar_height // 2
            pygame.draw.rect(screen, pause_bar_color, (left_bar_x, pause_bar_y, pause_bar_width, pause_bar_height))
            pygame.draw.rect(screen, pause_bar_color, (right_bar_x, pause_bar_y, pause_bar_width, pause_bar_height))
            is_pixelated = True

        # --- Drawing ---
        draw_menu_bar(score, level) # Draw menu bar always

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()
