from main import Agent
import random

def manhattan_distance(cell, goal=(9, 9)):
    """
    Calculate the Manhattan distance from a cell to the diamond at (9, 9).
    :param cell: tuple (x, y) - current cell coordinates
    :param goal: tuple (x, y) - goal cell coordinates (default is diamond at (9, 9))
    :return: int - Manhattan distance
    """
    x, y = cell
    gx, gy = goal
    return abs(x - gx) + abs(y - gy)

class QTable:
    def __init__(self):
        self.q = {}
        actions = ['up', 'down', 'left', 'right']
        goal = (9, 9)
        grid_size = 10

        for x in range(grid_size):
            for y in range(grid_size):
                for action in actions:
                    nx, ny = x, y
                    if action == 'up' and y > 0:
                        ny -= 1
                    elif action == 'down' and y < grid_size - 1:
                        ny += 1
                    elif action == 'left' and x > 0:
                        nx -= 1
                    elif action == 'right' and x < grid_size - 1:
                        nx += 1

                    dist_now = manhattan_distance((x, y), goal)
                    dist_next = manhattan_distance((nx, ny), goal)

                    is_middle = (
                        1 <= nx < grid_size - 1 and
                        1 <= ny < grid_size - 1 and
                        (nx, ny) != goal
                    )

                    # --- NEW LOGIC: Encourage bottom row and rightmost column ---
                    is_bottom_row = (y == grid_size - 1 and x < grid_size - 1)
                    is_right_col = (x == grid_size - 1 and y < grid_size - 1)

                    # Identify special cells for extra boost
                    cell_num = ny * grid_size + nx + 1
                    high_reward_cells = {50, 60, 70, 90, 95, 96, 97, 98, 99, 100}
                    low_reward_cells = {10, 20, 30, 40, 91, 92, 93, 94}

                    boost = 1.0
                    if cell_num in high_reward_cells:
                        boost = 8.0
                    elif cell_num in low_reward_cells:
                        boost = 0.5
                    elif (is_bottom_row or is_right_col) and dist_next < dist_now:
                        boost = 4.0

                    if (x, y) == goal:
                        q_value = 0.0
                    elif (nx, ny) == goal:
                        q_value = 100.0
                    elif dist_next < dist_now:
                        q_value = (8.0 if is_middle else 0.8) * boost
                    elif dist_next == dist_now:
                        q_value = (5.0 if is_middle else 0.5) * boost
                    else:
                        q_value = (2.0 if is_middle else 0.2) * boost

                    self.q[((x, y), action)] = q_value

    def get_q_value(self, state, action):
        return self.q.get((state, action), 0.0)

    def set_q_value(self, state, action, value):
        self.q[(state, action)] = value

    def choose_action(self, state, epsilon):
        # Example: always pick the action with highest Q-value for the state
        actions = ['up', 'down', 'left', 'right']
        if random.uniform(0, 1) < epsilon:
            return random.choice(actions)  # Explore
        else:
            q_values = [self.get_q_value(state, a) for a in actions]
            max_q = max(q_values)
            best_actions = [a for a, q in zip(actions, q_values) if q == max_q]
            return random.choice(best_actions)  # Exploit

class Qlearning:
    def __init__(self, q_table, learning_rate=0.1, discount_factor=0.9, epsilon=0.1):
        self.q_table = q_table
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.actions = ['up', 'down', 'left', 'right']

    def step(self, state):
        action = self.q_table.choose_action(state, self.epsilon)
        return action

    def observe(self, state, action, reward, next_state):
        old_q_value = self.q_table.get_q_value(state, action)
        next_max_q = max([self.q_table.get_q_value(next_state, a) for a in self.actions])
        new_q_value = (1 - self.learning_rate) * old_q_value + self.learning_rate * (reward + self.discount_factor * next_max_q)
        self.q_table.set_q_value(state, action, new_q_value)