"""
Connect 4 Game Logic
Standard 7 columns by 6 rows grid with gravity drop, win checking, and AI.
"""
import random

ROWS = 6
COLS = 7


def create_board():
    """Create a 6x7 grid filled with zeros (0 = empty, 1 = Red/Player, 2 = Yellow/AI)."""
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]


def get_valid_locations(board):
    """Return a list of column numbers (0-6) that are not completely full."""
    valid_cols = []
    for col in range(COLS):
        # A column is valid if the top row (row 0) is empty
        if board[0][col] == 0:
            valid_cols.append(col)
    return valid_cols


def get_next_open_row(board, col):
    """
    Find the lowest empty row in the given column (gravity effect).
    Returns row index (0-5), or -1 if the column is full.
    """
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == 0:
            return row
    return -1


def drop_piece(board, col, piece):
    """
    Drop a piece (1 or 2) into the specified column.
    Returns the row index where it landed, or -1 if invalid.
    """
    row = get_next_open_row(board, col)
    if row != -1:
        board[row][col] = piece
        return row
    return -1


def check_winner(board, piece):
    """
    Check if the given piece has 4 in a row horizontally, vertically, or diagonally.
    """
    # 1. Horizontal check
    for r in range(ROWS):
        for c in range(COLS - 3):
            if (board[r][c] == piece and
                board[r][c + 1] == piece and
                board[r][c + 2] == piece and
                board[r][c + 3] == piece):
                return True

    # 2. Vertical check
    for r in range(ROWS - 3):
        for c in range(COLS):
            if (board[r][c] == piece and
                board[r + 1][c] == piece and
                board[r + 2][c] == piece and
                board[r + 3][c] == piece):
                return True

    # 3. Positively sloped diagonal (up-right)
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if (board[r][c] == piece and
                board[r - 1][c + 1] == piece and
                board[r - 2][c + 2] == piece and
                board[r - 3][c + 3] == piece):
                return True

    # 4. Negatively sloped diagonal (down-right)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if (board[r][c] == piece and
                board[r + 1][c + 1] == piece and
                board[r + 2][c + 2] == piece and
                board[r + 3][c + 3] == piece):
                return True

    return False


def is_board_full(board):
    """Return True if no more pieces can be dropped."""
    return len(get_valid_locations(board)) == 0


def get_ai_move(board, ai_piece=2, player_piece=1, difficulty="medium"):
    """
    Choose a column for the AI.
    - Easy: Random valid column.
    - Medium: Win if possible, block player's win, else prioritize center.
    """
    valid_cols = get_valid_locations(board)
    if not valid_cols:
        return None

    if difficulty == "easy":
        return random.choice(valid_cols)

    # 1. Check if AI can win on next move
    for col in valid_cols:
        row = get_next_open_row(board, col)
        board[row][col] = ai_piece
        if check_winner(board, ai_piece):
            board[row][col] = 0
            return col
        board[row][col] = 0

    # 2. Check if player would win on next move, and block them
    for col in valid_cols:
        row = get_next_open_row(board, col)
        board[row][col] = player_piece
        if check_winner(board, player_piece):
            board[row][col] = 0
            return col
        board[row][col] = 0

    # 3. Prefer center column (col 3), then adjacent (cols 2, 4)
    priority_order = [3, 2, 4, 1, 5, 0, 6]
    for col in priority_order:
        if col in valid_cols:
            return col

    return random.choice(valid_cols)
