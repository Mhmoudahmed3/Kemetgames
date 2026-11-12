"""Full server-authoritative Chess engine with SAN history, dual clocks, spectators, and minimax AI bot."""

from __future__ import annotations

import copy
import random
import time
from typing import Any

from backend.base_game import BaseGame, PlayerSlot, normalize_difficulty

FILES = "abcdefgh"
RANKS = "87654321"

PIECE_VALUES = {
    "P": 100,
    "N": 320,
    "B": 330,
    "R": 500,
    "Q": 900,
    "K": 20000,
}

# Center control bonus table (rank 8 at row 0 to rank 1 at row 7 for White)
PST_PAWN = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5, 5, 10, 25, 25, 10, 5, 5],
    [0, 0, 0, 22, 22, 0, 0, 0],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

PST_KNIGHT = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50],
]

TIME_CONTROLS = {
    "3+2": (180.0, 2.0),
    "5+0": (300.0, 0.0),
    "10+0": (600.0, 0.0),
}


def initial_board() -> list[list[str | None]]:
    return [
        ["r", "n", "b", "q", "k", "b", "n", "r"],
        ["p"] * 8,
        [None] * 8,
        [None] * 8,
        [None] * 8,
        [None] * 8,
        ["P"] * 8,
        ["R", "N", "B", "Q", "K", "B", "N", "R"],
    ]


def piece_color(piece: str | None) -> str | None:
    if not piece:
        return None
    return "w" if piece.isupper() else "b"


def to_alg(r: int, c: int) -> str:
    return f"{FILES[c]}{RANKS[r]}"


def from_alg(sq: str) -> tuple[int, int] | None:
    if not isinstance(sq, str) or len(sq) != 2:
        return None
    f, rk = sq[0].lower(), sq[1]
    if f not in FILES or rk not in RANKS:
        return None
    return RANKS.index(rk), FILES.index(f)


VALID_CHESS_PIECES = {"P", "N", "B", "R", "Q", "K", "p", "n", "b", "r", "q", "k"}


def validate_custom_board(board: list[list[str | None]]) -> tuple[bool, str]:
    if not isinstance(board, list) or len(board) != 8:
        return False, "Custom chess board must have exactly 8 rows."
    w_kings = 0
    b_kings = 0
    for r in range(8):
        row = board[r]
        if not isinstance(row, list) or len(row) != 8:
            return False, f"Row {r} must have exactly 8 squares."
        for c in range(8):
            p = row[c]
            if p is not None:
                if p not in VALID_CHESS_PIECES:
                    return False, f"Invalid piece '{p}' at {to_alg(r, c)}."
                if p == "K":
                    w_kings += 1
                elif p == "k":
                    b_kings += 1
    if w_kings != 1:
        return False, f"Requires exactly 1 White King (found {w_kings})."
    if b_kings != 1:
        return False, f"Requires exactly 1 Black King (found {b_kings})."
    return True, ""


def parse_fen_placement(fen: str) -> list[list[str | None]] | None:
    parts = fen.strip().split()
    placement = parts[0]
    ranks = placement.split("/")
    if len(ranks) != 8:
        return None
    board: list[list[str | None]] = []
    for rank in ranks:
        row: list[str | None] = []
        for ch in rank:
            if "1" <= ch <= "8":
                row.extend([None] * int(ch))
            elif ch in VALID_CHESS_PIECES:
                row.append(ch)
            else:
                return None
        if len(row) != 8:
            return None
        board.append(row)
    return board


