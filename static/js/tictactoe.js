/**
 * Tic-Tac-Toe Client-Side Script
 * Handles board interaction, move dispatch to Flask API, and score tracking.
 */

let board = ["", "", "", "", "", "", "", "", ""];
let currentPlayer = "X";
let isGameOver = false;
let scores = { x: 0, tie: 0, o: 0 };

const cells = document.querySelectorAll(".ttt-cell");
const statusBanner = document.getElementById("ttt-status");
const modeSelect = document.getElementById("ttt-mode");
const diffSelect = document.getElementById("ttt-difficulty");
const diffGroup = document.getElementById("difficulty-group");
const resetBtn = document.getElementById("ttt-reset-btn");
const labelPlayerO = document.getElementById("label-player-o");

const scoreXElem = document.getElementById("score-x");
const scoreTieElem = document.getElementById("score-tie");
const scoreOElem = document.getElementById("score-o");

// 1. Initialize Cell Click Listeners
cells.forEach(cell => {
    cell.addEventListener("click", () => {
        const index = parseInt(cell.getAttribute("data-index"));
        handleCellClick(index);
    });
});

// 2. Mode Change Listener (vs AI or 2-Player)
modeSelect.addEventListener("change", () => {
    const mode = modeSelect.value;
    if (mode === "ai") {
        diffGroup.style.display = "flex";
        labelPlayerO.textContent = "Computer (O)";
    } else {
        diffGroup.style.display = "none";
        labelPlayerO.textContent = "Player O";
    }
    resetGame();
});

// 3. Reset Button Listener
resetBtn.addEventListener("click", resetGame);

// 4. Handle Move
async function handleCellClick(index) {
    if (board[index] !== "" || isGameOver) {
        return;
    }

    const mode = modeSelect.value;
    const difficulty = diffSelect.value;

    // Provide immediate visual feedback for player click
    board[index] = currentPlayer;
    renderBoard();

    statusBanner.textContent = "Processing move...";

    try {
        const response = await fetch("/api/tictactoe/move", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                board: board,
                move: index,
                difficulty: difficulty,
                mode: mode,
                current_player: currentPlayer
            })
        });

        const data = await response.json();
        if (data.error) {
            statusBanner.textContent = data.error;
            return;
        }

        board = data.board;
        renderBoard();

        // Check if there is a winner or tie
        if (data.winner) {
            handleGameOver(data.winner);
        } else {
            if (mode === "pvp") {
                currentPlayer = (currentPlayer === "X") ? "O" : "X";
                statusBanner.textContent = `Player ${currentPlayer}'s Turn`;
            } else {
                statusBanner.textContent = "Your turn (Player X)";
            }
        }
    } catch (err) {
        console.error("Error communicating with server:", err);
        statusBanner.textContent = "Server connection error.";
    }
}

// 5. Render Board State to DOM
function renderBoard() {
    cells.forEach((cell, i) => {
        cell.textContent = board[i];
        cell.classList.remove("cell-x", "cell-o");
        if (board[i] === "X") cell.classList.add("cell-x");
        if (board[i] === "O") cell.classList.add("cell-o");
    });
}

// 6. Game Over Resolution
function handleGameOver(winner) {
    isGameOver = true;
    statusBanner.classList.remove("win", "loss", "tie");

    if (winner === "Tie") {
        scores.tie++;
        scoreTieElem.textContent = scores.tie;
        statusBanner.textContent = "It's a Tie Game!";
        statusBanner.classList.add("tie");
    } else if (winner === "X") {
        scores.x++;
        scoreXElem.textContent = scores.x;
        statusBanner.textContent = modeSelect.value === "ai" ? "🎉 You Won! Excellent move." : "🎉 Player X Wins!";
        statusBanner.classList.add("win");
    } else if (winner === "O") {
        scores.o++;
        scoreOElem.textContent = scores.o;
        statusBanner.textContent = modeSelect.value === "ai" ? "🤖 Computer (O) Won! Try again." : "🎉 Player O Wins!";
        statusBanner.classList.add(modeSelect.value === "ai" ? "loss" : "win");
    }
}

// 7. Reset Game State
function resetGame() {
    board = ["", "", "", "", "", "", "", "", ""];
    currentPlayer = "X";
    isGameOver = false;
    statusBanner.classList.remove("win", "loss", "tie");
    statusBanner.textContent = modeSelect.value === "ai" ? "Player X's Turn (You)" : "Player X's Turn";
    renderBoard();
}
