from copy import deepcopy

class GO:
    def __init__(self, n):
        self.size = n
        self.X_move = True
        self.died_pieces = []
        self.n_move = 0
        self.max_move = n * n - 1
        self.komi = n/2
        self.board = [[]]
        self.previous_board = [[]]

    def init_board(self, n):
        board = [[0 for x in range(n)] for y in range(n)]
        self.board = board
        self.previous_board = deepcopy(board)

    def set_board(self, piece_type, previous_board, board):
        for i in range(self.size):
            for j in range(self.size):
                if previous_board[i][j] == piece_type and board[i][j] != piece_type:
                    self.died_pieces.append((i, j))
        self.previous_board = previous_board
        self.board = board

    def compare_board(self, board1, board2):
        for i in range(self.size):
            for j in range(self.size):
                if board1[i][j] != board2[i][j]:
                    return False
        return True

    def copy_board(self):
        return deepcopy(self)

    def detect_neighbor(self, i, j):
        board = self.board
        neighbors = []
        if i > 0: neighbors.append((i-1, j))
        if i < len(board) - 1: neighbors.append((i+1, j))
        if j > 0: neighbors.append((i, j-1))
        if j < len(board) - 1: neighbors.append((i, j+1))
        return neighbors

    def detect_neighbor_ally(self, i, j):
        board = self.board
        neighbors = self.detect_neighbor(i, j)
        group_allies = []
        for piece in neighbors:
            if board[piece[0]][piece[1]] == board[i][j]:
                group_allies.append(piece)
        return group_allies

    def ally_dfs(self, i, j):
        stack = [(i, j)]
        ally_members = []
        while stack:
            piece = stack.pop()
            ally_members.append(piece)
            neighbor_allies = self.detect_neighbor_ally(piece[0], piece[1])
            for ally in neighbor_allies:
                if ally not in stack and ally not in ally_members:
                    stack.append(ally)
        return ally_members

    def find_liberty(self, i, j):
        board = self.board
        ally_members = self.ally_dfs(i, j)
        for member in ally_members:
            neighbors = self.detect_neighbor(member[0], member[1])
            for piece in neighbors:
                if board[piece[0]][piece[1]] == 0:
                    return True
        return False

    def find_died_pieces(self, piece_type):
        board = self.board
        died_pieces = []

        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] == piece_type:
                    if not self.find_liberty(i, j):
                        died_pieces.append((i,j))
        return died_pieces

    def remove_died_pieces(self, piece_type):
        died_pieces = self.find_died_pieces(piece_type)
        if not died_pieces: return []
        self.remove_certain_pieces(died_pieces)
        return died_pieces

    def remove_certain_pieces(self, positions):
        board = self.board
        for piece in positions:
            board[piece[0]][piece[1]] = 0
        self.update_board(board)

    def place_chess(self, i, j, piece_type):
        board = self.board

        valid_place = self.valid_place_check(i, j, piece_type)
        if not valid_place:
            return False
        self.previous_board = deepcopy(board)
        board[i][j] = piece_type
        self.update_board(board)
        return True

    def valid_place_check(self, i, j, piece_type):
        board = self.board

        # Check if the place is in the board range
        if not (0 <= i < len(board)):
            return False
        if not (0 <= j < len(board)):
            return False

        if board[i][j] != 0:
            return False

        test_go = self.copy_board()
        test_board = test_go.board

        test_board[i][j] = piece_type
        test_go.update_board(test_board)
        if test_go.find_liberty(i, j):
            return True

        test_go.remove_died_pieces(3 - piece_type)
        if not test_go.find_liberty(i, j):
            return False

        else:
            if self.died_pieces and self.compare_board(self.previous_board, test_go.board):
                return False
        return True
        
    def update_board(self, new_board):
        self.board = new_board

    def game_end(self, piece_type, action="MOVE"):

        if self.n_move >= self.max_move:
            return True

        if self.compare_board(self.previous_board, self.board) and action == "PASS":
            return True
        return False

    def score(self, piece_type):

        board = self.board
        cnt = 0
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == piece_type:
                    cnt += 1
        return cnt          

    def judge_winner(self):

        cnt_1 = self.score(1)
        cnt_2 = self.score(2)
        if cnt_1 > cnt_2 + self.komi:
            return 1
        elif cnt_1 < cnt_2 + self.komi:
            return 2
        else:
            return 0
