"""
Mini Arcade - CS50 Final Project
A beginner-friendly web gaming platform built with Flask, HTML, CSS, JavaScript, and Python.
"""
from flask import Flask, render_template, request, jsonify, session
import secrets
from games import tictactoe, connect4, rps, cards

app = Flask(__name__)
# Generate a secret key for session tracking
app.secret_key = secrets.token_hex(16)


# ----------------------------------------------------
# Page Routes (Frontend Views)
# ----------------------------------------------------

@app.route("/")
def index():
    """Render the homepage / arcade lobby."""
    return render_template("index.html")


@app.route("/tictactoe")
def page_tictactoe():
    """Render the Tic-Tac-Toe game page."""
    return render_template("tictactoe.html")


@app.route("/connect4")
def page_connect4():
    """Render the Connect 4 game page."""
    return render_template("connect4.html")


@app.route("/rps")
def page_rps():
    """Render the Rock-Paper-Scissors game page."""
    return render_template("rps.html")


@app.route("/cards")
def page_cards():
    """Render the Playing Cards (High-Low & Blackjack) page."""
    return render_template("cards.html")


@app.route("/about")
def page_about():
    """Render the project overview and CS50 documentation page."""
    return render_template("about.html")


# ----------------------------------------------------
# Tic-Tac-Toe API Endpoints
# ----------------------------------------------------

@app.route("/api/tictactoe/move", methods=["POST"])
def api_tictactoe_move():
    """
    Handle a Tic-Tac-Toe move.
    Receives current board, player move index, difficulty, and mode.
    """
    data = request.get_json() or {}
    board = data.get("board", [""] * 9)
    move = data.get("move")
    difficulty = data.get("difficulty", "medium")
    mode = data.get("mode", "ai")  # 'ai' or 'pvp'
    current_player = data.get("current_player", "X")

    # Validate move
    if move is None or move < 0 or move > 8 or board[move] != "":
        return jsonify({"error": "Invalid move"}), 400

    # 1. Apply player's move
    board[move] = current_player
    winner = tictactoe.check_winner(board)

    ai_move = None
    # 2. If game is not over and playing vs AI, make the AI move
    if mode == "ai" and winner is None:
        ai_move = tictactoe.get_ai_move(board, difficulty)
        if ai_move is not None:
            board[ai_move] = "O"
            winner = tictactoe.check_winner(board)

    return jsonify({
        "board": board,
        "winner": winner,
        "ai_move": ai_move
    })


# ----------------------------------------------------
# Connect 4 API Endpoints
# ----------------------------------------------------

@app.route("/api/connect4/drop", methods=["POST"])
def api_connect4_drop():
    """
    Handle a disc drop into a Connect 4 column.
    """
    data = request.get_json() or {}
    board = data.get("board", connect4.create_board())
    col = data.get("col")
    difficulty = data.get("difficulty", "medium")
    vs_ai = data.get("vs_ai", True)
    player_piece = data.get("piece", 1)  # 1 = Red, 2 = Yellow

    if col is None or col < 0 or col >= connect4.COLS:
        return jsonify({"error": "Invalid column"}), 400

    row = connect4.drop_piece(board, col, player_piece)
    if row == -1:
        return jsonify({"error": "Column is full"}), 400

    winner = None
    if connect4.check_winner(board, player_piece):
        winner = player_piece
    elif connect4.is_board_full(board):
        winner = "Tie"

    ai_col = None
    ai_row = None

    # If vs AI and game is still ongoing, AI drops piece 2
    if vs_ai and winner is None:
        ai_col = connect4.get_ai_move(board, ai_piece=2, player_piece=1, difficulty=difficulty)
        if ai_col is not None:
            ai_row = connect4.drop_piece(board, ai_col, 2)
            if connect4.check_winner(board, 2):
                winner = 2
            elif connect4.is_board_full(board):
                winner = "Tie"

    return jsonify({
        "board": board,
        "player_row": row,
        "ai_col": ai_col,
        "ai_row": ai_row,
        "winner": winner,
        "is_full": connect4.is_board_full(board)
    })


# ----------------------------------------------------
# Rock-Paper-Scissors API Endpoints
# ----------------------------------------------------

@app.route("/api/rps/play", methods=["POST"])
def api_rps_play():
    """
    Play a single round of Rock-Paper-Scissors or RPS-Lizard-Spock.
    """
    data = request.get_json() or {}
    choice = data.get("choice", "")
    mode = data.get("mode", "classic")

    result = rps.play_round(choice, mode)
    return jsonify(result)


# ----------------------------------------------------
# Playing Cards API Endpoints (High-Low & Blackjack)
# ----------------------------------------------------

@app.route("/api/cards/highlow/start", methods=["POST"])
def api_highlow_start():
    """Start a fresh High-Low game session."""
    game = cards.high_low_new_game()
    session["hl_deck"] = game["deck"]
    session["hl_current"] = game["current_card"]
    session["hl_streak"] = 0

    return jsonify({
        "current_card": game["current_card"],
        "streak": 0,
        "message": game["message"]
    })


@app.route("/api/cards/highlow/guess", methods=["POST"])
def api_highlow_guess():
    """Process a High-Low guess ('higher' or 'lower')."""
    data = request.get_json() or {}
    guess = data.get("guess", "higher")

    deck = session.get("hl_deck", cards.create_deck())
    current_card = session.get("hl_current", deck.pop())
    streak = session.get("hl_streak", 0)

    result = cards.high_low_guess(deck, current_card, guess, streak)

    # Update session state
    session["hl_deck"] = deck
    session["hl_current"] = result["current_card"]
    session["hl_streak"] = result["streak"]

    return jsonify({
        "current_card": result["current_card"],
        "streak": result["streak"],
        "game_over": result["game_over"],
        "outcome": result["outcome"],
        "message": result["message"]
    })


@app.route("/api/cards/blackjack/deal", methods=["POST"])
def api_blackjack_deal():
    """Deal a new hand of Blackjack."""
    game = cards.blackjack_new_game()
    session["bj_deck"] = game["deck"]
    session["bj_player"] = game["player_hand"]
    session["bj_dealer"] = game["dealer_hand"]

    return jsonify({
        "player_hand": game["player_hand"],
        "player_score": game["player_score"],
        "dealer_visible_card": game["dealer_hand"][0],
        "game_over": game["game_over"],
        "message": game["message"]
    })


@app.route("/api/cards/blackjack/hit", methods=["POST"])
def api_blackjack_hit():
    """Player draws a card in Blackjack."""
    deck = session.get("bj_deck", cards.create_deck())
    player_hand = session.get("bj_player", [])

    result = cards.blackjack_hit(deck, player_hand)
    session["bj_deck"] = deck
    session["bj_player"] = player_hand

    return jsonify(result)


@app.route("/api/cards/blackjack/stand", methods=["POST"])
def api_blackjack_stand():
    """Player stands in Blackjack; dealer resolves hand."""
    deck = session.get("bj_deck", cards.create_deck())
    player_hand = session.get("bj_player", [])
    dealer_hand = session.get("bj_dealer", [])

    result = cards.blackjack_stand(deck, player_hand, dealer_hand)
    session["bj_deck"] = deck
    session["bj_dealer"] = result["dealer_hand"]

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
