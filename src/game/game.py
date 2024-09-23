import curses
import random
import numpy as np
import argparse
from qLearningAgent import QLearningAgent

class SnakeGame:
    def __init__(self, height=20, width=20):
        self.height = height
        self.width = width
        self.reset()

    def reset(self):
        self.snake = [[self.height // 2, self.width // 4],
                      [self.height // 2, self.width // 4 - 1],
                      [self.height // 2, self.width // 4 - 2]]
        self.food = [self.height // 2, self.width // 2]
        self.score = 0
        self.direction = curses.KEY_RIGHT
        return self._get_state()

    def step(self, action):
        # Map action (0, 1, 2, 3) to direction
        if action == 0 and self.direction != curses.KEY_DOWN:
            self.direction = curses.KEY_UP
        elif action == 1 and self.direction != curses.KEY_UP:
            self.direction = curses.KEY_DOWN
        elif action == 2 and self.direction != curses.KEY_RIGHT:
            self.direction = curses.KEY_LEFT
        elif action == 3 and self.direction != curses.KEY_LEFT:
            self.direction = curses.KEY_RIGHT

        # Move the snake
        new_head = self.snake[0].copy()
        if self.direction == curses.KEY_UP:
            new_head[0] -= 1
        elif self.direction == curses.KEY_DOWN:
            new_head[0] += 1
        elif self.direction == curses.KEY_LEFT:
            new_head[1] -= 1
        elif self.direction == curses.KEY_RIGHT:
            new_head[1] += 1

        self.snake.insert(0, new_head)

        # Check if game over
        if (new_head[0] <= 0 or new_head[0] >= self.height - 1 or
            new_head[1] <= 0 or new_head[1] >= self.width - 1 or
            new_head in self.snake[1:]):
            return self._get_state(), -1, True

        # Check if food eaten
        if new_head == self.food:
            self.score += 1
            self._place_food()
            reward = 1
        else:
            self.snake.pop()
            reward = 0

        return self._get_state(), reward, False

    def _place_food(self):
        while True:
            self.food = [random.randint(1, self.height - 2),
                         random.randint(1, self.width - 2)]
            if self.food not in self.snake:
                break

    def _get_state(self):
        # Create a simple representation of the game state
        state = np.zeros((self.height, self.width), dtype=int)
        for segment in self.snake:
            state[segment[0], segment[1]] = 1
        state[self.food[0], self.food[1]] = 2
        return state

    def render(self, window):
        window.clear()
        self._draw_boundary(window)
        for segment in self.snake:
            window.addch(segment[0], segment[1], curses.ACS_CKBOARD)
        window.addch(self.food[0], self.food[1], curses.ACS_PI)
        window.addstr(self.height - 1, 1, f"Score: {self.score}")
        window.refresh()

    def _draw_boundary(self, window):
        for i in range(self.width):
            window.addch(0, i, curses.ACS_HLINE)
            if i < self.width - 1:
                window.addch(self.height - 1, i, curses.ACS_HLINE)
        for i in range(self.height):
            window.addch(i, 0, curses.ACS_VLINE)
            if i < self.height - 1:
                window.addch(i, self.width - 1, curses.ACS_VLINE)
        window.addch(0, 0, curses.ACS_ULCORNER)
        window.addch(0, self.width - 1, curses.ACS_URCORNER)
        window.addch(self.height - 1, 0, curses.ACS_LLCORNER)
        window.addch(self.height - 1, self.width - 1, curses.ACS_LRCORNER)

def play_game(stdscr):
    curses.curs_set(0)
    sh, sw = stdscr.getmaxyx()
    game = SnakeGame(height=20, width=20)

    if sh < game.height + 2 or sw < game.width + 2:
        stdscr.addstr(0, 0, "Terminal window too small. Please resize and try again.")
        stdscr.refresh()
        stdscr.getch()
        return

    window = curses.newwin(game.height + 2, game.width + 2, (sh - game.height) // 2, (sw - game.width) // 2)
    window.keypad(1)
    window.timeout(100)

    state = game.reset()
    done = False

    while not done:
        key = window.getch()
        if key == curses.KEY_UP:
            action = 0
        elif key == curses.KEY_DOWN:
            action = 1
        elif key == curses.KEY_LEFT:
            action = 2
        elif key == curses.KEY_RIGHT:
            action = 3
        else:
            action = -1

        if action != -1:
            state, reward, done = game.step(action)

        game.render(window)
        window.addstr(0, 1, f"Score: {game.score}")

    window.addstr(game.height // 2, game.width // 2 - 5, "GAME OVER")
    window.refresh()
    window.getch()

def train_agent(stdscr):
    curses.curs_set(0)
    sh, sw = stdscr.getmaxyx()
    game = SnakeGame(height=20, width=20)

    if sh < game.height + 2 or sw < game.width + 2:
        stdscr.addstr(0, 0, "Terminal window too small. Please resize and try again.")
        stdscr.refresh()
        stdscr.getch()
        return

    window = curses.newwin(game.height + 2, game.width + 2, (sh - game.height) // 2, (sw - game.width) // 2)
    window.keypad(1)
    window.timeout(100)

    agent = QLearningAgent(state_size=(game.height, game.width), action_size=4)

    episodes = 1000
    for episode in range(episodes):
        state = game.reset()
        total_reward = 0
        done = False
        step_count = 0

        while not done:
            action = agent.get_action(state)
            next_state, reward, done = game.step(action)
            agent.update(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            step_count += 1

            if step_count % 5 == 0:  # Update the screen every 5 steps
                game.render(window)
                window.addstr(0, 1, f"Episode: {episode + 1}/{episodes}, Score: {game.score}")
                curses.napms(50)  # Pause for 50 milliseconds

        print(f"Episode: {episode + 1}, Score: {game.score}")

    window.getch()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Snake Game")
    parser.add_argument('--train', action='store_true', help="Train the Q-learning agent")
    args = parser.parse_args()

    if args.train:
        curses.wrapper(train_agent)
    else:
        curses.wrapper(play_game)