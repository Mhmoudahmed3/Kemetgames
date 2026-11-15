/**
 * Playing Cards Client-Side Script
 * Manages tab switching, High-Low streak guessing, and Blackjack dealing & hitting.
 */

// ----------------------------------------------------
// Tab Switching
// ----------------------------------------------------
function switchCardTab(tabName) {
    const hlView = document.getElementById("view-highlow");
    const bjView = document.getElementById("view-blackjack");
    const hlBtn = document.getElementById("tab-btn-hl");
    const bjBtn = document.getElementById("tab-btn-bj");

    if (tabName === "highlow") {
        hlView.style.display = "flex";
        bjView.style.display = "none";
        hlBtn.classList.add("active");
        bjBtn.classList.remove("active");
    } else {
        hlView.style.display = "none";
        bjView.style.display = "flex";
        hlBtn.classList.remove("active");
        bjBtn.classList.add("active");
    }
}

// ----------------------------------------------------
// High-Low Game
// ----------------------------------------------------
let hlStreak = 0;
let hlBest = 0;

const hlCardElem = document.getElementById("hl-card");
const hlRankElem = document.getElementById("hl-rank");
const hlRankBrElem = document.getElementById("hl-rank-br");
const hlSuitElem = document.getElementById("hl-suit");
const hlSuitBrElem = document.getElementById("hl-suit-br");
const hlCenterSuitElem = document.getElementById("hl-center-suit");

const hlStreakElem = document.getElementById("hl-streak");
const hlBestElem = document.getElementById("hl-best");
const hlStatusElem = document.getElementById("hl-status");

const btnHigher = document.getElementById("btn-higher");
const btnLower = document.getElementById("btn-lower");
const hlResetBtn = document.getElementById("hl-reset-btn");

btnHigher.addEventListener("click", () => makeHighLowGuess("higher"));
btnLower.addEventListener("click", () => makeHighLowGuess("lower"));
hlResetBtn.addEventListener("click", startHighLow);

async function startHighLow() {
    try {
        const response = await fetch("/api/cards/highlow/start", { method: "POST" });
        const data = await response.json();

        hlStreak = 0;
        hlStreakElem.textContent = hlStreak;
        hlStatusElem.classList.remove("win", "loss", "tie");
        hlStatusElem.textContent = data.message;

        renderCard(hlCardElem, data.current_card);
        btnHigher.disabled = false;
        btnLower.disabled = false;
    } catch (err) {
        console.error("High-Low start error:", err);
    }
}

async function makeHighLowGuess(guess) {
    try {
        const response = await fetch("/api/cards/highlow/guess", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ guess: guess })
        });

        const data = await response.json();
        renderCard(hlCardElem, data.current_card);

        hlStreak = data.streak;
        hlStreakElem.textContent = hlStreak;
        if (hlStreak > hlBest) {
            hlBest = hlStreak;
            hlBestElem.textContent = hlBest;
        }

        hlStatusElem.classList.remove("win", "loss", "tie");
        hlStatusElem.textContent = data.message;

        if (data.game_over) {
            hlStatusElem.classList.add("loss");
            btnHigher.disabled = true;
            btnLower.disabled = true;
        } else {
            hlStatusElem.classList.add("win");
        }
    } catch (err) {
        console.error("High-Low guess error:", err);
    }
}

function renderCard(cardElement, card) {
    cardElement.classList.remove("red", "black");
    cardElement.classList.add(card.color);

    cardElement.querySelector(".card-rank").textContent = card.rank;
    cardElement.querySelector(".card-corner.bottom-right .card-rank").textContent = card.rank;
    cardElement.querySelector(".card-suit").textContent = card.suit;
    cardElement.querySelector(".card-corner.bottom-right .card-suit").textContent = card.suit;
    cardElement.querySelector(".card-center").textContent = card.suit;
}

// ----------------------------------------------------
// Blackjack Game
// ----------------------------------------------------
let bjChips = 100;
let currentBet = 10;
let isHandActive = false;

const bjChipsElem = document.getElementById("bj-chips");
const bjStatusElem = document.getElementById("bj-status");
const dealerCardsElem = document.getElementById("dealer-cards");
const playerCardsElem = document.getElementById("player-cards");
const dealerScoreElem = document.getElementById("dealer-score");
const playerScoreElem = document.getElementById("player-score");

