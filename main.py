import time
import pygame
import random
import sys
import pygame.event
import qlearning

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
num_agents = 5

# Winners file
WINNERS_FILE = "winners.txt"

# Agent class
class Agent:
    def __init__(self, x, y, agent_id):
        self.x = x
        self.y = y
        self.rect = AGENT_IMAGE.get_rect()
        self.rect.x = x * CELL_SIZE
        self.rect.y = y * CELL_SIZE + OFFSET
        self.agent_id = agent_id
        self.has_reached_diamond = False
        self.score = 0 # Individual agent score

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
        self.has_reached_diamond = False

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
def draw_menu_bar(agents, level, attempts):
    pygame.draw.rect(screen, (200, 200, 200), (0, 0, WIDTH, OFFSET))
    restart_text = FONT.render("Restart", True, (0, 0, 0))
    reset_text = FONT.render("Reset", True, (0, 0, 0))
    # Display individual agent scores
    score_texts = [FONT.render(f"{agent.score}", True, (0, 0, 0)) for agent in agents]
    level_text = FONT.render(f"Level: {level}", True, (0, 0, 0))
    attempts_text = FONT.render(f"Attempts: {attempts}", True, (0, 0, 0))

    screen.blit(restart_text, (10, 5))
    screen.blit(reset_text, (120, 5))
    # Calculate positions for individual scores
    score_x_start = WIDTH // 2 - (len(score_texts) * 60) // 2 # Adjusted for 5 scores and labels
    for i, score_text in enumerate(score_texts):
        screen.blit(score_text, (score_x_start + i * 60, 5)) # Spacing between scores and labels
    screen.blit(level_text, (WIDTH - 150, 5))
    # screen.blit(attempts_text, (WIDTH - 250, 5))

def save_level_start_scores(agents):
    """Save the current score of each agent at the start of a level."""
    return [agent.score for agent in agents]

def restore_level_start_scores(agents, level_start_scores):
    """Restore each agent's score to what it was at the start of the level."""
    for agent, score in zip(agents, level_start_scores):
        agent.score = score

def train_q_learning(agents, matrix, q_agent, num_episodes): # Removed training function
    global attempts
    global level
    global running
    global max_levels
    rewards = []
    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                print("Exiting game")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    print("Exiting game")
                if event.key == pygame.K_SPACE:
                    is_paused = not is_paused  # Toggle pause state
                if event.key == pygame.K_r:
                    score = 0
                    level = 1
                    attempts = 0
                    matrix = generate_matrix(GRID_SIZE, level)
                    for agent in agents:
                        agent.reset()
                        agent.score = 0
                if event.key == pygame.K_q:
                    running = False
                    print("Exiting game")
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if y < OFFSET:  # Menu bar click
                    if 10 <= x <= 100:  # Restart button
                        score = 0
                        level = 1
                        attempts = 0
                        matrix = generate_matrix(GRID_SIZE, level)
                        for agent in agents:
                            agent.reset()
                    elif 120 <= x <= 200:  # Reset button
                        matrix = generate_matrix(GRID_SIZE, level)
                        for agent in agents:
                            agent.reset()
        # Reset agent positions and diamond status at the start of each episode
        for agent in agents:
            agent.reset()
        states = [(agent.x, agent.y) for agent in agents]
        done = [False] * len(agents)
        total_reward = [0] * len(agents)
        while not all(done):
            for agent_index, agent in enumerate(agents):
                # --- Event Handling ---
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        print("Exiting game")
                    if event.type == pygame.KEYDOWN:
                        print("Hi")
                        if event.key == pygame.K_ESCAPE:
                            running = False
                            print("Exiting game")
                        if event.key == pygame.K_SPACE:
                            is_paused = not is_paused # Toggle pause state
                        if not is_paused: # Process game actions only if not paused
                            if event.key == pygame.K_r:
                                score = 0
                                level = 1
                                attempts = 0
                                matrix = generate_matrix(GRID_SIZE, level)
                                for agent in agents:
                                    agent.reset()
                                    agent.score = 0
                            if event.key == pygame.K_q:
                                running = False
                                print("Exiting game")
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if not is_paused: # Process clicks only if not paused
                            x, y = pygame.mouse.get_pos()
                            if y < OFFSET:  # Menu bar click
                                if 10 <= x <= 100:  # Restart button
                                    score = 0
                                    level = 1
                                    attempts = 0
                                    matrix = generate_matrix(GRID_SIZE, level)
                                    for agent in agents:
                                        agent.reset()
                                elif 120 <= x <= 200:  # Reset button
                                    # Reset score to start of level score? Need to track this.
                                    # For now, just reset agent and matrix as per original logic
                                    matrix = generate_matrix(GRID_SIZE, level) # Regenerates matrix, original comment was wrong
                                    for agent in agents:
                                        agent.reset()
                if agent.has_reached_diamond:
                    continue
                if not done[agent_index]:
                    state = (agent.x, agent.y)
                    action = q_agent.step(state)
                    dx, dy = 0, 0
                    if action == 'up':
                        dy = -1
                    elif action == 'down':
                        dy = 1
                    elif action == 'left':
                        dx = -1
                    elif action == 'right':
                        dx = 1

                    new_x, new_y = agent.x + dx, agent.y + dy
                    if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and matrix[new_y][new_x] != 'stone':
                        agent.move(dx, dy)
                        next_state = (agent.x, agent.y)
                        if matrix[agent.y][agent.x] == 'fire':
                            reward = -10
                            agent.reset()
                            attempts += 1
                        elif matrix[agent.y][agent.x] == 'diamond':
                            reward = 10
                            done[agent_index] = True
                            agent.has_reached_diamond = True
                        else:
                            reward = -0.1
                            done[agent_index] = False
                    else:
                        next_state = state
                        reward = -0.2
                        done[agent_index] = False

                    q_agent.observe(state, action, reward, next_state)
                    state = next_state
                    total_reward[agent_index] += reward
                    if not agent.has_reached_diamond:
                        agent.score += 1 # Increment agent's score

            # --- Rendering during training ---
            if not is_paused:
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
                for agent in agents:
                    screen.blit(AGENT_IMAGE, agent.rect)
                draw_menu_bar(agents, level, attempts)
                pygame.display.flip()
                # time.sleep(0.1) # Removed sleep during training

        for i in range(len(agents)):
            rewards.append(total_reward[i])
        # if (episode + 1) % 100 == 0:
        #     print(f"Episode {episode + 1}: Total Reward = {sum(total_reward)/len(agents)}")
    return rewards, attempts

