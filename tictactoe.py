from typing import List, Optional, Tuple

PLAYERS = ("X", "O")
SIZE = 3

# Every row, column and diagonal as (row, col) coordinates.
WIN_LINES: Tuple[Tuple[Tuple[int, int], ...], ...] = (
    ((0, 0), (0, 1), (0, 2)),
    ((1, 0), (1, 1), (1, 2)),
    ((2, 0), (2, 1), (2, 2)),
    ((0, 0), (1, 0), (2, 0)),
    ((0, 1), (1, 1), (2, 1)),
    ((0, 2), (1, 2), (2, 2)),
    ((0, 0), (1, 1), (2, 2)),
    ((0, 2), (1, 1), (2, 0)),
)


class TicTacToe:
    def __init__(self) -> None:
        # None marks an empty cell; otherwise the cell holds "X" or "O".
        self._board: List[List[Optional[str]]] = [
            [None] * SIZE for _ in range(SIZE)
        ]
        self._current_player: str = PLAYERS[0]

    @property
    def board(self) -> List[List[Optional[str]]]:
        # Return a copy so callers cannot change the game state directly.
        return [list(row) for row in self._board]

    @property
    def current_player(self) -> str:
        return self._current_player

    def play(self, row: int, col: int) -> None:
        if self.is_over():
            raise ValueError("game is already over")
        if not (0 <= row < SIZE and 0 <= col < SIZE):
            raise ValueError(f"cell ({row}, {col}) is out of range")
        if self._board[row][col] is not None:
            raise ValueError(f"cell ({row}, {col}) is already occupied")

        self._board[row][col] = self._current_player
        self._current_player = PLAYERS[1] if self._current_player == PLAYERS[0] else PLAYERS[0]

    def winner(self) -> Optional[str]:
        for line in WIN_LINES:
            first = self._board[line[0][0]][line[0][1]]
            if first is None:
                continue
            if all(self._board[r][c] == first for r, c in line):
                return first
        return None

    def is_draw(self) -> bool:
        return self.winner() is None and self._is_full()

    def is_over(self) -> bool:
        return self.winner() is not None or self._is_full()

    def status(self) -> str:
        """Return "in_progress", "X_wins", "O_wins" or "draw"."""
        winner = self.winner()
        if winner == "X":
            return "X_wins"
        if winner == "O":
            return "O_wins"
        if self._is_full():
            return "draw"
        return "in_progress"

    def _is_full(self) -> bool:
        return all(cell is not None for row in self._board for cell in row)
