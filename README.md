# Mini Arcade

#### Video Demo: [Insert YouTube Link Here]

#### Description:
Mini Arcade is a web-based gaming hub developed as a final project for Harvard's **CS50: Introduction to Computer Science**. The project brings together four classic tabletop and arcade games—**Tic-Tac-Toe**, **Connect 4**, **Rock-Paper-Scissors (with Lizard-Spock)**, and a **Playing Cards Suite (High-Low & Blackjack)**—into a unified, responsive web application.

The goal of this project was to synthesize the core web concepts taught in CS50 (HTML, CSS, JavaScript, and Python with Flask) by creating interactive, state-driven browser games powered by clean server-side logic and algorithmic AI opponents.

---

### Project Structure & Files

The project follows a standard, beginner-friendly Flask architecture:

```
games website/
├── app.py                  # Main Flask application with page and API routes
├── requirements.txt        # Python package dependencies (Flask, gunicorn)
├── render.yaml             # Render cloud deployment configuration
├── Procfile                # Web service process command for production
├── README.md               # Project documentation and write-up
├── start.bat               # Simple Windows launcher script
│
├── games/                  # Pure Python game logic modules
│   ├── __init__.py         # Package initializer
│   ├── tictactoe.py        # 3x3 board win detection and Minimax AI
│   ├── connect4.py         # 6x7 grid drop gravity and 4-in-a-row detection
│   ├── rps.py              # Classic & Lizard-Spock cyclic graph rules
│   └── cards.py            # 52-card deck, Fisher-Yates shuffle, High-Low & Blackjack
│
├── templates/              # Jinja2 HTML templates
│   ├── layout.html         # Base template with responsive navbar and footer
│   ├── index.html          # Arcade lobby with game cards and descriptions
│   ├── tictactoe.html      # Tic-Tac-Toe board and controls
│   ├── connect4.html       # Connect 4 grid and drop buttons
│   ├── rps.html            # Rock-Paper-Scissors battle arena and choices
│   ├── cards.html          # High-Low streak and Blackjack card tables
│   └── about.html          # CS50 technical overview and architecture details
│
└── static/                 # Static frontend assets
    ├── css/
    │   └── style.css       # Unified modern arcade styling and responsive layout
    └── js/
        ├── tictactoe.js    # Client-side board events and API communication
        ├── connect4.js     # Column click listeners and disc rendering
        ├── rps.js          # Gesture buttons, animations, and match formats
        └── cards.js        # Tab switching, High-Low guessing, and Blackjack dealing
```

---

### Key Game Modules & Algorithms

1. **Tic-Tac-Toe (`games/tictactoe.py`):**
   - The game board is represented as a 1D list of 9 elements.
   - Winner detection checks 8 predefined winning lines (3 rows, 3 columns, 2 diagonals).
   - In addition to an easy random bot and a medium tactical bot, an **unbeatable AI** is implemented using the **Minimax algorithm**, recursively scoring board states with depth discounting to always force a win or tie.

2. **Connect 4 (`games/connect4.py`):**
   - Implements a 6-row by 7-column matrix.
   - A gravity drop mechanism finds the lowest available row in any selected column.
   - Win validation performs horizontal, vertical, and diagonal scans (both positive and negative slopes) for 4 consecutive matching discs.

3. **Rock-Paper-Scissors (`games/rps.py`):**
   - Implements both the classic 3-gesture game and the 5-gesture **Rock-Paper-Scissors-Lizard-Spock** variation popularized by *The Big Bang Theory*.
   - Uses a dictionary lookup mapping winning pairs to human-readable explanations (e.g., *"Spock vaporizes rock"*).

4. **Card Games Suite (`games/cards.py`):**
   - Generates a standard 52-card deck with suits, ranks, values, and colors.
   - Shuffles cards using Python's pseudo-random distribution.
   - **High-Low:** Players guess whether the next drawn card is higher or lower, building a streak.
   - **Blackjack:** Features dealer play (drawing to 17), dynamic Ace valuation (counting Aces as 11, then reducing to 1 if the total hand exceeds 21), and hit/stand decisions.

---

### Design Decisions

* **Why Flask?** Flask is lightweight, transparent, and easy to understand compared to monolithic frameworks. It allows direct control over route handling and session data.
* **Why Separate Game Modules (`games/`)?** Keeping game mechanics separated from HTTP request handling makes the code modular, readable, and easy to unit test.
* **Why Vanilla JavaScript?** Using standard browser JavaScript (`fetch()`, `addEventListener`, DOM manipulation) avoids external frontend build tools (like React or Webpack) and reinforces foundational web programming.
* **Single-Page Feel with Multi-Page Navigation:** Each game has its own dedicated URL (`/tictactoe`, `/connect4`, etc.) using template inheritance, while the gameplay itself is fast and asynchronous without full-page reloads.

---

### How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Mhmoudahmed3/Kemetgames.git
   cd "games website"
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server:**
   ```bash
   python app.py
   ```

5. Open your web browser and navigate to `http://127.0.0.1:5000`.
