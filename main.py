import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 10
CELL_SIZE = WIDTH // GRID_SIZE
WHITE = (255, 255, 255)

# Load images
STONE_IMAGE = pygame.image.load("./static/stone.jpg")
FIRE_IMAGE = pygame.image.load("./static/fire.jpg")
DIAMOND_IMAGE = pygame.image.load("./static/diamond.jpg")
AGENT_IMAGE = pygame.image.load("./static/agent.jpg")

AGENT_IMAGE = pygame.transform.scale(AGENT_IMAGE, (CELL_SIZE, CELL_SIZE))
STONE_IMAGE = pygame.transform.scale(STONE_IMAGE, (CELL_SIZE, CELL_SIZE))
FIRE_IMAGE = pygame.transform.scale(FIRE_IMAGE, (CELL_SIZE, CELL_SIZE))
DIAMOND_IMAGE = pygame.transform.scale(DIAMOND_IMAGE, (CELL_SIZE, CELL_SIZE))


# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pathfinder Game")

# Agent class
class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = AGENT_IMAGE.get_rect()
        self.rect.x = x * CELL_SIZE
        self.rect.y = y * CELL_SIZE

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.x = self.x * CELL_SIZE
        self.rect.y = self.y * CELL_SIZE

# Function to generate the matrix
def generate_matrix(n):
    matrix = [['empty' for _ in range(n)] for _ in range(n)]

    # Place stone and fire
    stone_count = 0
    fire_count = 0

    while stone_count < 5:
        x = random.randint(0, n - 1)
        y = random.randint(0, n - 1)
        if matrix[x][y] == 'empty':
            matrix[x][y] = 'stone'
            stone_count += 1

    while fire_count < 5:
        x = random.randint(0, n - 1)
        y = random.randint(0, n - 1)
        if matrix[x][y] == 'empty':
            matrix[x][y] = 'fire'
            fire_count += 1

    matrix[n-1][0] = 'empty'
    matrix[n-1][n-1] = 'diamond'

    return matrix

# Game loop
def game():
    agent = Agent(0, 0)
    matrix = generate_matrix(GRID_SIZE)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    agent.move(-1, 0)
                if event.key == pygame.K_RIGHT:
                    agent.move(1, 0)
                if event.key == pygame.K_UP:
                    agent.move(0, -1)
                if event.key == pygame.K_DOWN:
                    agent.move(0, 1)
        if agent.x < 0:
            agent.x = 0
        if agent.x > GRID_SIZE -1:
            agent.x = GRID_SIZE -1
        if agent.y < 0:
            agent.y = 0
        if agent.y > GRID_SIZE -1:
            agent.y = GRID_SIZE -1
        # Draw everything
        screen.fill(WHITE)

        # Draw the grid
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x = j * CELL_SIZE
                y = i * CELL_SIZE
                if matrix[i][j] == 'stone':
                    screen.blit(STONE_IMAGE, (x, y))
                elif matrix[i][j] == 'fire':
                    screen.blit(FIRE_IMAGE, (x, y))
                elif matrix[i][j] == 'diamond':
                    screen.blit(DIAMOND_IMAGE, (x, y))
                else:
                    pygame.draw.rect(screen, (0,0,0), (x, y, CELL_SIZE, CELL_SIZE), 1)

                # Add cell identifier
                font = pygame.font.Font(None, 12)
                text = font.render(f"S{i * GRID_SIZE + j + 1}", True, (0, 0, 0))
                screen.blit(text, (x + 5, y + 5))

        # Draw the agent
        screen.blit(AGENT_IMAGE, agent.rect)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    game()