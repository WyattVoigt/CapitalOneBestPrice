import random
import numpy as np
import os
from PushBattle import Game, PLAYER1, PLAYER2, EMPTY, BOARD_SIZE, NUM_PIECES, _torus

class QLearningAgent:
    def __init__(self, player=PLAYER1, alpha=0.1, gamma=0.9, epsilon=0.1, q_table_filename="q_table.txt"):
        self.player = player
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.q_table = {}  # Q-table
        self.q_table_filename = q_table_filename
        self.load_q_table()  # Load the Q-table if it exists

    def get_possible_moves(self, game):
        """Returns list of all possible moves in current state."""
        moves = []
        current_pieces = game.p1_pieces if game.current_player == PLAYER1 else game.p2_pieces

        if current_pieces < NUM_PIECES:
            # placement moves
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    if game.board[r][c] == EMPTY:
                        moves.append((r, c))
        else:
            # movement moves
            for r0 in range(BOARD_SIZE):
                for c0 in range(BOARD_SIZE):
                    if game.board[r0][c0] == game.current_player:
                        for r1 in range(BOARD_SIZE):
                            for c1 in range(BOARD_SIZE):
                                if game.board[r1][c1] == EMPTY:
                                    moves.append((r0, c0, r1, c1))
        return moves

    def get_best_move(self, game):
        """Chooses the best move based on Q-values."""
        state = self.state_to_str(game)
        possible_moves = self.get_possible_moves(game)

        if np.random.rand() < self.epsilon:
            # Exploration: choose a random move
            return random.choice(possible_moves)

        # Exploitation: choose the best move based on Q-values
        q_values = [self.q_table.get((state, move), 0) for move in possible_moves]
        max_q_value = max(q_values)
        best_moves = [move for move, q in zip(possible_moves, q_values) if q == max_q_value]
        return random.choice(best_moves)

    def update_q_table(self, state, action, reward, next_state):
        """Updates the Q-table using the Q-learning formula."""
        best_next_q = max(self.q_table.get((next_state, next_action), 0) for next_action in self.get_possible_moves(Game.from_dict(eval(next_state))))
        self.q_table[(state, action)] = (1 - self.alpha) * self.q_table.get((state, action), 0) + self.alpha * (reward + self.gamma * best_next_q)

    def state_to_str(self, game):
        """Converts the game board state to a string for Q-table indexing."""
        return str(game.board)

    def save_q_table(self):
        """Saves the Q-table to a file."""
        with open(self.q_table_filename, 'w') as f:
            f.write(str(self.q_table))

    def load_q_table(self):
        """Loads the Q-table from a file."""
        if os.path.exists(self.q_table_filename):
            with open(self.q_table_filename, 'r') as f:
                self.q_table = eval(f.read())
