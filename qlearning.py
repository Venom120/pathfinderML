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
        # Hardcoded Q-matrix for demonstration: {(state), action: value}
        # Example: {((x, y), action): q_value}
        self.q = {}
        actions = ['up', 'down', 'left', 'right']
        goal = (9, 9)
        grid_size = 10

        for x in range(grid_size):
            for y in range(grid_size):
                for action in actions:
                    # Calculate next cell after action
                    nx, ny = x, y
                    if action == 'up' and y > 0:
                        ny -= 1
                    elif action == 'down' and y < grid_size - 1:
                        ny += 1
                    elif action == 'left' and x > 0:
                        nx -= 1
                    elif action == 'right' and x < grid_size - 1:
                        nx += 1

                    # Manhattan distances
                    dist_now = manhattan_distance((x, y), goal)
                    dist_next = manhattan_distance((nx, ny), goal)

                    # Q-value: higher if moving closer to goal, 1.0 for reaching goal, 0.0 if at goal
                    if (x, y) == goal:
                        q_value = 0.0
                    elif (nx, ny) == goal:
                        q_value = 1.0
                    elif dist_next < dist_now:
                        q_value = 0.8
                    elif dist_next == dist_now:
                        q_value = 0.5
                    else:
                        q_value = 0.2

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