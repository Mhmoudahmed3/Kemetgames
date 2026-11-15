/**
 * Connect 4 Client-Side Script
 * Manages 6x7 board rendering, column drop clicks, animations, and game state.
 */

const ROWS = 6;
const COLS = 7;

let board = [];
let currentPiece = 1; // 1 = Red (Player 1), 2 = Yellow (AI / Player 2)
let isGameOver = false;
let scores = { red: 0, tie: 0, yellow: 0 };

const boardElem = document.getElementById("c4-board");
const dropRowElem = document.getElementById("c4-drop-row");
const statusBanner = document.getElementById("c4-status");
const modeSelect = document.getElementById("c4-mode");
const diffSelect = document.getElementById("c4-difficulty");
const diffGroup = document.getElementById("c4-diff-group");
const resetBtn = document.getElementById("c4-reset-btn");
const labelYellow = document.getElementById("label-player-yellow");

const scoreRedElem = document.getElementById("score-red");
const scoreTieElem = document.getElementById("score-c4-tie");
const scoreYellowElem = document.getElementById("score-yellow");

// 1. Initialize Empty Board Matrix & DOM Elements
function initBoard() {
    board = [];
    boardElem.innerHTML = "";

    for (let r = 0; r < ROWS; r++) {
        const rowArr = [];
        for (let c = 0; c < COLS; c++) {
            rowArr.push(0);
            const slot = document.createElement("div");
            slot.classList.add("c4-slot");
            slot.setAttribute("id", `slot-${r}-${c}`);
            slot.setAttribute("data-col", c);
            slot.addEventListener("click", () => handleColumnClick(c));
            boardElem.appendChild(slot);
        }
        board.push(rowArr);
    }
}

// 2. Column Drop Button Listeners
const dropBtns = document.querySelectorAll(".c4-drop-btn");
dropBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        const col = parseInt(btn.getAttribute("data-col"));
        handleColumnClick(col);
    });
});

// 3. Mode Change (vs AI or 2-Player Local)
modeSelect.addEventListener("change", () => {
    const mode = modeSelect.value;
    if (mode === "ai") {
        diffGroup.style.display = "flex";
        labelYellow.textContent = "🟡 Yellow (AI)";
    } else {
        diffGroup.style.display = "none";
        labelYellow.textContent = "🟡 Yellow (P2)";
    }
    resetGame();
});

// 4. Reset Button Listener
resetBtn.addEventListener("click", resetGame);

// 5. Handle Column Drop Click
async function handleColumnClick(col) {
    if (isGameOver) return;

    // Check if column is already full (row 0 occupied)
    if (board[0][col] !== 0) {
        statusBanner.textContent = "Column is full! Choose another column.";
        return;
    }

    const vsAI = (modeSelect.value === "ai");
    const difficulty = diffSelect.value;

    statusBanner.textContent = "Dropping disc...";

    try {
        const response = await fetch("/api/connect4/drop", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                board: board,
                col: col,
                difficulty: difficulty,
                vs_ai: vsAI,
                piece: currentPiece
            })
        });

        const data = await response.json();
        if (data.error) {
            statusBanner.textContent = data.error;
            return;
        }

        board = data.board;
        renderBoard();

        if (data.winner) {
            handleGameOver(data.winner);
        } else {
            if (!vsAI) {
                currentPiece = (currentPiece === 1) ? 2 : 1;
                const turnColor = (currentPiece === 1) ? "🔴 Red's Turn" : "🟡 Yellow's Turn";
                statusBanner.textContent = turnColor;
            } else {
                statusBanner.textContent = "🔴 Your Turn (Red)";
            }
        }
    } catch (err) {
        console.error("Connect 4 drop error:", err);
        statusBanner.textContent = "Server communication error.";
    }
}

// 6. Update Slot Classes in DOM
function renderBoard() {
    for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
            const slot = document.getElementById(`slot-${r}-${c}`);
            slot.classList.remove("piece-red", "piece-yellow");
            if (board[r][c] === 1) {
                slot.classList.add("piece-red");
            } else if (board[r][c] === 2) {
                slot.classList.add("piece-yellow");
            }
        }
    }
}

// 7. Game Over Resolution
function handleGameOver(winner) {
    isGameOver = true;
    statusBanner.classList.remove("win", "loss", "tie");

    if (winner === "Tie") {
        scores.tie++;
        scoreTieElem.textContent = scores.tie;
        statusBanner.textContent = "Board is full! It's a Tie!";
        statusBanner.classList.add("tie");
    } else if (winner === 1) {
        scores.red++;
        scoreRedElem.textContent = scores.red;
        statusBanner.textContent = modeSelect.value === "ai" ? "🎉 You Won! 4 in a row!" : "🎉 Red Wins!";
        statusBanner.classList.add("win");
    } else if (winner === 2) {
        scores.yellow++;
        scoreYellowElem.textContent = scores.yellow;
        statusBanner.textContent = modeSelect.value === "ai" ? "🟡 Yellow (AI) Won! Better luck next time." : "🎉 Yellow Wins!";
        statusBanner.classList.add(modeSelect.value === "ai" ? "loss" : "win");
    }
}

// 8. Reset Game
function resetGame() {
    initBoard();
    currentPiece = 1;
    isGameOver = false;
    statusBanner.classList.remove("win", "loss", "tie");
    statusBanner.textContent = "🔴 Red's Turn — Click any column to drop a disc!";
}

// Initial Board Load
initBoard();
