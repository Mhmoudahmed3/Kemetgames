"""
Tic-Tac-Toe Game Logic
Simple, beginner-friendly implementation with win detection and AI.
"""
import random


WINNING_COMBINATIONS = [
    # Rows
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    # Columns
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    # Diagonals
    (0, 4, 8), (2, 4, 6)
]


def create_board():
    """Return an empty 3x3 board represented as a list of 9 strings."""
    return ["" for _ in range(9)]


def get_available_moves(board):
    """Return a list of empty cell indices (0-8)."""
    return [i for i, cell in enumerate(board) if cell == ""]


def check_winner(board):
    """
    Check if someone won or if the game ended in a tie.
    Returns: 'X', 'O', 'Tie', or None (game still in progress).
    """
    for a, b, c in WINNING_COMBINATIONS:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]

    # If no winner and no empty cells left, it's a tie
    if "" not in board:
        return "Tie"

    return None


def get_ai_move(board, difficulty="medium"):
    """
    Determine the AI's move (as 'O') based on the chosen difficulty.
    """
    available = get_available_moves(board)
    if not available:
        return None

    # Easy: Pick completely at random
    if difficulty == "easy":
        return random.choice(available)

    # Medium: Try to win, then try to block player ('X'), otherwise pick smart
    if difficulty == "medium":
        # 1. Check if AI can win in the next move
        for move in available:
            temp = list(board)
            temp[move] = "O"
            if check_winner(temp) == "O":
                return move

        # 2. Check if player would win in the next move, and block them
        for move in available:
            temp = list(board)
            temp[move] = "X"
            if check_winner(temp) == "X":
                return move

        # 3. Take the center if available
        if 4 in available:
            return 4

        # 4. Take any corner
        corners = [c for c in [0, 2, 6, 8] if c in available]
        if corners:
            return random.choice(corners)

        # 5. Take whatever is left
        return random.choice(available)

    # Unbeatable: Minimax algorithm
    if difficulty == "unbeatable":
        best_score = -float("inf")
        best_move = available[0]

        for move in available:
            board[move] = "O"
            score = _minimax(board, 0, False)
            board[move] = ""
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    return random.choice(available)


def _minimax(board, depth, is_maximizing):
    """
    Minimax recursive evaluation function.
    AI is maximizing ('O'), player is minimizing ('X').
    """
    winner = check_winner(board)
    if winner == "O":
        return 10 - depth
    elif winner == "X":
        return depth - 10
    elif winner == "Tie":
        return 0

    available = get_available_moves(board)

    if is_maximizing:
        max_eval = -float("inf")
        for move in available:
            board[move] = "O"
            evaluation = _minimax(board, depth + 1, False)
            board[move] = ""
            max_eval = max(max_eval, evaluation)
        return max_eval
    else:
        min_eval = float("inf")
        for move in available:
            board[move] = "X"
            evaluation = _minimax(board, depth + 1, True)
            board[move] = ""
            min_eval = min(min_eval, evaluation)
        return min_eval
