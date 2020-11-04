import numpy as np
import pickle

WIN_REWARD = 1.0
LOSS_REWARD = 0.0

def encode(board):
    return ''.join([str(board[i][j]) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)])



class QLearner:
    GAME_NUM = 100000

    def __init__(self, alpha=0.7, gamma=0.9, initial_value=0.5, side=None):
        self.side = side
        self.alpha = alpha
        self.gamma = gamma
        self.q_values = {}
        self.history_states = []
        self.initial_value = initial_value

    def set_side(self, side):
        self.side = side

    def read_tables(self, path='QTables.pickle'):
        with open(path, 'rb') as f:
            QTables = pickle.load(f)
        return QTables

    def select_best_move(self, board):

