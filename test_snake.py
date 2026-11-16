import random
import unittest

from snake import SnakeGame


class SnakeGameTests(unittest.TestCase):
    def make_game(self, width: int = 10, height: int = 10) -> SnakeGame:
        game = SnakeGame(width, height, rng=random.Random(0))
        game.food = (0, 0)  # park the food out of the way unless a test needs it
        return game

    def test_initial_state(self):
        game = self.make_game()
        self.assertEqual(list(game.snake), [(5, 5), (4, 5), (3, 5)])
        self.assertEqual(game.direction, "right")
        self.assertEqual(game.score, 0)
        self.assertFalse(game.game_over)

    def test_food_is_placed_on_empty_cell(self):
        game = SnakeGame(5, 5, rng=random.Random(1))
        self.assertIsNotNone(game.food)
        self.assertNotIn(game.food, game.snake)

    def test_moves_forward_without_growing(self):
        game = self.make_game()
        game.step()
        self.assertEqual(list(game.snake), [(6, 5), (5, 5), (4, 5)])
        self.assertFalse(game.game_over)

    def test_change_direction(self):
        game = self.make_game()
        self.assertTrue(game.change_direction("up"))
        game.step()
        self.assertEqual(game.snake[0], (5, 4))

    def test_reversal_is_ignored(self):
        game = self.make_game()
        self.assertFalse(game.change_direction("left"))
        self.assertEqual(game.direction, "right")

    def test_unknown_direction_raises(self):
        game = self.make_game()
        with self.assertRaises(ValueError):
            game.change_direction("diagonal")

    def test_eating_food_grows_and_scores(self):
        game = self.make_game()
        game.food = (6, 5)
        game.step()
        self.assertEqual(list(game.snake), [(6, 5), (5, 5), (4, 5), (3, 5)])
        self.assertEqual(game.score, 1)
        self.assertNotIn(game.food, game.snake)
        self.assertFalse(game.game_over)

    def test_wall_collision_ends_game(self):
        game = self.make_game(10, 10)
        game.snake = type(game.snake)([(9, 5), (8, 5), (7, 5)])
        game.step()
        self.assertTrue(game.game_over)

    def test_self_collision_ends_game(self):
        game = self.make_game()
        # A snake curled into a loop: moving down from (5, 5) lands on (5, 6).
        game.snake = type(game.snake)([(5, 5), (6, 5), (6, 6), (5, 6), (4, 6), (4, 5)])
        game.direction = "down"
        game.step()
        self.assertTrue(game.game_over)

    def test_moving_into_vacated_tail_is_allowed(self):
        game = self.make_game()
        # The head at (5, 5) moves down into (5, 6), which is the tail cell and is vacated this tick.
        game.snake = type(game.snake)([(5, 5), (4, 5), (4, 6), (5, 6)])
        game.direction = "down"
        game.step()
        self.assertFalse(game.game_over)
        self.assertEqual(game.snake[0], (5, 6))

    def test_step_after_game_over_does_nothing(self):
        game = self.make_game(10, 10)
        game.snake = type(game.snake)([(9, 5), (8, 5), (7, 5)])
        game.step()
        snapshot = list(game.snake)
        game.step()
        self.assertEqual(list(game.snake), snapshot)
        self.assertTrue(game.game_over)

    def test_board_full_ends_game(self):
        game = SnakeGame(3, 3, rng=random.Random(0))
        # Eight cells fill a 3x3 board. The head at (1, 1) eats the only free cell, (1, 2).
        game.snake = type(game.snake)([(1, 1), (0, 1), (0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (0, 2)])
        game.direction = "down"
        game.food = (1, 2)
        game.step()
        self.assertEqual(game.score, 1)
        self.assertIsNone(game.food)
        self.assertTrue(game.game_over)


if __name__ == "__main__":
    unittest.main()