const bjDealBtn = document.getElementById("bj-deal-btn");
const btnHit = document.getElementById("btn-hit");
const btnStand = document.getElementById("btn-stand");

bjDealBtn.addEventListener("click", dealBlackjackHand);
btnHit.addEventListener("click", hitBlackjack);
btnStand.addEventListener("click", standBlackjack);

async function dealBlackjackHand() {
    if (bjChips < currentBet) {
        bjStatusElem.textContent = "Out of chips! Reloading bankroll to $100...";
        bjChips = 100;
        bjChipsElem.textContent = bjChips;
    }

    bjChips -= currentBet;
    bjChipsElem.textContent = bjChips;

    try {
        const response = await fetch("/api/cards/blackjack/deal", { method: "POST" });
        const data = await response.json();

        isHandActive = true;
        bjStatusElem.classList.remove("win", "loss", "tie");
        bjStatusElem.textContent = data.message;

        // Render Player Cards
        renderHand(playerCardsElem, data.player_hand);
        playerScoreElem.textContent = data.player_score;

        // Render Dealer with 1 face-up and 1 face-down card
        dealerCardsElem.innerHTML = "";
        dealerCardsElem.appendChild(createCardDOM(data.dealer_visible_card));
        const hiddenCard = document.createElement("div");
        hiddenCard.classList.add("playing-card", "face-down");
        hiddenCard.id = "dealer-hidden-card";
        dealerCardsElem.appendChild(hiddenCard);

        dealerScoreElem.textContent = "?";

        if (data.game_over) {
            // Natural Blackjack!
            bjChips += currentBet * 2.5;
            bjChipsElem.textContent = bjChips;
            bjStatusElem.classList.add("win");
            endBlackjackRound();
        } else {
            btnHit.disabled = false;
            btnStand.disabled = false;
            bjDealBtn.disabled = true;
        }
    } catch (err) {
        console.error("Blackjack deal error:", err);
    }
}

async function hitBlackjack() {
    if (!isHandActive) return;

    try {
        const response = await fetch("/api/cards/blackjack/hit", { method: "POST" });
        const data = await response.json();

        renderHand(playerCardsElem, data.player_hand);
        playerScoreElem.textContent = data.player_score;
        bjStatusElem.textContent = data.message;

        if (data.game_over) {
            bjStatusElem.classList.add("loss");
            endBlackjackRound();
        }
    } catch (err) {
        console.error("Blackjack hit error:", err);
    }
}

async function standBlackjack() {
    if (!isHandActive) return;

    try {
        const response = await fetch("/api/cards/blackjack/stand", { method: "POST" });
        const data = await response.json();

        // Reveal dealer's full hand
        renderHand(dealerCardsElem, data.dealer_hand);
        dealerScoreElem.textContent = data.dealer_score;

        bjStatusElem.classList.remove("win", "loss", "tie");
        bjStatusElem.textContent = data.message;

        if (data.outcome === "win") {
            bjChips += currentBet * 2;
            bjStatusElem.classList.add("win");
        } else if (data.outcome === "push") {
            bjChips += currentBet;
            bjStatusElem.classList.add("tie");
        } else {
            bjStatusElem.classList.add("loss");
        }

        bjChipsElem.textContent = bjChips;
        endBlackjackRound();
    } catch (err) {
        console.error("Blackjack stand error:", err);
    }
}

function endBlackjackRound() {
    isHandActive = false;
    btnHit.disabled = true;
    btnStand.disabled = true;
    bjDealBtn.disabled = false;
}

function renderHand(container, hand) {
    container.innerHTML = "";
    hand.forEach(card => {
        container.appendChild(createCardDOM(card));
    });
}

function createCardDOM(card) {
    const cardDiv = document.createElement("div");
    cardDiv.classList.add("playing-card", card.color);

    cardDiv.innerHTML = `
        <div class="card-corner top-left">
            <span class="card-rank">${card.rank}</span>
            <span class="card-suit">${card.suit}</span>
        </div>
        <div class="card-center">${card.suit}</div>
        <div class="card-corner bottom-right">
            <span class="card-rank">${card.rank}</span>
            <span class="card-suit">${card.suit}</span>
        </div>
    `;
    return cardDiv;
}

// Start High-Low on page load
startHighLow();
