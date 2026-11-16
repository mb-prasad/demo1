import random
from collections import deque
from typing import Deque, List, Optional, Tuple

Point = Tuple[int, int]

DIRECTIONS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}
OPPOSITES = {"up": "down", "down": "up", "left": "right", "right": "left"}


class SnakeGame:
    """Game logic for snake on a width x height grid. It has no I/O, so any front end can drive it."""

    def __init__(
        self,
        width: int = 20,
        height: int = 20,
        rng: Optional[random.Random] = None,
    ) -> None:
        if width < 3 or height < 3:
            raise ValueError("board must be at least 3x3")
        self.width = width
        self.height = height
        self.rng = rng or random.Random()
        # The snake starts with three cells in a row, heading right. The head is first.
        start_x, start_y = width // 2, height // 2
        self.snake: Deque[Point] = deque(
            [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        )
        self.direction = "right"
        self.score = 0
        self.game_over = False
        self.food: Optional[Point] = self._place_food()

    def change_direction(self, direction: str) -> bool:
        """Turn the snake. Returns False if the turn is a reversal, which is ignored."""
        if direction not in DIRECTIONS:
            raise ValueError(f"unknown direction: {direction}")
        if direction == OPPOSITES[self.direction]:
            return False
        self.direction = direction
        return True

    def step(self) -> None:
        """Advance the game by one tick."""
        if self.game_over:
            return
        dx, dy = DIRECTIONS[self.direction]
        head_x, head_y = self.snake[0]
        new_head = (head_x + dx, head_y + dy)
        x, y = new_head

        grows = new_head == self.food
        # The tail moves away this tick unless the snake grows, so the head may enter the old tail cell.
        body = list(self.snake) if grows else list(self.snake)[:-1]
        if not (0 <= x < self.width and 0 <= y < self.height) or new_head in body:
            self.game_over = True
            return

        self.snake.appendleft(new_head)
        if grows:
            self.score += 1
            self.food = self._place_food()
            if self.food is None:
                # The snake fills the whole board, so there is nowhere left to place food.
                self.game_over = True
        else:
            self.snake.pop()

    def _place_food(self) -> Optional[Point]:
        """Pick a random empty cell for the food, or return None if the board is full."""
        occupied = set(self.snake)
        free: List[Point] = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in occupied
        ]
        if not free:
            return None
        return self.rng.choice(free)
