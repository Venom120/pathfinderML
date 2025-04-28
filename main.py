import pygame
import random
import threading
import time
import queue

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

STONE_IMAGE = pygame.transform.scale(STONE_IMAGE, (CELL_SIZE, CELL_SIZE))
FIRE_IMAGE = pygame.transform.scale(FIRE_IMAGE, (CELL_SIZE, CELL_SIZE))
DIAMOND_IMAGE = pygame.transform.scale(DIAMOND_IMAGE, (CELL_SIZE, CELL_SIZE))



# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pathfinder Game")

# Agent class
class GameObject(pygame.sprite.Sprite):
    def __init__(self, image, x, y, width, height):
        super().__init__()
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Agent(GameObject):
    def __init__(self, image, x, y):
        super().__init__(image, x, y, CELL_SIZE, CELL_SIZE)
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.x = self.x * CELL_SIZE
        self.rect.y = self.y * CELL_SIZE

    def reset(self):
        self.x = 0
        self.y = 0
        self.rect.x = self.x * CELL_SIZE
        self.rect.y = self.y * CELL_SIZE

# Function to generate the matrix
def generate_matrix(n):
    matrix = [['empty' for _ in range(n)] for _ in range(n)]

    # Place stone and fire, ensuring they are not on the edges
    stone_count = 0
    fire_count = 0

    while stone_count < 5:
        x = random.randint(1, n - 2)
        y = random.randint(1, n - 2)
        if matrix[x][y] == 'empty':
            matrix[x][y] = 'stone'
            stone_count += 1

    while fire_count < 5:
        x = random.randint(1, n - 2)
        y = random.randint(1, n - 2)
        if matrix[x][y] == 'empty':
            matrix[x][y] = 'fire'
            fire_count += 1

    # Ensure diamond has at least one open side
    matrix[n-1][n-1] = 'diamond'

    return matrix

# Event handling thread
def event_handler(events, agent, matrix, running):
    while running[0]:
        event = events.get()
        if event is not None:
            if event.type == pygame.QUIT:
                running[0] = False
            if event.type == pygame.KEYDOWN:
                new_x, new_y = agent.x, agent.y
                if event.key == pygame.K_LEFT:
                    new_x -= 1
                elif event.key == pygame.K_RIGHT:
                    new_x += 1
                elif event.key == pygame.K_UP:
                    new_y -= 1
                elif event.key == pygame.K_DOWN:
                    new_y += 1

                if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and matrix[new_y][new_x] != 'stone':
                    agent.move(new_x - agent.x, new_y - agent.y)
        time.sleep(0.01)

# Game loop
def game():
    agent = Agent(AGENT_IMAGE, 0, 0)
    matrix = generate_matrix(GRID_SIZE)
    running = [True]
    events = queue.Queue()

    # Start event handling thread
    event_thread = threading.Thread(target=event_handler, args=(events, agent, matrix, running))
    event_thread.start()

    while running[0]:
        # Get events from queue
        for event in pygame.event.get():
            events.put(event)

        # Game logic
        # Check for fire
        if matrix[agent.y][agent.x] == 'fire':
            agent.reset()

        # Check for diamond
        if matrix[agent.y][agent.x] == 'diamond':
            matrix = generate_matrix(GRID_SIZE)
            agent.reset()

        # Drawing
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
                    pygame.draw.rect(screen, (0, 0, 0), (x, y, CELL_SIZE, CELL_SIZE), 1)

                # Add cell identifier
                font = pygame.font.Font(None, 12)
                text = font.render(f"S{i * GRID_SIZE + j + 1}", True, (0, 0, 0))
                screen.blit(text, (x + 5, y + 5))

        # Draw the agent
        agent.draw(screen)

        pygame.display.flip()

    event_thread.join()
    pygame.quit()

if __name__ == "__main__":
    game()