class ChessGame(BaseGame):
    GAME_TYPE = "chess"
    TITLE = "CHESS"
    CATEGORY = "Strategy"
    DESCRIPTION = (
        "Full legal Chess with castling, en passant, promotions, 50-move rule, dual clocks, spectators, and AI bot."
    )
    MIN_PLAYERS = 2
    MAX_PLAYERS = 2
    SUPPORTS_SOLO = False
    SUPPORTS_BOTS = True
    SUPPORTS_SPECTATORS = True
    DEFAULT_SETTINGS = {"time_control": "5+0", "difficulty": "mid"}

    def __init__(
        self,
        room_code: str,
        players: list[PlayerSlot] | None = None,
        settings: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(room_code, players, settings)
        self.board: list[list[str | None]] = initial_board()
        self.turn: str = "w"
        self.castling: dict[str, bool] = {"K": True, "Q": True, "k": True, "q": True}
        self.en_passant: tuple[int, int] | None = None
        self.halfmove_clock: int = 0
        self.fullmove_number: int = 1
        self.move_history: list[str] = []
        self.captured: dict[str, list[str]] = {"w": [], "b": []}
        self.last_move: dict[str, str] | None = None
        self.clocks: dict[str, float] = {"w": 300.0, "b": 300.0}
        self.increment: float = 0.0
        self.last_clock_ts: float = 0.0
        self.color_map: dict[str, str] = {}
        self.position_counts: dict[str, int] = {}
        self.is_custom_mode: bool = False

    def can_start(self) -> tuple[bool, str]:
        ok, err = super().can_start()
        if not ok:
            return False, err
        custom_board = self.settings.get("custom_board")
        if custom_board:
            v_ok, v_err = validate_custom_board(custom_board)
            if not v_ok:
                return False, f"Custom Chess: {v_err}"
        else:
            custom_fen = self.settings.get("custom_fen")
            if custom_fen and isinstance(custom_fen, str):
                parsed = parse_fen_placement(custom_fen)
                if not parsed:
                    return False, "Custom Chess: Invalid FEN placement."
                v_ok, v_err = validate_custom_board(parsed)
                if not v_ok:
                    return False, f"Custom Chess: {v_err}"
        return True, ""

    def start_game(self, settings: dict[str, Any] | None = None) -> None:
        if settings:
            self.settings.update(settings)
        self.settings["difficulty"] = self.normalize_difficulty(
            self.settings.get("difficulty", "mid")
        )
        tc = str(self.settings.get("time_control", "5+0"))
        base_sec, inc_sec = TIME_CONTROLS.get(tc, (300.0, 0.0))

        custom_board = self.settings.get("custom_board")
        custom_fen = self.settings.get("custom_fen")
        loaded_board: list[list[str | None]] | None = None
        if custom_board and isinstance(custom_board, list):
            ok, _ = validate_custom_board(custom_board)
            if ok:
                loaded_board = [
                    [cell if cell in VALID_CHESS_PIECES else None for cell in row]
                    for row in custom_board
                ]
        elif custom_fen and isinstance(custom_fen, str):
            parsed = parse_fen_placement(custom_fen)
            if parsed:
                ok, _ = validate_custom_board(parsed)
                if ok:
                    loaded_board = parsed

        self.is_custom_mode = loaded_board is not None
        if loaded_board:
            self.board = loaded_board
            self.castling = {
                "K": self.board[7][4] == "K" and self.board[7][7] == "R",
                "Q": self.board[7][4] == "K" and self.board[7][0] == "R",
                "k": self.board[0][4] == "k" and self.board[0][7] == "r",
                "q": self.board[0][4] == "k" and self.board[0][0] == "r",
            }
        else:
            self.board = initial_board()
            self.castling = {"K": True, "Q": True, "k": True, "q": True}

        self.turn = "w"
        self.en_passant = None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.move_history = []
        self.captured = {"w": [], "b": []}
        self.last_move = None
        self.clocks = {"w": base_sec, "b": base_sec}
        self.increment = inc_sec
        self.started_at = time.time()
        self.last_clock_ts = self.started_at
        self.phase = "playing"
        self.winner_ids = []
        self.win_reason = ""

        self.color_map = {
            "w": self.players[0].id,
            "b": self.players[1].id,
        }
        self.turn_player_id = self.color_map["w"]
        self.position_counts = {self._position_key(): 1}
        mode_tag = " [Custom Rules]" if self.is_custom_mode else ""
        self.log_event(
            f"Chess started{mode_tag}: {self.players[0].name} (White) vs {self.players[1].name} (Black) [{tc}]."
        )
        if self.is_custom_mode:
            initial_legal = self._legal_moves(
                self.board, self.turn, self.castling, self.en_passant
            )
            if not initial_legal:
                if self._in_check(self.board, self.turn):
                    winner_id = self.color_map["b"]
                    winner = self.get_player(winner_id)
                    if winner:
                        winner.score = 1
                    self.finish_game(
                        [winner_id],
                        f"Checkmate from starting setup! {winner.name if winner else winner_id} wins.",
                    )
                else:
                    self.finish_game([], "Stalemate from starting setup — match drawn.")

    def _has_legal_en_passant(self) -> bool:
        if not self.en_passant:
            return False
        legal = self._legal_moves(self.board, self.turn, self.castling, self.en_passant)
        return any(mv.get("en_passant") for mv in legal)

    def _position_key(self) -> str:
        rows = "/".join("".join(cell or "." for cell in r) for r in self.board)
        cast = "".join(k for k, v in self.castling.items() if v) or "-"
        ep = to_alg(*self.en_passant) if self._has_legal_en_passant() else "-"
        return f"{rows}|{self.turn}|{cast}|{ep}"

    def _find_king(
        self, board: list[list[str | None]], color: str
    ) -> tuple[int, int] | None:
        target = "K" if color == "w" else "k"
        for r in range(8):
            for c in range(8):
                if board[r][c] == target:
                    return (r, c)
        return None

    def _is_attacked(
        self, board: list[list[str | None]], r: int, c: int, by_color: str
    ) -> bool:
        # Pawn attacks
        pawn_dir = 1 if by_color == "w" else -1
        pawn_sym = "P" if by_color == "w" else "p"
        pr = r + pawn_dir
        if 0 <= pr < 8:
            for dc in (-1, 1):
                pc = c + dc
                if 0 <= pc < 8 and board[pr][pc] == pawn_sym:
                    return True

        # Knights
        knight_sym = "N" if by_color == "w" else "n"
        for dr, dc in ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] == knight_sym:
                return True

        # Kings
        king_sym = "K" if by_color == "w" else "k"
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] == king_sym:
                    return True

        # Orthogonal rays (Rook / Queen)
        rook_syms = ("R", "Q") if by_color == "w" else ("r", "q")
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                p = board[nr][nc]
                if p:
                    if p in rook_syms:
                        return True
                    break
                nr += dr
                nc += dc

        # Diagonal rays (Bishop / Queen)
        bishop_syms = ("B", "Q") if by_color == "w" else ("b", "q")
        for dr, dc in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            nr, nc = r + dr, c + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                p = board[nr][nc]
                if p:
                    if p in bishop_syms:
                        return True
                    break
                nr += dr
                nc += dc

        return False

    def _in_check(self, board: list[list[str | None]], color: str) -> bool:
        kpos = self._find_king(board, color)
        if not kpos:
            return False
        opp = "b" if color == "w" else "w"
        return self._is_attacked(board, kpos[0], kpos[1], opp)

    def _pseudo_moves(
        self,
        board: list[list[str | None]],
        color: str,
        castling: dict[str, bool],
        en_passant: tuple[int, int] | None,
    ) -> list[dict[str, Any]]:
        moves: list[dict[str, Any]] = []
        opp = "b" if color == "w" else "w"
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if not p or piece_color(p) != color:
                    continue
                ptype = p.upper()
                if ptype == "P":
                    step = -1 if color == "w" else 1
                    start_row = 6 if color == "w" else 1
                    promo_row = 0 if color == "w" else 7
                    nr = r + step
                    if 0 <= nr < 8 and board[nr][c] is None:
                        if nr == promo_row:
                            for pr in ("Q", "R", "B", "N"):
                                moves.append({"from": (r, c), "to": (nr, c), "promo": pr})
                        else:
                            moves.append({"from": (r, c), "to": (nr, c)})
                            if r == start_row and board[r + 2 * step][c] is None:
                                moves.append({"from": (r, c), "to": (r + 2 * step, c), "double_pawn": True})
                    for dc in (-1, 1):
                        nc = c + dc
                        if 0 <= nr < 8 and 0 <= nc < 8:
                            target = board[nr][nc]
                            if target and piece_color(target) == opp and target.upper() != "K":
                                if nr == promo_row:
                                    for pr in ("Q", "R", "B", "N"):
                                        moves.append({"from": (r, c), "to": (nr, nc), "promo": pr, "capture": True})
                                else:
                                    moves.append({"from": (r, c), "to": (nr, nc), "capture": True})
                            elif en_passant and (nr, nc) == en_passant:
                                moves.append({"from": (r, c), "to": (nr, nc), "en_passant": True, "capture": True})

                elif ptype == "N":
                    for dr, dc in ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < 8 and 0 <= nc < 8:
                            t = board[nr][nc]
                            if t is None or (piece_color(t) == opp and t.upper() != "K"):
                                moves.append({"from": (r, c), "to": (nr, nc), "capture": t is not None})

                elif ptype in ("B", "R", "Q"):
                    dirs: list[tuple[int, int]] = []
                    if ptype in ("B", "Q"):
                        dirs.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])
                    if ptype in ("R", "Q"):
                        dirs.extend([(-1, 0), (1, 0), (0, -1), (0, 1)])
                    for dr, dc in dirs:
                        nr, nc = r + dr, c + dc
                        while 0 <= nr < 8 and 0 <= nc < 8:
                            t = board[nr][nc]
                            if t is None:
                                moves.append({"from": (r, c), "to": (nr, nc)})
                            else:
                                if piece_color(t) == opp and t.upper() != "K":
                                    moves.append({"from": (r, c), "to": (nr, nc), "capture": True})
                                break
                            nr += dr
                            nc += dc

                elif ptype == "K":
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < 8 and 0 <= nc < 8:
                                t = board[nr][nc]
                                if t is None or (piece_color(t) == opp and t.upper() != "K"):
                                    moves.append({"from": (r, c), "to": (nr, nc), "capture": t is not None})
                    # Castling
                    back_row = 7 if color == "w" else 0
                    if r == back_row and c == 4 and not self._is_attacked(board, back_row, 4, opp):
                        ks_key = "K" if color == "w" else "k"
                        qs_key = "Q" if color == "w" else "q"
                        rook_sym = "R" if color == "w" else "r"
                        if castling.get(ks_key) and board[back_row][7] == rook_sym:
                            if board[back_row][5] is None and board[back_row][6] is None:
                                if not self._is_attacked(board, back_row, 5, opp) and not self._is_attacked(board, back_row, 6, opp):
                                    moves.append({"from": (back_row, 4), "to": (back_row, 6), "castle": "K"})
                        if castling.get(qs_key) and board[back_row][0] == rook_sym:
                            if board[back_row][1] is None and board[back_row][2] is None and board[back_row][3] is None:
                                if not self._is_attacked(board, back_row, 3, opp) and not self._is_attacked(board, back_row, 2, opp):
                                    moves.append({"from": (back_row, 4), "to": (back_row, 2), "castle": "Q"})
        return moves

    def _apply_move_copy(
        self,
        board: list[list[str | None]],
        castling: dict[str, bool],
        move: dict[str, Any],
    ) -> tuple[list[list[str | None]], dict[str, bool], tuple[int, int] | None, str | None]:
        nb = [row[:] for row in board]
        nc = dict(castling)
        fr, fc = move["from"]
        tr, tc = move["to"]
        piece = nb[fr][fc]
        color = piece_color(piece)
        captured_piece = nb[tr][tc]

        nb[fr][fc] = None
        if move.get("en_passant"):
            captured_piece = nb[fr][tc]
            nb[fr][tc] = None

        if move.get("promo"):
            placed = move["promo"] if color == "w" else move["promo"].lower()
            nb[tr][tc] = placed
        else:
            nb[tr][tc] = piece

        if move.get("castle") == "K":
            nb[fr][5] = nb[fr][7]
            nb[fr][7] = None
        elif move.get("castle") == "Q":
            nb[fr][3] = nb[fr][0]
            nb[fr][0] = None

        # Update castling rights
        if piece == "K":
            nc["K"] = False
            nc["Q"] = False
        elif piece == "k":
            nc["k"] = False
            nc["q"] = False
        elif piece == "R":
            if (fr, fc) == (7, 7):
                nc["K"] = False
            elif (fr, fc) == (7, 0):
                nc["Q"] = False
        elif piece == "r":
            if (fr, fc) == (0, 7):
                nc["k"] = False
            elif (fr, fc) == (0, 0):
                nc["q"] = False

        if (tr, tc) == (7, 7):
            nc["K"] = False
        elif (tr, tc) == (7, 0):
            nc["Q"] = False
        elif (tr, tc) == (0, 7):
            nc["k"] = False
        elif (tr, tc) == (0, 0):
            nc["q"] = False

        new_ep = ((fr + tr) // 2, fc) if move.get("double_pawn") else None
        return nb, nc, new_ep, captured_piece

    def _legal_moves(
        self,
        board: list[list[str | None]],
        color: str,
        castling: dict[str, bool],
        en_passant: tuple[int, int] | None,
    ) -> list[dict[str, Any]]:
        legal: list[dict[str, Any]] = []
        for mv in self._pseudo_moves(board, color, castling, en_passant):
            nb, _, _, _ = self._apply_move_copy(board, castling, mv)
            if not self._in_check(nb, color):
                legal.append(mv)
        return legal

    def _format_san(
        self,
        move: dict[str, Any],
        legal_before: list[dict[str, Any]],
        next_board: list[list[str | None]],
        next_castling: dict[str, bool],
        next_ep: tuple[int, int] | None,
    ) -> str:
        if move.get("castle") == "K":
            san = "O-O"
        elif move.get("castle") == "Q":
            san = "O-O-O"
        else:
            fr, fc = move["from"]
            tr, tc = move["to"]
            piece = self.board[fr][fc] or "P"
            ptype = piece.upper()
            is_cap = bool(move.get("capture"))
            dest = to_alg(tr, tc)

            if ptype == "P":
                prefix = f"{FILES[fc]}x" if is_cap else ""
                promo = f"={move['promo']}" if move.get("promo") else ""
                san = f"{prefix}{dest}{promo}"
            else:
                same_type = [
                    m
                    for m in legal_before
                    if m["to"] == (tr, tc)
                    and m["from"] != (fr, fc)
                    and (self.board[m["from"][0]][m["from"][1]] or "").upper() == ptype
                ]
                disambig = ""
                if same_type:
                    same_file = any(m["from"][1] == fc for m in same_type)
                    same_rank = any(m["from"][0] == fr for m in same_type)
                    if not same_file:
                        disambig = FILES[fc]
                    elif not same_rank:
                        disambig = RANKS[fr]
                    else:
                        disambig = to_alg(fr, fc)
                cap_mark = "x" if is_cap else ""
                san = f"{ptype}{disambig}{cap_mark}{dest}"

        opp = "b" if self.turn == "w" else "w"
        if self._in_check(next_board, opp):
            opp_legal = self._legal_moves(next_board, opp, next_castling, next_ep)
            san += "#" if not opp_legal else "+"
        return san

    def _has_non_king_pieces(self, board: list[list[str | None]], color: str) -> bool:
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p and piece_color(p) == color and p.upper() != "K":
                    return True
        return False

    def _has_insufficient_material(self, board: list[list[str | None]]) -> bool:
        pieces: list[tuple[str, int, int]] = []
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p and p.upper() != "K":
                    pieces.append((p, r, c))
        if not pieces:
            return True
        if self.is_custom_mode:
            return False
        if len(pieces) == 1 and pieces[0][0].upper() in ("B", "N"):
            return True
        if len(pieces) == 2:
            (p1, r1, c1), (p2, r2, c2) = pieces
            if p1.upper() == "B" and p2.upper() == "B" and piece_color(p1) != piece_color(p2):
                if (r1 + c1) % 2 == (r2 + c2) % 2:
                    return True
        return False

    def _sync_clock(self, now: float) -> None:
        if self.phase != "playing":
            return
        dt = max(0.0, now - self.last_clock_ts)
        self.last_clock_ts = now
        self.clocks[self.turn] = max(0.0, self.clocks[self.turn] - dt)
        if self.clocks[self.turn] <= 0.0:
            loser_color = self.turn
            winner_color = "b" if loser_color == "w" else "w"
            winner_id = self.color_map[winner_color]
            winner = self.get_player(winner_id)
            if winner:
                winner.score = 1
            self.finish_game(
                [winner_id],
                f"{'White' if loser_color == 'w' else 'Black'} ran out of time! {winner.name if winner else winner_id} wins.",
            )

    def _tick_timers(self, now: float) -> bool:
        if self.phase != "playing":
            return False
        prev_w, prev_b = int(self.clocks["w"]), int(self.clocks["b"])
        self._sync_clock(now)
        if self.phase == "finished":
            return True
        return int(self.clocks["w"]) != prev_w or int(self.clocks["b"]) != prev_b

    def forfeit_player(self, player_id: str, reason: str | None = None) -> bool:
        if self.phase not in ("pre_game", "playing") or player_id not in self.color_map.values():
            return False
        player_color = "w" if self.color_map.get("w") == player_id else "b"
        winner_color = "b" if player_color == "w" else "w"
        winner_id = self.color_map[winner_color]
        winner = self.get_player(winner_id)
        if winner:
            winner.score = 1
        resigner = self.get_player(player_id)
        msg = reason or (
            f"{resigner.name if resigner else player_id} resigned. {winner.name if winner else winner_id} wins!"
        )
        self.finish_game([winner_id], msg)
        return True

    def handle_action(
        self, player_id: str, action: str, data: dict[str, Any]
    ) -> tuple[bool, str]:
        if self.phase != "playing":
            return False, "Match is not active."
        now = time.time()
        self._sync_clock(now)
        if self.phase == "finished":
            return True, ""

        if action == "resign":
            if player_id not in self.color_map.values():
                return False, "Only active players can resign."
            self.forfeit_player(player_id)
            return True, ""

        if action != "move":
            return False, f"Unsupported action: {action}"

        expected_pid = self.color_map[self.turn]
        if player_id != expected_pid:
            return False, "It is not your turn."

        from_sq = from_alg(data.get("from", ""))
        to_sq = from_alg(data.get("to", ""))
        if not from_sq or not to_sq:
            return False, "Invalid square coordinates."

        raw_promo = data.get("promotion")
        promo = (
            raw_promo.strip().upper()
            if isinstance(raw_promo, str) and raw_promo.strip()
            else None
        )
        legal = self._legal_moves(self.board, self.turn, self.castling, self.en_passant)
        matched = [
            m
            for m in legal
            if m["from"] == from_sq
            and m["to"] == to_sq
            and (
                (not m.get("promo"))
                or m.get("promo") == promo
                or (promo is None and m.get("promo") == "Q")
            )
        ]
        if not matched:
            return False, "Illegal chess move."

        chosen = matched[0]
        nb, nc, new_ep, cap = self._apply_move_copy(self.board, self.castling, chosen)
        san = self._format_san(chosen, legal, nb, nc, new_ep)

        moved_piece = self.board[from_sq[0]][from_sq[1]] or "P"
        self.board = nb
        self.castling = nc
        self.en_passant = new_ep
        if cap:
            self.captured[self.turn].append(cap)
        self.move_history.append(san)
        self.last_move = {"from": to_alg(*from_sq), "to": to_alg(*to_sq)}

        if moved_piece.upper() == "P" or cap:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        if self.turn == "b":
            self.fullmove_number += 1

        self.clocks[self.turn] += self.increment
        self.turn = "b" if self.turn == "w" else "w"
        self.turn_player_id = self.color_map[self.turn]

        pos_key = self._position_key()
        self.position_counts[pos_key] = self.position_counts.get(pos_key, 0) + 1

        self.log_event(f"{san}")

        # Check end conditions
        mover_color = "b" if self.turn == "w" else "w"
        mover_id = self.color_map[mover_color]
        next_legal = self._legal_moves(self.board, self.turn, self.castling, self.en_passant)
        if not next_legal and self._in_check(self.board, self.turn):
            winner = self.get_player(mover_id)
            if winner:
                winner.score = 1
            self.finish_game(
                [mover_id],
                f"Checkmate! {winner.name if winner else mover_id} wins ({san}).",
            )
        elif (
            self.is_custom_mode
            and cap is not None
            and not self._has_non_king_pieces(self.board, self.turn)
        ):
            winner = self.get_player(mover_id)
            if winner:
                winner.score = 1
            self.finish_game(
                [mover_id],
                f"All rival pieces captured! {winner.name if winner else mover_id} wins ({san}).",
            )
        elif not next_legal:
            self.finish_game([], "Stalemate — match drawn.")
        elif self.halfmove_clock >= 100:
            self.finish_game([], "Draw by 50-move rule.")
        elif self.position_counts[pos_key] >= 3:
            self.finish_game([], "Draw by threefold repetition.")
        elif self._has_insufficient_material(self.board):
            self.finish_game([], "Draw by insufficient mating material.")

        return True, ""

    # --- Minimax AI Bot (Depth 2 with alpha-beta & PST) ---
    def _eval_board(self, board: list[list[str | None]]) -> int:
        score = 0
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if not p:
                    continue
                val = PIECE_VALUES[p.upper()]
                bonus = 0
                if p.upper() == "P":
                    bonus = PST_PAWN[r if p.isupper() else 7 - r][c]
                elif p.upper() == "N":
                    bonus = PST_KNIGHT[r if p.isupper() else 7 - r][c]
                if p.isupper():
                    score += val + bonus
                else:
                    score -= val + bonus
        return score

    def _minimax(
        self,
        board: list[list[str | None]],
        castling: dict[str, bool],
        ep: tuple[int, int] | None,
        color: str,
        depth: int,
        alpha: int,
        beta: int,
        budget: dict[str, Any] | None = None,
    ) -> tuple[int, dict[str, Any] | None]:
        if budget is not None:
            budget["nodes"] += 1
            if budget["nodes"] > budget["limit"]:
                budget["aborted"] = True
                return self._eval_board(board), None

        legal = self._legal_moves(board, color, castling, ep)
        if not legal:
            if self._in_check(board, color):
                return (-99999 - depth if color == "w" else 99999 + depth), None
            return 0, None
        if depth == 0:
            return self._eval_board(board), None

        # MVV-LVA + promotion move ordering improves alpha-beta cutoffs
        def order_key(m: dict[str, Any]) -> int:
            sc = 0
            if m.get("promo"):
                sc += 900
            if m.get("capture"):
                victim = board[m["to"][0]][m["to"][1]]
                attacker = board[m["from"][0]][m["from"][1]]
                sc += PIECE_VALUES.get((victim or "P").upper(), 100) - (
                    PIECE_VALUES.get((attacker or "P").upper(), 100) // 10
                )
            return sc

        legal.sort(key=order_key, reverse=True)
        best_move = legal[0]
        next_color = "b" if color == "w" else "w"

        if color == "w":
            max_eval = -10**8
            for mv in legal:
                nb, nc, nep, cap = self._apply_move_copy(board, castling, mv)
                if (
                    self.is_custom_mode
                    and cap is not None
                    and not self._has_non_king_pieces(nb, next_color)
                ):
                    ev = 99999 + depth
                else:
                    ev, _ = self._minimax(nb, nc, nep, next_color, depth - 1, alpha, beta, budget)
                if budget is not None and budget["aborted"]:
                    return max_eval, best_move
                if ev > max_eval:
                    max_eval = ev
                    best_move = mv
                alpha = max(alpha, ev)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = 10**8
            for mv in legal:
                nb, nc, nep, cap = self._apply_move_copy(board, castling, mv)
                if (
                    self.is_custom_mode
                    and cap is not None
                    and not self._has_non_king_pieces(nb, next_color)
                ):
                    ev = -99999 - depth
                else:
                    ev, _ = self._minimax(nb, nc, nep, next_color, depth - 1, alpha, beta, budget)
                if budget is not None and budget["aborted"]:
                    return min_eval, best_move
                if ev < min_eval:
                    min_eval = ev
                    best_move = mv
                beta = min(beta, ev)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def get_bot_action(self, bot_id: str) -> tuple[str, dict[str, Any]] | None:
        if self.phase != "playing" or self.color_map.get(self.turn) != bot_id:
            return None
        legal = self._legal_moves(self.board, self.turn, self.castling, self.en_passant)
        if not legal:
            return None

        next_color = "b" if self.turn == "w" else "w"
        scored: list[tuple[int, dict[str, Any]]] = []
        for mv in legal:
            nb, _, _, cap = self._apply_move_copy(self.board, self.castling, mv)
            if (
                self.is_custom_mode
                and cap is not None
                and not self._has_non_king_pieces(nb, next_color)
            ):
                ev = 99999 if self.turn == "w" else -99999
            else:
                ev = self._eval_board(nb)
            scored.append((ev if self.turn == "w" else -ev, mv))
        scored.sort(key=lambda item: item[0], reverse=True)

        diff = self.get_difficulty()
        best: dict[str, Any] | None = scored[0][1]

        if diff == "easy":
            pool = [mv for _, mv in scored[: min(3, len(scored))]]
            best = random.choice(pool) if (len(pool) > 1 and random.random() < 0.45) else scored[0][1]
        else:
            budget2 = {"nodes": 0, "limit": 4000, "aborted": False}
            _, best2 = self._minimax(
                self.board, self.castling, self.en_passant, self.turn, 2, -10**8, 10**8, budget2
            )
            if not budget2["aborted"] and best2 is not None:
                best = best2
                if diff == "hard":
                    budget3 = {"nodes": 0, "limit": 4500, "aborted": False}
                    _, best3 = self._minimax(
                        self.board,
                        self.castling,
                        self.en_passant,
                        self.turn,
                        3,
                        -10**8,
                        10**8,
                        budget3,
                    )
                    if not budget3["aborted"] and best3 is not None:
                        best = best3

        if not best:
            return None
        data: dict[str, Any] = {
            "from": to_alg(*best["from"]),
            "to": to_alg(*best["to"]),
        }
        if best.get("promo"):
            data["promotion"] = best["promo"]
        return "move", data

    def get_public_state(self) -> dict[str, Any]:
        legal = (
            self._legal_moves(self.board, self.turn, self.castling, self.en_passant)
            if self.phase == "playing"
            else []
        )
        legal_map: dict[str, list[dict[str, Any]]] = {}
        seen_pairs: set[tuple[str, str]] = set()
        for mv in legal:
            src = to_alg(*mv["from"])
            dst = to_alg(*mv["to"])
            if (src, dst) in seen_pairs:
                continue
            seen_pairs.add((src, dst))
            legal_map.setdefault(src, []).append(
                {
                    "to": dst,
                    "promo": bool(mv.get("promo")),
                    "capture": bool(mv.get("capture")),
                }
            )
        kpos = self._find_king(self.board, self.turn)
        in_check_sq = to_alg(*kpos) if (kpos and self._in_check(self.board, self.turn)) else None

        return {
            "phase": self.phase,
            "board": self.board,
            "turn": self.turn,
            "turn_player_id": self.turn_player_id,
            "color_map": self.color_map,
            "clocks": {k: round(v, 1) for k, v in self.clocks.items()},
            "move_history": self.move_history,
            "captured": self.captured,
            "last_move": self.last_move,
            "in_check_square": in_check_sq,
            "legal_moves": legal_map,
            "custom_mode": self.is_custom_mode,
            "winner_ids": self.winner_ids,
            "win_reason": self.win_reason,
        }

