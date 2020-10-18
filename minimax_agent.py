from host import GO
import numpy as np
from read import readInput
from sys import maxsize
from write import writeOutput
import random

BOARD_SIZE = 5
DEPTH = 4  # minimax tree depth

EMPTY_BOARD = [[0 for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]
ALL_PLACES = [(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)]
CHILD_ITER = ALL_PLACES.copy()
CHILD_ITER.append((-1, -1))


# class Node2:
#     def __init__(self, current_board, parent_board, player, move_count=None):
#         self.childNodes = []
#         self.currentBoard = current_board   # current board status
#         self.parentBoard = parent_board # the previous board status
#         self.moveCount = move_count # the total number of moves so far
#         self.player = player    # player to make a move
#         self.action = "PASS"  # PASS OR MOVE
#         self.move = None # next move: (x, y);

class Node:
    def __init__(self, go_board, player, parent=None):
        self.go_board = go_board
        # self.child_nodes = []
        self.player = player
        # self.action = "MOVE"
        self.move = None  # next move: (x, y);
        self.parent = parent


# class Board:
#     def __init__(self, state=None):
#         if state is None:
#             self.state = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.int)
#         else:
#             self.state = state.copy()
#
#
# class MinimaxTree:
#     """
#     max_depth is the
#     """
#
#     def __init__(self, max_depth, root, player):
#         self.maxDepth = max_depth
#         self.root = root
#         self.player = player


def game_is_over(node):
    if node.parent is None:
        return False
    if node.go_board.n_move >= node.go_board.max_move:
        return True
    # Means two consecutive PASSes
    if node.go_board.compare_board(node.go_board.board, node.go_board.previous_board) and \
            node.go_board.compare_board(node.parent.go_board.board, node.parent.go_board.previous_board):
        return True
    return False


def opponent_last_move(board1, board2):
    diff = np.subtract(board1, board2)
    non_zero = np.nonzero(diff)
    if len(non_zero[0]) == 0:
        return -1, -1
    else:
        return non_zero[0][0], non_zero[1][0]


def detect_neighbor(board, i, j):
    neighbors = []
    # Detect borders and add neighbor coordinates
    if i > 0: neighbors.append((i - 1, j))
    if i < len(board) - 1: neighbors.append((i + 1, j))
    if j > 0: neighbors.append((i, j - 1))
    if j < len(board) - 1: neighbors.append((i, j + 1))
    return neighbors


def detect_neighbor_ally(board, i, j):
    neighbors = detect_neighbor(board, i, j)  # Detect neighbors
    group_allies = []
    # Iterate through neighbors
    for piece in neighbors:
        # Add to allies list if having the same color
        if board[piece[0]][piece[1]] == board[i][j]:
            group_allies.append(piece)
    return group_allies


def ally_dfs(board, i, j):
    stack = [(i, j)]  # stack for DFS serach
    ally_members = []  # record allies positions during the search
    while stack:
        piece = stack.pop()
        ally_members.append(piece)
        neighbor_allies = detect_neighbor_ally(board, piece[0], piece[1])
        for ally in neighbor_allies:
            if ally not in stack and ally not in ally_members:
                stack.append(ally)
    return ally_members
    print()


def find_all_liberties(board, i, j):
    """
    returns a list of the unoccupied places around the stone (i,j) and its allies
    :param board:
    :param i:
    :param j:
    :return:
    """
    liberties = []
    ally_members = ally_dfs(board, i, j)
    for member in ally_members:
        neighbors = detect_neighbor(board, member[0], member[1])
        for piece in neighbors:
            # If there is empty space around a piece, it has liberty
            if board[piece[0]][piece[1]] == 0:
                liberties.append((piece[0], piece[1]))
    # If none of the pieces in a allied group has an empty space, it has no liberty
    return liberties


def find_player_liberties(board, player):
    """
    :param board:
    :param player:
    :return: a set of all liberty places surrounding the player's stones on the board
    """
    explored = set()
    all_liberties = set()
    for place in ALL_PLACES:
        if place in explored:
            continue
        if board[place[0]][place[1]] == player:
            explored.add(place)
            neighbors = set(ally_dfs(board, place[0], place[1]))
            explored.update(neighbors)
            liberties = set(find_all_liberties(board, place[0], place[1]))
            all_liberties.update(liberties)

    return all_liberties

def minimax_pruning(node, depth, is_maximizing, alpha, beta):
    """
    :param node: current node
    :param go_board: current go board of the node
    :param depth: current depth of the minimax tree
    :param is_maximizing: if maximizing is true
    :param alpha:
    :param beta:
    :return:
    """

    if game_is_over(node) or depth >= DEPTH:
        if is_maximizing:
            my_player = node.player  # my player is always the max player
        else:
            my_player = 3 - node.player
        # if game_is_over(node):
        #     if node.go_board.judge_winner() == my_player:
        #         u_val = 100
        #     else:
        #         u_val = -100
        # else:  # game is not over yet, using heuristic evaluation
        player_liberty = len(find_player_liberties(node.go_board.board, node.player))
        opponent_liberty = len(find_player_liberties(node.go_board.board, 3 - node.player))
        u_val = 100*(node.go_board.score(my_player) - node.go_board.score(3 - my_player)) \
            + player_liberty - opponent_liberty
        return u_val, None  # utility function of the leaf

    if node.go_board.n_move < 10:
        # last_move = opponent_last_move(node.go_board.previous_board, node.go_board.board)
        # places = find_all_liberties(node.go_board.board, last_move[0], last_move[1])
        places = find_player_liberties(node.go_board.board, 3 - node.player)
        places.add((-1, -1))
    else:
        places = []
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if node.go_board.board[i][j] == 0:
                    places.append((i, j))
        places.append((-1, -1))
        random.shuffle(places)

    # print(places)

    if is_maximizing:
        bestVal = -maxsize
        # random.shuffle(CHILD_ITER)
        for place in places:
            # Case 1: do not make a move, child node's board is the same as its parent's
            if place == (-1, -1):  # (-1, -1) is defined as PASS
                go_board_c = node.go_board.copy_board()
                go_board_c.n_move += 1  # increment the n of moves
                child_node = Node(go_board_c, 3 - node.player, node)
            # Case 2: make a valid move, board changes
            elif node.go_board.valid_place_check(place[0], place[1], node.player):
                go_board_n = node.go_board.copy_board()
                go_board_n.n_move += 1
                # place stone in the board, update boards and previous_board
                go_board_n.place_chess(place[0], place[1], node.player)
                go_board_n.remove_died_pieces(3 - node.player)  # remove the dead stones in the board
                child_node = Node(go_board_n, 3 - node.player, node)
            # Case 3: placement is invalid, thus no child node should be generated
            else:
                continue
            value, move = minimax_pruning(child_node, depth + 1, False, alpha, beta)
            if value > bestVal:
                bestMove = place

            bestVal = max(bestVal, value)
            alpha = max(alpha, bestVal)
            if beta <= alpha:
                # print("pruning1")
                break
        return bestVal, bestMove
    else:
        bestVal = maxsize
        # random.shuffle(CHILD_ITER)
        for place in places:
            # Case 1: do not make a move, child node's board is the same as its parent's
            if place == (-1, -1):  # (-1, -1) is defined as PASS
                go_board_c = node.go_board.copy_board()
                go_board_c.n_move += 1  # increment the n of moves
                child_node = Node(go_board_c, 3 - node.player, node)
            # Case 2: make a valid move, board changes
            elif node.go_board.valid_place_check(place[0], place[1], node.player):
                go_board_n = node.go_board.copy_board()
                go_board_n.n_move += 1
                # place stone in the board, update boards and previous_board
                go_board_n.place_chess(place[0], place[1], node.player)
                go_board_n.remove_died_pieces(3 - node.player)  # remove the dead stones in the board
                child_node = Node(go_board_n, 3 - node.player, node)
            # Case 3: placement is invalid, thus no child node should be generated
            else:
                continue
            value, move = minimax_pruning(child_node, depth + 1, True, alpha, beta)
            if value < bestVal:
                bestMove = place

            bestVal = min(bestVal, value)
            beta = min(beta, bestVal)
            if beta <= alpha:
                # print("pruning2")
                break
        return bestVal, bestMove


def write_n_moves(num, path="n_moves.txt"):
    with open(path, 'w') as f:
        f.write(str(num))


def read_n_moves(path="n_moves.txt"):
    with open(path, 'r') as f:
        line = f.readline()
        return int(line)


if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    # piece_type, previous_board, board = readInput(N, "init/input.txt")
    # print(opponent_last_move(previous_board, board))
    go = GO(BOARD_SIZE)
    go.set_board(piece_type, previous_board, board)
    # print(previous_board)
    # print(board)

    action = None
    retVal = None
    # check to see if this is the initial board
    if go.compare_board(previous_board, EMPTY_BOARD) and go.compare_board(board, EMPTY_BOARD):
        n_moves = 0
        go.n_move = 0
        action = (2, 2)

    # this is the board after first move
    elif go.compare_board(previous_board, EMPTY_BOARD) and not go.compare_board(board, EMPTY_BOARD):
        n_moves = 1
        go.n_move = 1
        if board[2][2] == 0:
            action = (2, 2)
    else:
        n_moves = read_n_moves() + 1
        go.n_move = n_moves

    print("n of moves", n_moves)

    #
    if action is None:
        first_node = Node(go, piece_type)
        retVal, move = minimax_pruning(first_node, 0, True, -maxsize, maxsize)
        if move == (-1, -1):
            action = "PASS"
        else:
            action = move

    write_n_moves(n_moves + 1)
    writeOutput(action)

    # root = Node(board, previous_board, piece_type, 0)
    # nodesToExpand = [root]
    # tree = MinimaxTree(DEPTH, root, piece_type)
    """
    build the game tree
    """
    # while len(nodesToExpand) > 0:
    #     node = nodesToExpand.pop()
    #     moveCount = node.moveCount
    #     go = GO(BOARD_SIZE)
    #     go.set_board(node.player, node.parentBoard, node.currentBoard)
    #
    #
    #     for i in range(BOARD_SIZE):
    #         for j in range(BOARD_SIZE):
    #             if go.valid_place_check(i, j, node.player):
    #                 go_copy = go.copy_board()
    #                 go_copy.place_chess(i, j)

    if retVal is not None:
        print(retVal, move)
