/**
 * Rock-Paper-Scissors Client-Side Script
 * Manages move selections, reveal animations, scorekeeping, and rule modes.
 */

const choiceIcons = {
    rock: "✊",
    paper: "✋",
    scissors: "✌️",
    lizard: "🦎",
    spock: "🖖"
};

let scores = { player: 0, cpu: 0, tie: 0, streak: 0 };
let isBattling = false;

const modeSelect = document.getElementById("rps-mode");
const formatSelect = document.getElementById("rps-format");
const resetBtn = document.getElementById("rps-reset-btn");

const playerIconElem = document.getElementById("player-choice-icon");
const playerNameElem = document.getElementById("player-choice-name");
const cpuIconElem = document.getElementById("cpu-choice-icon");
const cpuNameElem = document.getElementById("cpu-choice-name");

const playerScoreElem = document.getElementById("rps-player-score");
const cpuScoreElem = document.getElementById("rps-cpu-score");
const tieScoreElem = document.getElementById("rps-tie-score");
const streakElem = document.getElementById("rps-streak");
const statusBanner = document.getElementById("rps-status");

const extraButtons = document.querySelectorAll(".rps-extra");
const classicRulesText = document.getElementById("rules-classic-text");
const lsRulesText = document.getElementById("rules-ls-text");

// 1. Variant Selector (Classic vs Lizard-Spock)
modeSelect.addEventListener("change", () => {
    const mode = modeSelect.value;
    if (mode === "lizard-spock") {
        extraButtons.forEach(btn => btn.style.display = "flex");
        classicRulesText.style.display = "none";
        lsRulesText.style.display = "block";
    } else {
        extraButtons.forEach(btn => btn.style.display = "none");
        classicRulesText.style.display = "block";
        lsRulesText.style.display = "none";
    }
    resetScores();
});

// 2. Format Selector & Reset
formatSelect.addEventListener("change", resetScores);
resetBtn.addEventListener("click", resetScores);

// 3. Choice Button Listeners
const rpsBtns = document.querySelectorAll(".rps-btn");
rpsBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        if (isBattling) return;
        const choice = btn.getAttribute("data-choice");
        playRound(choice);
    });
});

// 4. Play Round with Animated Reveal
async function playRound(playerChoice) {
    isBattling = true;
    const mode = modeSelect.value;

    // Show suspense animation
    playerIconElem.textContent = "✊";
    cpuIconElem.textContent = "✊";
    playerNameElem.textContent = "Rock...";
    cpuNameElem.textContent = "Paper...";
    statusBanner.textContent = "3... 2... 1... Shoot!";

    try {
        const response = await fetch("/api/rps/play", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                choice: playerChoice,
                mode: mode
            })
        });

        const data = await response.json();

        // Brief delay for dramatic reveal
        setTimeout(() => {
            playerIconElem.textContent = choiceIcons[data.player] || "❓";
            playerNameElem.textContent = capitalize(data.player);

            cpuIconElem.textContent = choiceIcons[data.computer] || "❓";
            cpuNameElem.textContent = capitalize(data.computer);

            // Update scores & banner
            statusBanner.classList.remove("win", "loss", "tie");
            statusBanner.textContent = data.message;

            if (data.outcome === "win") {
                scores.player++;
                scores.streak++;
                statusBanner.classList.add("win");
            } else if (data.outcome === "loss") {
                scores.cpu++;
                scores.streak = 0;
                statusBanner.classList.add("loss");
            } else {
                scores.tie++;
                statusBanner.classList.add("tie");
            }

            updateScoreDisplay();
            checkMatchFormat();
            isBattling = false;
        }, 350);

    } catch (err) {
        console.error("RPS error:", err);
        statusBanner.textContent = "Server communication error.";
        isBattling = false;
    }
}

// 5. Update Scoreboard Numbers
function updateScoreDisplay() {
    playerScoreElem.textContent = scores.player;
    cpuScoreElem.textContent = scores.cpu;
    tieScoreElem.textContent = scores.tie;
    streakElem.textContent = scores.streak;
}

// 6. Check Best of 3 / Best of 5 Win Conditions
function checkMatchFormat() {
    const format = formatSelect.value;
    let target = 0;

    if (format === "bo3") target = 2;
    if (format === "bo5") target = 3;

    if (target > 0) {
        if (scores.player >= target) {
            statusBanner.textContent = `🏆 MATCH OVER: You won the series (${scores.player} - ${scores.cpu})!`;
            statusBanner.classList.add("win");
        } else if (scores.cpu >= target) {
            statusBanner.textContent = `💀 MATCH OVER: Computer won the series (${scores.cpu} - ${scores.player})!`;
            statusBanner.classList.add("loss");
        }
    }
}

// 7. Reset Scoreboard
function resetScores() {
    scores = { player: 0, cpu: 0, tie: 0, streak: 0 };
    updateScoreDisplay();

    playerIconElem.textContent = "❓";
    cpuIconElem.textContent = "❓";
    playerNameElem.textContent = "Waiting...";
    cpuNameElem.textContent = "Waiting...";

    statusBanner.classList.remove("win", "loss", "tie");
    statusBanner.textContent = "Choose your move below to begin!";
}

function capitalize(str) {
    if (!str) return "";
    return str.charAt(0).toUpperCase() + str.slice(1);
}
