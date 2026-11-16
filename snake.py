"""Terminal snake game. Run with: python snake.py

Controls: arrow keys or WASD to steer, P to pause, R to restart, Q to quit.
Uses only the standard library (curses).
"""

import curses
import random
import time
from collections import deque

BOARD_WIDTH = 30
BOARD_HEIGHT = 20
STEP_SECONDS = 0.12

DIRECTIONS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}
OPPOSITE = {"up": "down", "down": "up", "left": "right", "right": "left"}


class Game:
    def __init__(self, width=BOARD_WIDTH, height=BOARD_HEIGHT, rng=None):
        self.width = width
        self.height = height
        self.rng = rng or random.Random()
        self.reset()

    def reset(self):
        cx, cy = self.width // 2, self.height // 2
        # The head is snake[0]; the snake starts three cells long, heading right.
        self.snake = deque([(cx, cy), (cx - 1, cy), (cx - 2, cy)])
        self.direction = "right"
        self.next_direction = "right"
        self.score = 0
        self.alive = True
        self.food = None
        self._place_food()

    def turn(self, direction):
        # Compare against the direction the snake is currently moving, so a
        # reversal can never be applied within a single step.
        if direction != OPPOSITE[self.direction]:
            self.next_direction = direction

    def step(self):
        if not self.alive:
            return
        self.direction = self.next_direction
        dx, dy = DIRECTIONS[self.direction]
        hx, hy = self.snake[0]
        head = (hx + dx, hy + dy)

        if not (0 <= head[0] < self.width and 0 <= head[1] < self.height):
            self.alive = False
            return

        ate = head == self.food
        tail = self.snake[-1]
        # The tail moves away this step unless we eat, so it is safe to move into it.
        if head in self.snake and not (head == tail and not ate):
            self.alive = False
            return

        self.snake.appendleft(head)
        if ate:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()

    def _place_food(self):
        free = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in self.snake
        ]
        self.food = self.rng.choice(free) if free else None


KEY_DIRECTIONS = {
    curses.KEY_UP: "up",
    curses.KEY_DOWN: "down",
    curses.KEY_LEFT: "left",
    curses.KEY_RIGHT: "right",
    ord("w"): "up",
    ord("s"): "down",
    ord("a"): "left",
    ord("d"): "right",
}


def draw(stdscr, game, paused):
    stdscr.erase()
    max_y, max_x = stdscr.getmaxyx()
    # Each cell is two characters wide so the board looks roughly square.
    board_w = game.width * 2 + 2
    board_h = game.height + 2
    if max_y < board_h + 2 or max_x < board_w:
        stdscr.addstr(0, 0, "Terminal too small for the board.")
        stdscr.refresh()
        return

    top, left = 1, 0
    stdscr.addstr(0, 0, f"Score: {game.score}")
    stdscr.addstr(top, left, "+" + "-" * (game.width * 2) + "+")
    stdscr.addstr(top + game.height + 1, left, "+" + "-" * (game.width * 2) + "+")
    for y in range(game.height):
        stdscr.addstr(top + 1 + y, left, "|")
        stdscr.addstr(top + 1 + y, left + board_w - 1, "|")

    if game.food is not None:
        fx, fy = game.food
        stdscr.addstr(top + 1 + fy, left + 1 + fx * 2, "*")
    for index, (x, y) in enumerate(game.snake):
        ch = "O" if index == 0 else "o"
        stdscr.addstr(top + 1 + y, left + 1 + x * 2, ch)

    footer = top + board_h
    if not game.alive:
        stdscr.addstr(footer, 0, "Game over! R to restart, Q to quit.")
    elif paused:
        stdscr.addstr(footer, 0, "Paused. P to resume, Q to quit.")
    else:
        stdscr.addstr(footer, 0, "Arrows/WASD to steer, P pause, Q quit.")
    stdscr.refresh()


def run(stdscr):
    curses.curs_set(0)
    stdscr.timeout(20)
    game = Game()
    paused = False
    last_step = time.monotonic()

    while True:
        key = stdscr.getch()
        if key in (ord("q"), ord("Q")):
            break
        if key in (ord("r"), ord("R")):
            game.reset()
            paused = False
            last_step = time.monotonic()
        elif key in (ord("p"), ord("P")):
            paused = not paused
        elif key in KEY_DIRECTIONS:
            game.turn(KEY_DIRECTIONS[key])

        now = time.monotonic()
        if not paused and game.alive and now - last_step >= STEP_SECONDS:
            game.step()
            last_step = now

        draw(stdscr, game, paused)


if __name__ == "__main__":
    curses.wrapper(run)
