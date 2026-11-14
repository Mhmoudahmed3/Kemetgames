"""Registry mapping all 15 game_type keys to their server-authoritative engines."""

from __future__ import annotations

from backend.base_game import BaseGame
from backend.games.backgammon_game import BackgammonGame
from backend.games.chess_game import ChessGame
from backend.games.connect4_game import Connect4Game
from backend.games.dominoes_game import DominoesGame
from backend.games.globe_game import GlobeGame
from backend.games.ludo_game import LudoGame
from backend.games.minesweeper_game import MinesweeperGame
from backend.games.monopoly_game import MonopolyGame
from backend.games.playing_cards_game import PlayingCardsGame
from backend.games.qa_trivia_game import QaTriviaGame
from backend.games.rock_paper_scissors_game import RockPaperScissorsGame
from backend.games.skru_game import SkruGame
from backend.games.snake_game import SnakeGame
from backend.games.tic_tac_toe_game import TicTacToeGame
from backend.games.uno_game import UnoGame

GAME_REGISTRY: dict[str, type[BaseGame]] = {
    SnakeGame.GAME_TYPE: SnakeGame,
    MinesweeperGame.GAME_TYPE: MinesweeperGame,
    ChessGame.GAME_TYPE: ChessGame,
    BackgammonGame.GAME_TYPE: BackgammonGame,
    DominoesGame.GAME_TYPE: DominoesGame,
    LudoGame.GAME_TYPE: LudoGame,
    SkruGame.GAME_TYPE: SkruGame,
    UnoGame.GAME_TYPE: UnoGame,
    QaTriviaGame.GAME_TYPE: QaTriviaGame,
    GlobeGame.GAME_TYPE: GlobeGame,
    MonopolyGame.GAME_TYPE: MonopolyGame,
    TicTacToeGame.GAME_TYPE: TicTacToeGame,
    RockPaperScissorsGame.GAME_TYPE: RockPaperScissorsGame,
    Connect4Game.GAME_TYPE: Connect4Game,
    PlayingCardsGame.GAME_TYPE: PlayingCardsGame,
}
