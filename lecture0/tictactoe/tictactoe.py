"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    empty_board = [[EMPTY,  EMPTY, EMPTY],
                   [EMPTY, EMPTY, EMPTY],
                   [EMPTY, EMPTY, EMPTY]]

    global rows
    rows = len(empty_board)

    global columns
    columns = len(empty_board[0])

    return empty_board


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    count_X = 0
    count_O = 0

    for i in range(rows):
        for j in range(columns):
            if board[i][j] == X:
                count_X += 1
            elif board[i][j] == O:
                count_O += 1

    return X if (count_X <= count_O) else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    empty_cells = set()

    for i in range(rows):
        for j in range(columns):
            if board[i][j] == EMPTY:
                empty_cells.add((i, j))

    return empty_cells


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    new_board = deepcopy(board)

    if new_board[i][j] is not EMPTY:
        raise Exception("Invalid action.")
    else:
        new_board[i][j] = player(new_board)

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # Horizontal
    for i in range(rows):
        if all(j == board[i][0] for j in board[i]):
            return board[i][0]

    # Vertical
    for i in range(columns):
        if all(board[j][i] == board[0][i] for j in range(columns)):
            return board[0][i]

    # Diagonal
    if all(board[j][j] == board[0][0] for j in range(columns)):
        return board[0][0]
    elif all(board[2-j][j] == board[2][0] for j in range(columns)):
        return board[2][0]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if (winner(board) or len(actions(board)) == 0):
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if (winner(board) == X):
        return 1
    elif (winner(board) == O):
        return -1
    elif len(actions(board)) == 0:
        return 0


def minimax_value(board, player, alpha, beta):
    if terminal(board):
        return utility(board)

    if player == X:
        v = -math.inf

        for action in actions(board):
            v = max(v, minimax_value(result(board, action), O, alpha, beta))

            alpha = max(alpha, v)

            if alpha >= beta:
                break

        return v
    else:
        v = math.inf

        for action in actions(board):
            v = min(v, minimax_value(result(board, action), X, alpha, beta))

            beta = min(beta, v)

            if alpha >= beta:
                break

        return v


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    optimail_move = None

    alpha = -math.inf
    beta = math.inf

    if player(board) is X:
        v = -math.inf

        for action in actions(board):
            new_v = minimax_value(result(board, action), O, alpha, beta)

            if new_v > v:
                v = new_v
                optimail_move = action
    else:
        v = math.inf

        for action in actions(board):
            new_v = minimax_value(result(board, action), X, alpha, beta)

            if new_v < v:
                v = new_v
                optimail_move = action

    return optimail_move

