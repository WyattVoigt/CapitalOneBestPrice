import random
import copy
from PushBattle import Game, PLAYER1, PLAYER2, EMPTY, BOARD_SIZE, NUM_PIECES, _torus


class MinimaxAgent:
    def __init__(self, player=PLAYER1):
        self.player = player

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

    def simulate_move(self, game, move):
        """Simulates a move and returns the new game state."""
        new_game = copy.deepcopy(game)
        if len(move) == 2:  # placement move
            r, c = move
            new_game.board[r][c] = new_game.current_player
        else:  # movement move
            r0, c0, r1, c1 = move
            new_game.board[r0][c0] = EMPTY
            new_game.board[r1][c1] = new_game.current_player

        return new_game

    def minimax(self, game, depth, is_maximizing, alpha, beta):
        """Minimax algorithm implementation with alpha-beta pruning."""
        if game.check_winner() == PLAYER1:
            return 1 if self.player == PLAYER1 else -1
        elif game.check_winner() == PLAYER2:
            return 1 if self.player == PLAYER2 else -1
        elif game.check_winner() == EMPTY or depth == 0:
            return 0

        possible_moves = self.get_possible_moves(game)
        if is_maximizing:
            max_eval = float('-inf')
            for move in possible_moves:
                simulated_game = self.simulate_move(game, move)
                eval = self.minimax(simulated_game, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in possible_moves:
                simulated_game = self.simulate_move(game, move)
                eval = self.minimax(simulated_game, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self, game):
        print("finding best move")
        """Returns the best move using the Minimax algorithm with alpha-beta pruning."""
        best_move = None
        best_score = float('-inf') if self.player == game.current_player else float('inf')
        is_maximizing = self.player == game.current_player

        for move in self.get_possible_moves(game):
            print(move)
            simulated_game = self.simulate_move(game, move)
            score = self.minimax(simulated_game, 100, not is_maximizing, float('-inf'), float('inf'))
            if (is_maximizing and score > best_score) or (not is_maximizing and score < best_score):
                best_move = move
                best_score = score

        return best_move
