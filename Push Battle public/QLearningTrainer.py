import judge_engine
from PushBattle import Game, PLAYER1, PLAYER2, EMPTY, BOARD_SIZE, NUM_PIECES, _torus

from QLearningAgent import QLearningAgent  # Import the QLearningAgent class

class QLearningTrainer:
    def __init__(self, num_games, q_table_filename="q_table.txt"):
        self.num_games = num_games
        self.q_table_filename = q_table_filename

    def train(self):
        # Load the Q-learning agent
        agent = QLearningAgent(player=PLAYER1, q_table_filename=self.q_table_filename)

        for i in range(self.num_games):
            print(f"Training game {i+1}/{self.num_games}")
            judge_engine.main()

        # Save the Q-table after training
        agent.save_q_table()

if __name__ == "__main__":
    # Start training
    trainer = QLearningTrainer(num_games=300)
    trainer.train()
