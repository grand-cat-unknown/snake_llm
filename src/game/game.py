import curses
import random
import time
import json
import os

# Define constant game board dimensions
GAME_HEIGHT = 30  # Reduced from 40
GAME_WIDTH = 30 # Reduced from 40

def draw_boundary(w):
    for i in range(GAME_WIDTH):
        w.addch(0, i, curses.ACS_HLINE)
        if i < GAME_WIDTH - 1:
            w.addch(GAME_HEIGHT - 1, i, curses.ACS_HLINE)
    for i in range(GAME_HEIGHT):
        w.addch(i, 0, curses.ACS_VLINE)
        if i < GAME_HEIGHT - 1:
            w.addch(i, GAME_WIDTH - 1, curses.ACS_VLINE)
    w.addch(0, 0, curses.ACS_ULCORNER)
    w.addch(0, GAME_WIDTH - 1, curses.ACS_URCORNER)
    w.addch(GAME_HEIGHT - 1, 0, curses.ACS_LLCORNER)

def show_game_over(w, score):
    w.clear()
    game_over_text = "GAME OVER"
    w.addstr(GAME_HEIGHT // 2, (GAME_WIDTH - len(game_over_text)) // 2, game_over_text)
    w.refresh()
    time.sleep(3)  # Show the game over screen for 3 seconds

def save_game_state(action, snake, food, score):
    game_state = {
        "action": action,
        "snake": snake,
        "food": food,
        "score": score,
        "board_height": GAME_HEIGHT,
        "board_width": GAME_WIDTH
    }
    
    # Create a directory to store the game states if it doesn't exist
    os.makedirs("game_states", exist_ok=True)
    
    # Save the game state to a JSON file
    with open(f"game_states/state_{int(time.time())}.json", "w") as f:
        json.dump(game_state, f)

def main(stdscr):
    curses.curs_set(0)
    sh, sw = stdscr.getmaxyx()
    
    # Check if the terminal window is large enough
    if sh < GAME_HEIGHT + 2 or sw < GAME_WIDTH + 2:
        stdscr.clear()
        stdscr.addstr(0, 0, "Terminal window too small. Please resize and try again.")
        stdscr.addstr(1, 0, f"Minimum size: {GAME_WIDTH + 2}x{GAME_HEIGHT + 2}")
        stdscr.addstr(2, 0, f"Current size: {sw}x{sh}")
        stdscr.refresh()
        stdscr.getch()
        return

    w = curses.newwin(GAME_HEIGHT, GAME_WIDTH, (sh - GAME_HEIGHT) // 2, (sw - GAME_WIDTH) // 2)
    w.keypad(1)
    w.nodelay(1)  # Make getch non-blocking

    w.clear()
    draw_boundary(w)

    snake_x = GAME_WIDTH // 4
    snake_y = GAME_HEIGHT // 2
    snake = [
        [snake_y, snake_x],
        [snake_y, snake_x - 1],
        [snake_y, snake_x - 2]
    ]

    food = [GAME_HEIGHT // 2, GAME_WIDTH // 2]
    w.addch(food[0], food[1], curses.ACS_PI)

    key = curses.KEY_RIGHT
    score = 0

    move_time = 0
    move_delay = 0.1  # Adjust this value to change the snake's speed

    action_map = {
        curses.KEY_UP: "UP",
        curses.KEY_DOWN: "DOWN",
        curses.KEY_LEFT: "LEFT",
        curses.KEY_RIGHT: "RIGHT"
    }

    while True:
        current_time = time.time()

        # Handle input
        next_key = w.getch()
        if next_key != -1:
            if (key == curses.KEY_DOWN and next_key != curses.KEY_UP) or \
               (key == curses.KEY_UP and next_key != curses.KEY_DOWN) or \
               (key == curses.KEY_LEFT and next_key != curses.KEY_RIGHT) or \
               (key == curses.KEY_RIGHT and next_key != curses.KEY_LEFT):
                key = next_key

        # Move the snake at a constant speed
        if current_time - move_time > move_delay:
            move_time = current_time

            new_head = [snake[0][0], snake[0][1]]

            if key == curses.KEY_DOWN:
                new_head[0] += 1
            if key == curses.KEY_UP:
                new_head[0] -= 1
            if key == curses.KEY_LEFT:
                new_head[1] -= 1
            if key == curses.KEY_RIGHT:
                new_head[1] += 1

            snake.insert(0, new_head)

            if (snake[0][0] <= 0 or snake[0][0] >= GAME_HEIGHT - 1 or
                snake[0][1] <= 0 or snake[0][1] >= GAME_WIDTH - 1 or
                snake[0] in snake[1:]):
                break

            if snake[0] == food:
                score += 1
                food = None
                while food is None:
                    nf = [
                        random.randint(1, GAME_HEIGHT - 2),
                        random.randint(1, GAME_WIDTH - 2)
                    ]
                    food = nf if nf not in snake else None
                w.addch(food[0], food[1], curses.ACS_PI)
            else:
                tail = snake.pop()
                w.addch(tail[0], tail[1], ' ')

            w.addch(snake[0][0], snake[0][1], curses.ACS_CKBOARD)
            w.addstr(GAME_HEIGHT - 1, 1, f"Score: {score}")
            w.refresh()

            # Save the game state after each move
            save_game_state(action_map.get(key, "NONE"), snake, food, score)

        # Add a small sleep to prevent high CPU usage
        time.sleep(0.01)

    show_game_over(w, score)

if __name__ == "__main__":
    curses.wrapper(main)