# Game loop
# Game loop variables
agents = []
matrix = None
running = True
# agent_direction = (0, 0) # Desired agent movement (dx, dy)
q_agent = None # Q-learning agent
learning_rate = 0.1
discount_factor = 0.9
epsilon = 0.1

# Main game loop
if __name__ == "__main__":
    agents = [Agent(0, 0, i) for i in range(num_agents)]
    matrix = generate_matrix(GRID_SIZE, level)
    clock = pygame.time.Clock()
    q_table = qlearning.QTable()
    q_agent = qlearning.Qlearning(q_table, learning_rate, discount_factor, epsilon)

    # Save scores at the start of the level
    level_start_scores = save_level_start_scores(agents)

    # --- Game Loop ---
    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                print("Exiting game")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    print("Exiting game")
                if event.key == pygame.K_SPACE:
                    is_paused = not is_paused  # Toggle pause state
                if event.key == pygame.K_r:
                    score = 0
                    level = 1
                    attempts = 0
                    matrix = generate_matrix(GRID_SIZE, level)
                    for agent in agents:
                        agent.reset()
                        agent.score = 0
                    # Save new level start scores
                    level_start_scores = save_level_start_scores(agents)
                if event.key == pygame.K_q:
                    running = False
                    print("Exiting game")
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if y < OFFSET:  # Menu bar click
                    if 10 <= x <= 100:  # Restart button
                        score = 0
                        level = 1
                        attempts = 0
                        matrix = generate_matrix(GRID_SIZE, level)
                        for agent in agents:
                            agent.reset()
                            agent.score = 0
                        # Save new level start scores
                        level_start_scores = save_level_start_scores(agents)
                    elif 120 <= x <= 200:  # Reset button
                        matrix = generate_matrix(GRID_SIZE, level)
                        for agent in agents:
                            agent.reset()
                        # Restore scores to what they were at the start of the level
                        restore_level_start_scores(agents, level_start_scores)
        # --- Game State Update ---
        if not is_paused:
            # Simultaneous movement using Q-learning
            agent_states = [(agent.x, agent.y) for agent in agents]
            agent_actions = [q_agent.step(state) for state in agent_states]
            new_agent_positions = []
            rewards = []
            done = [False] * len(agents)

            # Update score *before* agent movement
            for agent in agents:
                if not agent.has_reached_diamond:
                    agent.score += 1

            for agent_index, agent in enumerate(agents):
                dx, dy = 0, 0
                action = agent_actions[agent_index]
                if action == 'up':
                    dy = -1
                elif action == 'down':
                    dy = 1
                elif action == 'left':
                    dx = -1
                elif action == 'right':
                    dx = 1


                if agent.has_reached_diamond:
                    new_x, new_y = agent.x, agent.y
                    new_agent_positions.append((new_x, new_y))  # Ensure position is appended!
                else:
                    new_x, new_y = agent.x + dx, agent.y + dy
                    if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and matrix[new_y][new_x] != 'stone':
                        new_agent_positions.append((new_x, new_y))
                    else:
                        new_agent_positions.append((agent.x, agent.y)) # Stay in place if invalid move


            for agent_index, agent in enumerate(agents):
                new_x, new_y = new_agent_positions[agent_index]
                state = (agent.x, agent.y)
                action = agent_actions[agent_index]
                agent.x, agent.y = new_x, new_y
                agent.rect.x = agent.x * CELL_SIZE
                agent.rect.y = agent.y * CELL_SIZE + OFFSET


                if matrix[agent.y][agent.x] == 'fire':
                    agent.reset()
                    attempts += 1
                    reward = -10
                    q_agent.observe(state, action, reward, (agent.x, agent.y))
                    done[agent_index] = True
                elif matrix[agent.y][agent.x] == 'diamond':
                    agent.has_reached_diamond = True
                    reward = 10
                    q_agent.observe(state, action, reward, (agent.x, agent.y))
                    done[agent_index] = True
                else:
                    reward = -0.1
                    q_agent.observe(state, action, reward, (agent.x, agent.y))
                    done[agent_index] = False

            # Check if all agents have reached the diamond
            all_agents_reached_diamond = all(agent.has_reached_diamond for agent in agents)
            if all_agents_reached_diamond:
                level += 1
                # Save new level start scores
                level_start_scores = save_level_start_scores(agents)
                if level > max_levels:
                    with open(WINNERS_FILE, "a") as file:
                        file.write(f"Score: {score}, Attempts: {attempts}\n")
                    running = False
                    print("Exiting game")
                else:
                    matrix = generate_matrix(GRID_SIZE, level)
                    for agent in agents:
                        agent.reset()

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

            for agent in agents:
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
        draw_menu_bar(agents, level, attempts) # Draw menu bar always

        pygame.display.flip()
        clock.tick(60)
        time.sleep(0.01) # Add sleep to control game speed