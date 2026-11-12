"""Comprehensive unit tests for all 11 server-authoritative game engines and AI bots."""

from __future__ import annotations

from pathlib import Path
import time
import pytest

from backend.base_game import PlayerSlot
from backend.data.country_store import COUNTRIES_BANK, COUNTRY_BY_CODE, shortest_border_path
from backend.games.backgammon_game import BackgammonGame
from backend.games.chess_game import ChessGame, validate_custom_board
from backend.games.dominoes_game import DominoesGame
from backend.games.globe_game import GlobeGame
from backend.games.ludo_game import LudoGame
from backend.games.minesweeper_game import MinesweeperGame
from backend.games.monopoly_game import MonopolyGame
from backend.games.qa_trivia_game import QaTriviaGame
from backend.games.skru_game import SkruGame
from backend.games.snake_game import SnakeGame
from backend.games.uno_game import UnoGame, build_uno_deck


def make_players(count: int, bots_from: int | None = None) -> list[PlayerSlot]:
    out = []
    for i in range(count):
        is_bot = bots_from is not None and i >= bots_from
        out.append(
            PlayerSlot(
                id=f"p{i+1}",
                name=f"Player{i+1}",
                is_bot=is_bot,
                is_host=(i == 0),
                seat=i,
            )
        )
    return out


def test_snake_solo_and_multiplayer_race():
    solo = SnakeGame("SNK001", make_players(1))
    solo.start_game()
    ok, _ = solo.handle_action("p1", "sync", {"score": 40, "length": 7, "alive": True})
    assert ok
    assert solo.phase == "playing"
    ok, _ = solo.handle_action("p1", "sync", {"score": 50, "length": 8, "alive": False})
    assert ok
    assert solo.phase == "finished"
    assert solo.winner_ids == ["p1"]

    race = SnakeGame("SNK002", make_players(2))
    race.start_game({"duration": 60})
    race.handle_action("p1", "sync", {"score": 999999, "length": 10, "alive": True})
    # Sanity clamp prevents score forging in a single 0.2s jump
    assert race.snakes["p1"]["score"] < 1000
    race.handle_action("p2", "sync", {"score": 20, "length": 5, "alive": False})
    assert race.phase == "finished"
    assert race.winner_ids == ["p1"]


def test_minesweeper_first_click_safe_and_privacy():
    for diff, (r_exp, c_exp, m_exp) in [
        ("beginner", (9, 9, 10)),
        ("intermediate", (16, 16, 40)),
        ("expert", (16, 30, 99)),
    ]:
        g = MinesweeperGame("MS0001", make_players(1))
        g.start_game({"difficulty": diff})
        assert (g.rows, g.cols, g.total_mines) == (r_exp, c_exp, m_exp)
        ok, err = g.handle_action("p1", "reveal", {"r": 4, "c": 4})
        assert ok, err
        board = g.boards["p1"]
        # First click must be 0 adjacent mines and never a mine
        assert board["numbers"][(4, 4)] == 0
        assert (4, 4) not in board["mines"]
        # Secret mines must never appear in public_state or active private_state
        assert "mines" not in g.get_public_state()
        assert g.get_private_state("p1")["mines"] == []

        # Flag + chord verification
        ok, _ = g.handle_action("p1", "flag", {"r": 0, "c": 0})
        if (0, 0) not in board["revealed"]:
            assert ok
            assert [0, 0] in g.get_private_state("p1")["flagged"]

    # Custom manual grid and booms verification
    cg = MinesweeperGame("MSCUSTOM", make_players(1))
    cg.start_game({"difficulty": "custom", "width": 24, "height": 18, "booms": 55})
    assert cg.difficulty == "custom"
    assert (cg.rows, cg.cols, cg.total_mines) == (18, 24, 55)
    pub = cg.get_public_state()
    assert pub["rows"] == 18
    assert pub["cols"] == 24
    assert pub["total_mines"] == 55
    ok, err = cg.handle_action("p1", "reveal", {"r": 5, "c": 5})
    assert ok, err
    assert cg.boards["p1"]["numbers"][(5, 5)] == 0
    assert (5, 5) not in cg.boards["p1"]["mines"]


def test_chess_legal_rules_scholars_mate_castling_en_passant_and_bot():
    g = ChessGame("CH0001", make_players(2))
    g.start_game({"time_control": "5+0"})

    # Scholar's mate: 1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7#
    moves = [
        ("p1", "e2", "e4"),
        ("p2", "e7", "e5"),
        ("p1", "f1", "c4"),
        ("p2", "b8", "c6"),
        ("p1", "d1", "h5"),
        ("p2", "g8", "f6"),
        ("p1", "h5", "f7"),
    ]
    for pid, f, t in moves:
        ok, err = g.handle_action(pid, "move", {"from": f, "to": t})
        assert ok, err
    assert g.phase == "finished"
    assert g.winner_ids == ["p1"]
    assert g.move_history[-1].endswith("#")

    # En passant + Castling check
    g2 = ChessGame("CH0002", make_players(2))
    g2.start_game()
    sequence = [
        ("p1", "e2", "e4"),
        ("p2", "a7", "a6"),
        ("p1", "e4", "e5"),
        ("p2", "d7", "d5"),
        ("p1", "e5", "d6"),  # En passant capture!
        ("p2", "a6", "a5"),
        ("p1", "g1", "f3"),
        ("p2", "a5", "a4"),
        ("p1", "f1", "e2"),
        ("p2", "b7", "b6"),
        ("p1", "e1", "g1"),  # Kingside castling!
    ]
    for pid, f, t in sequence:
        ok, err = g2.handle_action(pid, "move", {"from": f, "to": t})
        assert ok, err
    assert "O-O" in g2.move_history
    assert g2.board[7][6] == "K"
    assert g2.board[7][5] == "R"

    # Bot move check
    g_bot = ChessGame("CH0003", make_players(2, bots_from=1))
    g_bot.start_game()
    g_bot.handle_action("p1", "move", {"from": "e2", "to": "e4"})
    bot_cmd = g_bot.get_bot_action("p2")
    assert bot_cmd is not None
    ok, err = g_bot.handle_action("p2", bot_cmd[0], bot_cmd[1])
    assert ok, err


def test_backgammon_bar_entry_and_bearing_off():
    g = BackgammonGame("BG0001", make_players(2, bots_from=1))
    g.start_game()
    # Set up custom scenario: White has 1 checker on Bar, 14 in home board (0..5)
    g.points = [0] * 24
    g.points[0] = 14
    g.points[22] = -1  # Red blot on point 22 (index 22)
    g.bar = {0: 1, 1: 0}
    g.off = {0: 0, 1: 14}
    g.turn_idx = 0
    g.turn_player_id = "p1"
    g.subphase = "move"
    g.dice = [2, 3]
    g.remaining_dice = [2, 3]

    # Mandatory bar entry: die=2 enters onto 24-2 = 22 (hitting Red blot!)
    legal = g._legal_first_moves()
    assert all(m["from"] == "bar" for m in legal)
    ok, err = g.handle_action("p1", "move", {"from": "bar", "to": 22})
    assert ok, err
    assert g.bar[1] == 1
    assert g.bar[0] == 0

    # Test bearing off
    g.bar = {0: 0, 1: 0}
    g.points = [0] * 24
    g.points[2] = 1
    g.off = {0: 14, 1: 0}
    g.remaining_dice = [5]  # Over-roll from highest occupied point 2!
    ok, err = g.handle_action("p1", "move", {"from": 2, "to": "off"})
    assert ok, err
    assert g.phase == "finished"
    assert g.winner_ids == ["p1"]


def test_tawla_31_and_mahbosa_modes():
    # Test Tawla 31: all 15 start on point 23 and point 0, single blot blocks opponent
    g31 = BackgammonGame("BG3101", make_players(2), {"mode": "tawla_31"})
    g31.start_game()
    assert g31.points[23] == 15
    assert g31.points[0] == -15
    g31.points = [0] * 24
    g31.points[10] = 1
    g31.points[7] = -1  # Single Red checker at index 7 must block White die=3!
    g31.turn_idx = 0
    g31.turn_player_id = "p1"
    g31.subphase = "move"
    g31.remaining_dice = [3]
    assert g31._legal_first_moves() == []

    # Test Mahbosa: landing on lone Red checker pins/jails it underneath, and moving away liberates it!
    gm = BackgammonGame("BGMH01", make_players(2), {"mode": "mahbosa"})
    gm.start_game()
    assert gm.points[23] == 15
    assert gm.points[0] == -15
    gm.points = [0] * 24
    gm.points[10] = 1
    gm.points[7] = -1  # Lone Red checker on point 7
    gm.turn_idx = 0
    gm.turn_player_id = "p1"
    gm.subphase = "move"
    gm.dice = [3, 4]
    gm.remaining_dice = [3, 4]
    ok, err = gm.handle_action("p1", "move", {"from": 10, "to": 7})
    assert ok, err
    assert gm.points[7] == 1  # White owns the point
    assert gm.pinned[7] == -1  # Red checker is pinned underneath!
    assert gm.bar[1] == 0  # Not sent to bar

    # Now White moves off point 7 with die=4 -> Red checker must be liberated!
    ok, err = gm.handle_action("p1", "move", {"from": 7, "to": 3})
    assert ok, err
    assert gm.pinned[7] == 0
    assert gm.points[7] == -1


def test_chess_custom_board_setup_and_play():
    custom = [[None] * 8 for _ in range(8)]
    custom[0][4] = "k"
    custom[6][3] = "Q"
    custom[7][4] = "K"
    gc = ChessGame("CHCUST", make_players(2, bots_from=1), {"custom_board": custom})
    ok, err = gc.can_start()
    assert ok, err
    gc.start_game()
    assert gc.board[0][4] == "k"
    assert gc.board[6][3] == "Q"
    assert gc.board[7][4] == "K"
    assert gc.TITLE == "CHESS"
    # White Queen captures/moves diagonally or delivers checkmate Qh7# -> d2-e2
    ok, err = gc.handle_action("p1", "move", {"from": "d2", "to": "e2"})
    assert ok, err
    bot_cmd = gc.get_bot_action("p2")
    assert bot_cmd is not None


def test_chess_custom_free_placement_and_capture_all_win():
    # Pawns on rank 8 and rank 1, adjacent kings, and multiple queens must all be valid
    board = [[None] * 8 for _ in range(8)]
    board[0] = ["p", "p", "p", "p", "k", "p", "p", "p"]
    board[1] = ["p"] * 8
    board[6] = ["Q"] * 8
    board[7] = ["Q", "Q", "Q", "Q", "K", "Q", "Q", "P"]
    ok, err = validate_custom_board(board)
    assert ok, err

    # Adjacent kings allowed in validation
    adj = [[None] * 8 for _ in range(8)]
    adj[3][4] = "k"
    adj[4][4] = "K"
    adj[7][0] = "R"
    ok, err = validate_custom_board(adj)
    assert ok, err

    # King count validation must still require exactly 1 K and 1 k
    no_wk = [[None] * 8 for _ in range(8)]
    no_wk[0][4] = "k"
    ok, _ = validate_custom_board(no_wk)
    assert not ok

    two_bk = [[None] * 8 for _ in range(8)]
    two_bk[0][4] = "k"
    two_bk[0][5] = "k"
    two_bk[7][4] = "K"
    ok, _ = validate_custom_board(two_bk)
    assert not ok

    # Heavy custom board (many queens vs rank-8 pawns) starts and bot moves cleanly
    gc_heavy = ChessGame("CHHVY", make_players(2, bots_from=1), {"custom_board": board})
    assert gc_heavy.can_start()[0]
    gc_heavy.start_game()
    assert gc_heavy.get_public_state()["custom_mode"] is True
    ok, err = gc_heavy.handle_action("p1", "move", {"from": "a2", "to": "a7"})
    assert ok, err
    bot_mv = gc_heavy.get_bot_action("p2")
    assert bot_mv is not None

    # Adjacent kings: White cannot capture Black's king directly, must step away
    gc_adj = ChessGame("CHADJ", make_players(2), {"custom_board": adj})
    gc_adj.start_game()
    ok_cap_k, _ = gc_adj.handle_action("p1", "move", {"from": "e4", "to": "e5"})
    assert not ok_cap_k
    ok_escape, err = gc_adj.handle_action("p1", "move", {"from": "e4", "to": "d3"})
    assert ok_escape, err
    assert gc_adj.phase == "playing"

    # Custom win condition: capturing all opponent's non-king pieces wins immediately (even K+B vs K+B!)
    bish = [[None] * 8 for _ in range(8)]
    bish[0][7] = "k"
    bish[2][5] = "b"  # f6 (dark square)
    bish[4][3] = "B"  # d4 (dark square)
    bish[7][0] = "K"
    gc_bish = ChessGame("CHBSH", make_players(2), {"custom_board": bish})
    gc_bish.start_game()
    # Non-capturing bishop move should NOT trigger insufficient-material draw in custom mode
    ok, err = gc_bish.handle_action("p1", "move", {"from": "d4", "to": "e5"})
    assert ok, err
    assert gc_bish.phase == "playing"
    # Black moves king, then White captures Black's only non-king piece (f6) and wins immediately
    ok, err = gc_bish.handle_action("p2", "move", {"from": "h8", "to": "g8"})
    assert ok, err
    ok, err = gc_bish.handle_action("p1", "move", {"from": "e5", "to": "f6"})
    assert ok, err
    assert gc_bish.phase == "finished"
    assert gc_bish.winner_ids == ["p1"]
    assert "All rival pieces captured" in gc_bish.win_reason


def test_dominoes_boneyard_and_blocked_round():
    g = DominoesGame("DOM001", make_players(2))
    g.start_game({"target_score": 50})
    assert len(g.hands["p1"]) == 7
    assert len(g.hands["p2"]) == 7
    assert len(g.boneyard) == 14
    assert "hands" not in g.get_public_state()

    # Force blocked round resolution
    g.chain = [(6, 6)]
    g.left_end = 6
    g.right_end = 6
    g.boneyard = []
    g.hands["p1"] = [(0, 1)]  # 1 pip
    g.hands["p2"] = [(5, 4), (5, 5)]  # 19 pips
    g.turn_idx = 0
    g.turn_player_id = "p1"
    ok, err = g.handle_action("p1", "pass", {})
    assert ok, err
    ok, err = g.handle_action("p2", "pass", {})
    assert ok, err
    # p1 earned 19 pts and started round 2
    assert g.players[0].score == 19
    assert g.round_number == 2


def test_ludo_triple_six_forfeit_safe_squares_and_capture():
    g = LudoGame("LUD001", make_players(2))
    g.start_game()
    # Force 3 consecutive 6s check
    g.tokens["p1"] = [0, 5, -1, -1]
    g.consecutive_sixes = 2
    # Simulate rolling a 6 directly through handle_action by patching random
    import backend.games.ludo_game as ludo_mod
    orig_randint = ludo_mod.random.randint
    try:
        ludo_mod.random.randint = lambda a, b: 6
        ok, err = g.handle_action("p1", "roll", {})
        assert ok, err
        # 3rd six forfeits turn to p2!
        assert g.turn_player_id == "p2"
    finally:
        ludo_mod.random.randint = orig_randint

    # Capture check on non-safe square: p1 at rel 2 (track 2), p2 starts at color 2 (offset 26)
    g.turn_idx = 0
    g.turn_player_id = "p1"
    g.subphase = "move"
    g.dice_value = 2
    g.tokens["p1"] = [2, -1, -1, -1]  # moves to rel 4 -> track 4 (not safe)
    # p2 color is 2 (offset 26); track 4 = (26 + 30) % 52 = 4 -> rel 30
    g.tokens["p2"] = [30, -1, -1, -1]
    ok, err = g.handle_action("p1", "move", {"token": 0})
    assert ok, err
    assert g.tokens["p2"][0] == -1  # Sent back to yard!
    assert g.turn_player_id == "p1"  # Bonus roll granted on capture!


def test_skru_powers_basra_and_call_skru_privacy():
    g = SkruGame("SKR001", make_players(3, bots_from=2))
    g.start_game()
    assert g.phase == "pre_game"
    pub = g.get_public_state()
    assert all(slot == {"hidden": True} for slot in pub["hands"]["p1"])
    priv1 = g.get_private_state("p1")
    assert set(priv1["initial_bottom"].keys()) == {"2", "3"}

    # Advance to playing
    g.handle_action("p1", "ready", {})
    g.handle_action("p2", "ready", {})
    assert g.phase == "playing"
    assert g.turn_player_id == "p1"

    # Test Basra toss match
    target_card = g.hands["p1"][0]
    g.discard_pile.append(dict(target_card))
    ok, err = g.handle_action("p1", "basra", {"slot": 0})
    assert ok, err
    assert g.hands["p1"][0] is None

    # Test calling SKRU on p2
    ok, err = g.handle_action("p2", "skru", {})
    assert ok, err
    assert g.skru_caller_id == "p2"
    # p3 gets final turn, p1 gets final turn, then tally
    g.handle_action("p3", "draw_deck", {})
    g.handle_action("p3", "swap_drawn", {"slot": 0})
    assert g.phase == "playing"
    g.handle_action("p1", "draw_deck", {})
    g.handle_action("p1", "swap_drawn", {"slot": 1})
    assert g.phase == "finished"


def test_trivia_and_countries_scoring_and_modes():
    tq = QaTriviaGame("QA0001", make_players(1))
    tq.start_game({"category": "Science", "rounds": 4})
    assert tq.TITLE == "QA"
    correct = tq.questions[0]["correct_index"]
    ok, err = tq.handle_action("p1", "answer", {"choice": correct})
    assert ok, err
    assert tq.subphase == "reveal"
    assert 500 <= tq.players[0].score <= 1000

    # Unified Atlas category includes all 6 interactive country mechanics + SVG flags
    atlas_qa = QaTriviaGame("QAAT01", make_players(1))
    atlas_qa.start_game({"category": "Atlas", "rounds": 12})
    modes = [q["mode"] for q in atlas_qa.questions]
    assert modes[:4] == ["flag", "capital", "borders", "mystery"]
    assert "population_area" in modes
    assert "characteristics" in modes
    assert atlas_qa.questions[0].get("flag_svg")
    border_q = atlas_qa.questions[2]
    assert len(border_q["border_list"]) == 3
    ok, err = atlas_qa.handle_action("p1", "answer", {"choice": atlas_qa.questions[0]["correct_index"]})
    assert ok, err

    # Flags-only category produces SVG flag challenges
    flags_qa = QaTriviaGame("QAFL01", make_players(1))
    flags_qa.start_game({"category": "Flags", "rounds": 6})
    assert len(flags_qa.questions) == 6
    assert all(q["mode"] == "flag" and q.get("flag_svg") for q in flags_qa.questions)

    # All mix category blends both Trivia and Atlas items
    mix_qa = QaTriviaGame("QAMX01", make_players(1))
    mix_qa.start_game({"category": "All", "rounds": 10})
    assert any(q["mode"] == "trivia" for q in mix_qa.questions)
    assert any(q["mode"] != "trivia" for q in mix_qa.questions)

    # War category with difficulty filtering
    war_qa = QaTriviaGame("QAWAR1", make_players(1))
    war_qa.start_game({"category": "War", "difficulty": "hard", "rounds": 8})
    assert len(war_qa.questions) == 8
    assert all(q["category"] == "War" for q in war_qa.questions)
    assert all(q.get("difficulty") == "hard" for q in war_qa.questions)

    # 1,800 question bank completeness: 300 per topic (100 easy, 100 mid, 100 hard)
    from backend.games.qa_trivia_game import QUESTION_BANK
    assert len(QUESTION_BANK) == 1800
    for topic in ["War", "History", "Science", "Logic & Pattern IQ", "General Knowledge", "Tech & Pop Culture"]:
        topic_qs = [q for q in QUESTION_BANK if q["category"] == topic]
        assert len(topic_qs) == 300
        assert len([q for q in topic_qs if q.get("difficulty") == "easy"]) == 100
        assert len([q for q in topic_qs if q.get("difficulty") == "mid"]) == 100
        assert len([q for q in topic_qs if q.get("difficulty") == "hard"]) == 100


def test_globe_four_modes_heatmap_privacy_and_shortest_path():
    g = GlobeGame("GLB001", make_players(2))
    g.start_game({"mode": "mix", "rounds": 8})
    modes = [r["mode"] for r in g.rounds]
    assert modes[:4] == ["name", "flag", "hint", "borders_between"]

    # Round 1: Locate by Name -> test private heatmap & target secrecy
    pub = g.get_public_state()
    assert pub["subphase"] == "question"
    assert pub["reveal"] is None
    target_code = g.rounds[0]["target"]["code"]
    wrong_code = next(c["code"] for c in COUNTRIES_BANK if c["code"] != target_code)

    ok, err = g.handle_action("p1", "guess", {"code": wrong_code})
    assert ok, err
    priv1 = g.get_private_state("p1")
    priv2 = g.get_private_state("p2")
    assert len(priv1["guesses"]) == 1
    assert priv1["guesses"][0]["is_correct"] is False
    assert priv1["guesses"][0]["distance_km"] > 0
    assert priv2["guesses"] == []  # Isolated per player!

    # Solve round 1 for p1 and verify points; p2 solves directly on 1st attempt
    ok, err = g.handle_action("p1", "guess", {"code": target_code})
    assert ok, err
    ok, err = g.handle_action("p2", "guess", {"code": target_code})
    assert ok, err
    assert g.subphase == "reveal"
    assert g.players[1].score > g.players[0].score

    # Jump to Round 3 (hint) and verify extra hint unlocks
    g.round_idx = 2
    g._begin_question(time.time())
    assert len(g.get_private_state("p1")["hints_visible"]) == 2
    ok, err = g.handle_action("p1", "reveal_hint", {})
    assert ok, err
    assert len(g.get_private_state("p1")["hints_visible"]) == 3

    # Jump to Round 4 (borders_between) and verify shortest path BFS calculation
    g.round_idx = 3
    g._begin_question(time.time())
    q4 = g.rounds[3]
    a_code = q4["country_a"]["code"]
    b_code = q4["country_b"]["code"]
    bfs = shortest_border_path(a_code, b_code)
    assert bfs is not None
    expected_between = len(bfs) - 2
    assert q4["min_between"] == expected_between

    p1_before = g.players[0].score
    ok, err = g.handle_action("p1", "answer_between", {"count": expected_between})
    assert ok, err
    ok, err = g.handle_action("p2", "answer_between", {"count": expected_between + 1})
    assert ok, err
    assert g.subphase == "reveal"
    assert g.players[0].score >= p1_before + 1000
    assert len(g.get_public_state()["reveal"]["shortest_path"]) == len(bfs)


def test_country_dataset_completeness_and_qa_countries_category():
    assert len(COUNTRIES_BANK) >= 195
    flags_root = Path(__file__).resolve().parent.parent / "frontend" / "flags"
    for c in COUNTRIES_BANK:
        assert c["population"] > 0
        assert c["area_km2"] > 0
        assert c["capital"]
        assert c["landmark_clue"]
        assert len(c.get("characteristics", [])) >= 3
        assert (flags_root / f"{c['code'].lower()}.svg").exists()
        for nb in c.get("border_codes", []):
            assert c["code"] in COUNTRY_BY_CODE[nb]["border_codes"]

    tq = QaTriviaGame("QA00C1", make_players(1))
    tq.start_game({"category": "Countries", "rounds": 10})
    assert len(tq.questions) == 10
    assert all(q["category"] == "Atlas" and len(q["options"]) == 4 for q in tq.questions)


def test_monopoly_buy_auction_houses_trade_and_bankruptcy():
    g = MonopolyGame("MON001", make_players(2))
    g.start_game()
    # p1 buys Baltic Ave (id 3) via direct placement
    g.p_state["p1"]["pos"] = 3
    g.subphase = "buy_or_auction"
    ok, err = g.handle_action("p1", "buy", {})
    assert ok, err
    assert g.ownership[3] == "p1"

    # Give p1 Mediterranean (id 1) to form brown monopoly and build even houses
    g.ownership[1] = "p1"
    g.turn_player_id = "p1"
    g.subphase = "end_turn"
    ok, err = g.handle_action("p1", "build_house", {"tile_id": 1})
    assert ok, err
    # Even rule prevents second house on tile 1 before tile 3 has 1 house
    ok_even, _ = g.handle_action("p1", "build_house", {"tile_id": 1})
    assert not ok_even

    # Trigger 15s auction on Oriental Ave (id 6)
    g.p_state["p1"]["pos"] = 6
    g.subphase = "buy_or_auction"
    ok, err = g.handle_action("p1", "pass_buy", {})
    assert ok, err
    assert g.subphase == "auction"
    ok, err = g.handle_action("p2", "bid", {"amount": 75})
    assert ok, err
    ok, err = g.handle_action("p1", "pass_auction", {})
    assert ok, err
    assert g.ownership[6] == "p2"
    assert g.p_state["p2"]["cash"] == 1500 - 75

    # Trade proposal + acceptance
    ok, err = g.handle_action(
        "p1",
        "propose_trade",
        {"to_id": "p2", "offer_cash": 100, "request_cash": 0, "offer_props": [], "request_props": [6]},
    )
    assert ok, err
    ok, err = g.handle_action("p2", "accept_trade", {})
    assert ok, err
    assert g.ownership[6] == "p1"

    # Bankruptcy transfer when p2 cannot cover huge debt
    g.p_state["p2"]["cash"] = 10
    g._charge_player("p2", 5000, "p1", "Boardwalk Hotel Rent")
    assert g.phase == "finished"
    assert g.winner_ids == ["p1"]


@pytest.mark.parametrize(
    "cls",
    [ChessGame, BackgammonGame, DominoesGame, LudoGame, SkruGame, UnoGame, MonopolyGame],
)
def test_bot_simulations_never_stall(cls):
    g = cls("BOTTST", make_players(2, bots_from=0))
    g.start_game()
    if g.phase == "pre_game":
        for p in g.players:
            g.handle_action(p.id, "ready", {})

    steps = 0
    while g.phase == "playing" and steps < 180:
        active = g.get_active_bot_ids()
        assert active, f"{cls.GAME_TYPE} stalled with no active bot ids in phase={g.phase}"
        acted = False
        for bid in active:
            cmd = g.get_bot_action(bid)
            if cmd is not None:
                ok, err = g.handle_action(bid, cmd[0], cmd[1])
                assert ok, f"{cls.GAME_TYPE} bot action failed: {cmd} -> {err}"
                acted = True
                break
        assert acted, f"{cls.GAME_TYPE} active bots returned None action"
        steps += 1


def test_difficulty_profiles_across_all_11_engines():
    # Minesweeper easy / mid / hard
    for diff, dims in [("easy", (9, 9, 10)), ("mid", (16, 16, 40)), ("hard", (16, 30, 99))]:
        ms = MinesweeperGame("DFMS01", make_players(1))
        ms.start_game({"difficulty": diff})
        assert (ms.rows, ms.cols, ms.total_mines) == dims

    # Snake pace & points scaling
    for diff, (ms_step, pts) in [("easy", (165, 10)), ("mid", (125, 10)), ("hard", (85, 15))]:
        snk = SnakeGame("DFSN01", make_players(1))
        snk.start_game({"difficulty": diff})
        pub = snk.get_public_state()
        assert pub["difficulty"] == diff
        assert pub["step_ms"] == ms_step
        assert pub["points_per_food"] == pts

    # Unified QA timers (standard + mystery)
    for diff, (std_sec, mys_sec) in [("easy", (20.0, 24.0)), ("mid", (15.0, 18.0)), ("hard", (10.0, 12.0))]:
        qa = QaTriviaGame("DFQA01", make_players(1))
        qa.start_game({"difficulty": diff, "category": "Atlas", "rounds": 6})
        assert qa.question_seconds == std_sec
        assert qa.mystery_seconds == mys_sec
        assert qa.get_public_state()["question_duration"] == std_sec

    # Globe timers & guess limits
    for diff, (dur, guesses) in [("easy", (55.0, 7)), ("mid", (40.0, 6)), ("hard", (25.0, 4))]:
        gl = GlobeGame("DFGL01", make_players(1))
        gl.start_game({"difficulty": diff, "mode": "name", "rounds": 4})
        pub = gl.get_public_state()
        assert pub["duration"] == dur
        assert pub["question"]["max_guesses"] == guesses

    # Skru peek window
    for diff, sec in [("easy", 12.0), ("mid", 10.0), ("hard", 7.0)]:
        sk = SkruGame("DFSK01", make_players(2, bots_from=1))
        sk.start_game({"difficulty": diff})
        assert sk.peek_seconds == sec

    # Monopoly starting treasury
    for diff, cash in [("easy", 1800), ("mid", 1500), ("hard", 1200)]:
        mo = MonopolyGame("DFMO01", make_players(2, bots_from=1))
        mo.start_game({"difficulty": diff})
        assert mo.p_state["p1"]["cash"] == cash


@pytest.mark.parametrize("diff", ["easy", "hard"])
@pytest.mark.parametrize(
    "cls",
    [ChessGame, BackgammonGame, DominoesGame, LudoGame, SkruGame, UnoGame, MonopolyGame],
)
def test_bot_simulations_easy_and_hard(cls, diff):
    g = cls("BTDF01", make_players(2, bots_from=0))
    g.start_game({"difficulty": diff})
    if g.phase == "pre_game":
        for p in g.players:
            g.handle_action(p.id, "ready", {})

    steps = 0
    while g.phase == "playing" and steps < 60:
        active = g.get_active_bot_ids()
        assert active
        acted = False
        for bid in active:
            cmd = g.get_bot_action(bid)
            if cmd is not None:
                ok, err = g.handle_action(bid, cmd[0], cmd[1])
                assert ok, f"{cls.GAME_TYPE} ({diff}) bot action failed: {cmd} -> {err}"
                acted = True
                break
        assert acted
        steps += 1


def test_uno_rules_actions_wilds_uno_shout_and_catch():
    deck = build_uno_deck()
    assert len(deck) == 108

    g = UnoGame("UNO001", make_players(3))
    g.start_game({"difficulty": "mid"})
    assert all(len(g.hands[p.id]) == 7 for p in g.players)
    pub = g.get_public_state()
    assert "hands" not in pub
    assert pub["card_counts"] == {"p1": 7, "p2": 7, "p3": 7}

    # Test Reverse flips direction in 3P
    g.discard_pile = [{"id": 900, "color": "blue", "kind": "5", "label": "5", "points": 5}]
    g.active_color = "blue"
    g.turn_idx = 0
    g.turn_player_id = "p1"
    g.hands["p1"] = [
        {"id": 901, "color": "blue", "kind": "reverse", "label": "REV", "points": 20},
        {"id": 902, "color": "red", "kind": "3", "label": "3", "points": 3},
    ]
    ok, err = g.handle_action("p1", "play", {"index": 0})
    assert ok, err
    assert g.direction == -1
    assert g.turn_player_id == "p3"

    # p1 landed on 1 card without calling UNO -> p2 catches p1 (+2 penalty cards!)
    assert "p1" in g.get_public_state()["uno_vulnerable_ids"]
    ok, err = g.handle_action("p2", "catch_uno", {"target_id": "p1"})
    assert ok, err
    assert len(g.hands["p1"]) == 3

    # Wild +4 requires valid color, draws 4 for victim & skips victim
    g.turn_idx = 2
    g.turn_player_id = "p3"
    g.hands["p3"] = [
        {"id": 903, "color": "wild", "kind": "wild4", "label": "+4", "points": 50},
        {"id": 904, "color": "green", "kind": "7", "label": "7", "points": 7},
    ]
    ok_bad, _ = g.handle_action("p3", "play", {"index": 0, "color": "orange"})
    assert not ok_bad
    # Shout UNO from 2 cards before playing down to 1
    ok, err = g.handle_action("p3", "shout_uno", {})
    assert ok, err
    p2_before = len(g.hands["p2"])
    ok, err = g.handle_action("p3", "play", {"index": 0, "color": "green"})
    assert ok, err
    assert g.active_color == "green"
    assert len(g.hands["p2"]) == p2_before + 4
    assert "p3" not in g.get_public_state()["uno_vulnerable_ids"]

    # Victory check when final card played in 2P where Reverse acts as Skip
    g2 = UnoGame("UNO002", make_players(2))
    g2.start_game()
    g2.discard_pile = [{"id": 950, "color": "yellow", "kind": "2", "label": "2", "points": 2}]
    g2.active_color = "yellow"
    g2.hands["p1"] = [
        {"id": 951, "color": "yellow", "kind": "reverse", "label": "REV", "points": 20},
        {"id": 952, "color": "yellow", "kind": "9", "label": "9", "points": 9},
    ]
    ok, err = g2.handle_action("p1", "play", {"index": 0})
    assert ok, err
    assert g2.turn_player_id == "p1"  # 2P Reverse plays again!
    ok, err = g2.handle_action("p1", "play", {"index": 0})
    assert ok, err
    assert g2.phase == "finished"
    assert g2.winner_ids == ["p1"]


def test_custom_difficulty_normalizes_across_all_11_engines():
    from backend.games import GAME_REGISTRY

    assert len(GAME_REGISTRY) == 11
    for game_type, cls in GAME_REGISTRY.items():
        players = make_players(max(cls.MIN_PLAYERS, 2 if cls.MAX_PLAYERS >= 2 else 1))
        if cls.MIN_PLAYERS == 1 and not cls.SUPPORTS_BOTS:
            players = make_players(1)
        g = cls("CST001", players, {"difficulty": "custom"})
        if game_type == "minesweeper":
            assert g.SUPPORTS_CUSTOM_DIFFICULTY is True
            assert g.get_difficulty() == "custom"
        else:
            assert g.SUPPORTS_CUSTOM_DIFFICULTY is False
            assert g.get_difficulty() == "mid"

        g.start_game({"difficulty": "custom"})
        if game_type == "minesweeper":
            assert g.get_difficulty() == "custom"
        else:
            assert g.get_difficulty() == "mid"
        assert isinstance(g.get_public_state(), dict)

        # Also check legacy/invalid aliases normalize cleanly without KeyError
        g.start_game({"difficulty": "totally_unknown_preset"})
        assert g.get_difficulty() == "mid"


def test_minesweeper_difficulty_switching_detonation_clear_and_disconnect():
    ms = MinesweeperGame("MS002", make_players(1))
    ms.start_game({"difficulty": "custom", "width": 22, "height": 14, "booms": 30})
    assert (ms.difficulty, ms.rows, ms.cols, ms.total_mines) == ("custom", 14, 22, 30)

    # Switching custom -> easy -> hard must clear stale dimensions and apply preset dims
    ms.start_game({"difficulty": "easy"})
    assert (ms.difficulty, ms.rows, ms.cols, ms.total_mines) == ("easy", 9, 9, 10)
    ms.start_game({"difficulty": "hard"})
    assert (ms.difficulty, ms.rows, ms.cols, ms.total_mines) == ("hard", 16, 30, 99)

    # Non-int / bool inputs rejected cleanly; booms=0 clamped to >= 1
    ms.start_game({"difficulty": "custom", "width": 9, "height": 9, "booms": 0})
    assert ms.total_mines == 1
    ok, _ = ms.handle_action("p1", "reveal", {"r": "bad", "c": 0})
    assert not ok
    ok, _ = ms.handle_action("p1", "reveal", {"r": True, "c": 0})
    assert not ok

    # Detonation reveals mines and finishes solo match with no winner
    ok, err = ms.handle_action("p1", "reveal", {"r": 0, "c": 0})
    assert ok, err
    if ms.phase == "playing":
        mine_r, mine_c = next(iter(ms.boards["p1"]["mines"]))
        ok, err = ms.handle_action("p1", "reveal", {"r": mine_r, "c": mine_c})
        assert ok, err
        assert ms.phase == "finished"
        assert ms.winner_ids == []
        assert ms.boards["p1"]["status"] == "exploded"
        assert len(ms.get_private_state("p1")["mines"]) == 1

    # Full clear win in solo Minesweeper
    ms_win = MinesweeperGame("MSWIN", make_players(1))
    ms_win.start_game({"difficulty": "easy"})
    ok, err = ms_win.handle_action("p1", "reveal", {"r": 4, "c": 4})
    assert ok, err
    board = ms_win.boards["p1"]
    for r in range(ms_win.rows):
        for c in range(ms_win.cols):
            if ms_win.phase != "playing":
                break
            if (r, c) not in board["mines"] and (r, c) not in board["revealed"]:
                ok, err = ms_win.handle_action("p1", "reveal", {"r": r, "c": c})
                assert ok, err
    assert ms_win.phase == "finished"
    assert ms_win.winner_ids == ["p1"]
    assert ms_win.boards["p1"]["status"] == "cleared"
    assert ms_win.players[0].score >= 1000

    # Multiplayer: disconnected player must not block match finish
    ms_mp = MinesweeperGame("MSMP01", make_players(2))
    ms_mp.start_game({"difficulty": "easy"})
    ok, err = ms_mp.handle_action("p1", "reveal", {"r": 4, "c": 4})
    assert ok, err
    assert ms_mp.on_player_disconnect("p2") is True
    mine_r, mine_c = next(iter(ms_mp.boards["p1"]["mines"]))
    ok, err = ms_mp.handle_action("p1", "reveal", {"r": mine_r, "c": mine_c})
    assert ok, err
    assert ms_mp.phase == "finished"
    assert ms_mp.winner_ids == ["p1"]


def test_uno_empty_deck_hard_bot_no_softlock_and_full_games_finish():
    g = UnoGame("UNOEMPTY", make_players(2, bots_from=0))
    g.start_game({"difficulty": "hard"})
    g.deck = []
    g.discard_pile = [{"id": 999, "color": "blue", "kind": "5", "label": "5", "points": 5}]
    g.active_color = "blue"
    g.turn_idx = 0
    g.turn_player_id = "p1"
    g.hands["p1"] = [{"id": 1, "color": "red", "kind": "9", "label": "9", "points": 9}]
    g.hands["p2"] = [{"id": 2, "color": "green", "kind": "3", "label": "3", "points": 3}]
    g.uno_declared = {"p1": True, "p2": False}

    # With empty draw deck and <=1 discard card, Hard bot must NOT return catch_uno
    cmd1 = g.get_bot_action("p1")
    assert cmd1 is not None
    assert cmd1[0] != "catch_uno"
    ok_catch, _ = g.handle_action("p1", "catch_uno", {"target_id": "p2"})
    assert not ok_catch

    # Both bots draw/pass on empty deck -> lowest-points finish without soft-lock
    steps = 0
    while g.phase == "playing" and steps < 10:
        cmd = g.get_bot_action(g.turn_player_id)
        assert cmd is not None
        ok, err = g.handle_action(g.turn_player_id, cmd[0], cmd[1])
        assert ok, err
        steps += 1
    assert g.phase == "finished"
    assert g.winner_ids == ["p2"]

    # Full bot matches across easy & hard reach finished reliably
    for diff in ("easy", "hard"):
        sim = UnoGame(f"UNOSIM_{diff}", make_players(3, bots_from=0))
        sim.start_game({"difficulty": diff})
        steps = 0
        while sim.phase == "playing" and steps < 600:
            cmd = sim.get_bot_action(sim.turn_player_id)
            assert cmd is not None
            ok, err = sim.handle_action(sim.turn_player_id, cmd[0], cmd[1])
            assert ok, err
            steps += 1
        assert sim.phase == "finished"
        assert len(sim.winner_ids) >= 1


def test_monopoly_uneven_houses_trade_validation_bankruptcy_and_third_turn_jail_bail():
    # 1. Uneven house sell during bot resolve_debt chooses highest house count
    g = MonopolyGame("MONDEBT", make_players(2, bots_from=0))
    g.start_game({"difficulty": "mid"})
    g.ownership[1] = "p1"
    g.ownership[3] = "p1"
    g.houses[1] = 2
    g.houses[3] = 1
    g.p_state["p1"]["cash"] = 0
    g.turn_idx = 0
    g.turn_player_id = "p1"
    g._charge_player("p1", 60, None, "Luxury Tax")
    assert g.subphase == "resolve_debt"
    bot_cmd = g.get_bot_action("p1")
    assert bot_cmd == ("sell_house", {"tile_id": 1})
    ok, err = g.handle_action("p1", bot_cmd[0], bot_cmd[1])
    assert ok, err
    assert g.houses[1] == 1

    # 2. Trade re-validation & auction/debt guards & bankrupt clearing pending_trade
    g2 = MonopolyGame("MONTRD", make_players(3))
    g2.start_game()
    g2.ownership[1] = "p1"
    g2.ownership[3] = "p1"
    g2.ownership[6] = "p2"
    ok, err = g2.handle_action(
        "p1",
        "propose_trade",
        {"to_id": "p2", "offer_cash": 100, "request_cash": 0, "offer_props": [1], "request_props": [6]},
    )
    assert ok, err
    assert g2.pending_trade is not None

    # Trade forbidden during auction
    g2.subphase = "auction"
    ok_auc, _ = g2.handle_action("p2", "accept_trade", {})
    assert not ok_auc
    g2.subphase = "end_turn"

    # If proposer builds a house on the color set before acceptance, accept_trade rejects & clears trade
    g2.turn_player_id = "p1"
    ok, err = g2.handle_action("p1", "build_house", {"tile_id": 1})
    assert ok, err
    ok_house, _ = g2.handle_action("p2", "accept_trade", {})
    assert not ok_house
    assert g2.pending_trade is None

    # Cash validation on accept_trade
    g2.houses[1] = 0
    ok, err = g2.handle_action(
        "p1",
        "propose_trade",
        {"to_id": "p2", "offer_cash": 200, "request_cash": 0, "offer_props": [1], "request_props": [6]},
    )
    assert ok, err
    g2.p_state["p1"]["cash"] = 50
    ok_cash, _ = g2.handle_action("p2", "accept_trade", {})
    assert not ok_cash
    assert g2.pending_trade is None

    # Bankrupt player clears pending_trade
    ok, err = g2.handle_action(
        "p1",
        "propose_trade",
        {"to_id": "p2", "offer_cash": 10, "request_cash": 0, "offer_props": [1], "request_props": [6]},
    )
    assert ok, err
    assert g2.pending_trade is not None
    g2._bankrupt_player("p1", None, "Test bankruptcy")
    assert g2.pending_trade is None

    # 3. 3rd-turn Jail $50 bail charged even when landing on unowned property or debt
    import backend.games.monopoly_game as mono_mod

    g3 = MonopolyGame("MONJAIL", make_players(2))
    g3.start_game()
    g3.p_state["p1"].update({"pos": 10, "in_jail": True, "jail_turns": 2, "cash": 500})
    g3.turn_idx = 0
    g3.turn_player_id = "p1"
    g3.subphase = "roll"
    orig_randint = mono_mod.random.randint
    try:
        seq = iter([1, 2])  # sum 3 -> lands on unowned States Ave (id 13)
        mono_mod.random.randint = lambda a, b: next(seq)
        ok, err = g3.handle_action("p1", "roll", {})
        assert ok, err
        assert g3.p_state["p1"]["in_jail"] is False
        assert g3.p_state["p1"]["pos"] == 13
        assert g3.subphase == "buy_or_auction"
        assert g3.p_state["p1"]["cash"] == 450

        # Case B: <$50 cash on 3rd turn Jail triggers resolve_debt for $50 before moving
        g3.p_state["p1"].update({"pos": 10, "in_jail": True, "jail_turns": 2, "cash": 20})
        g3.ownership[3] = "p1"  # mortgage value $30
        g3.subphase = "roll"
        seq2 = iter([1, 2])
        mono_mod.random.randint = lambda a, b: next(seq2)
        ok, err = g3.handle_action("p1", "roll", {})
        assert ok, err
        assert g3.subphase == "resolve_debt"
        assert g3.pending_debt["amount"] == 50
        assert g3.pending_debt["post_move_steps"] == 3
        ok, err = g3.handle_action("p1", "mortgage", {"tile_id": 3})
        assert ok, err
        ok, err = g3.handle_action("p1", "pay_debt", {})
        assert ok, err
        assert g3.p_state["p1"]["cash"] == 0
        assert g3.p_state["p1"]["pos"] == 13
        assert g3.subphase == "buy_or_auction"
    finally:
        mono_mod.random.randint = orig_randint


def test_skru_invalid_inputs_memory_invalidation_and_ready_players():
    g = SkruGame("SKR002", make_players(3, bots_from=2))
    g.start_game({"difficulty": "mid"})
    pub_pre = g.get_public_state()
    assert "p3" in pub_pre["ready_players"]
    assert "p1" not in pub_pre["ready_players"]

    g.handle_action("p1", "ready", {})
    assert "p1" in g.get_public_state()["ready_players"]
    g.handle_action("p2", "ready", {})
    assert g.phase == "playing"

    # Reject non-int / bool slot inputs across all slot-taking actions cleanly
    for bad_slot in ("abc", None, True, -1, 9):
        ok, _ = g.handle_action("p1", "basra", {"slot": bad_slot})
        assert not ok

    g.drawn_card = {"id": 500, "code": "2", "label": "2", "points": 2, "power": None}
    g.turn_stage = "resolve_drawn"
    for bad_slot in ("abc", None, True):
        ok, _ = g.handle_action("p1", "swap_drawn", {"slot": bad_slot})
        assert not ok

    g.turn_stage = "power_peek_self"
    for bad_slot in ("abc", None, True):
        ok, _ = g.handle_action("p1", "peek", {"slot": bad_slot})
        assert not ok

    g.turn_stage = "power_peek_opp"
    for bad_slot in ("abc", None, True):
        ok, _ = g.handle_action("p1", "peek", {"target_id": "p2", "slot": bad_slot})
        assert not ok

    g.turn_stage = "power_blind_swap"
    for bad_slot in ("abc", None, True):
        ok, _ = g.handle_action("p1", "swap", {"my_slot": bad_slot, "target_id": "p2", "opp_slot": 0})
        assert not ok
        ok, _ = g.handle_action("p1", "swap", {"my_slot": 0, "target_id": "p2", "opp_slot": bad_slot})
        assert not ok

    g.turn_stage = "power_king_peek"
    for bad_slot in ("abc", None, True):
        ok, _ = g.handle_action("p1", "peek", {"my_slot": bad_slot, "target_id": "p2", "opp_slot": 0})
        assert not ok

    # Jack blind swap updates bot_memory and invalidates affected last_peek
    g.hands["p1"][1] = {"id": 601, "code": "6", "label": "6", "points": 6, "power": None}
    g.hands["p2"][0] = {"id": 602, "code": "1", "label": "1", "points": 1, "power": None}
    g.bot_memory["p3"] = {"p1:1": 6, "p2:0": 1}
    g.private_peeks["p1"]["last_peek"] = {"owner_id": "p2", "slot": 0, "card": g.hands["p2"][0]}
    g.turn_idx = 0
    g.turn_player_id = "p1"
    g.turn_stage = "power_blind_swap"
    ok, err = g.handle_action("p1", "swap", {"my_slot": 1, "target_id": "p2", "opp_slot": 0})
    assert ok, err
    assert g.bot_memory["p3"]["p1:1"] == 1
    assert g.bot_memory["p3"]["p2:0"] == 6
    assert g.private_peeks["p1"]["last_peek"] is None

    # King look_swap swaps memory and invalidates last_peek when swap=True
    g.turn_idx = 0
    g.turn_player_id = "p1"
    g.turn_stage = "power_king_peek"
    g.private_peeks["p2"]["last_peek"] = {"owner_id": "p1", "slot": 1, "card": g.hands["p1"][1]}
    ok, err = g.handle_action("p1", "peek", {"my_slot": 1, "target_id": "p2", "opp_slot": 0})
    assert ok, err
    assert g.turn_stage == "power_king_decide"
    ok, err = g.handle_action("p1", "king_decide", {"swap": True})
    assert ok, err
    assert g.bot_memory["p3"]["p1:1"] == 6
    assert g.bot_memory["p3"]["p2:0"] == 1
    assert g.private_peeks["p2"]["last_peek"] is None


def test_globe_done_players_easy_borders_pool_and_flag_svg_secrecy():
    # Easy mode: max_locate_guesses == 7; done_players only marks after 7 guesses
    g_easy = GlobeGame("GLBEZ", make_players(2))
    g_easy.start_game({"difficulty": "easy", "mode": "name", "rounds": 4})
    assert g_easy.max_locate_guesses == 7
    target_code = g_easy.rounds[0]["target"]["code"]
    wrong_codes = [c["code"] for c in COUNTRIES_BANK if c["code"] != target_code][:7]
    for code in wrong_codes[:6]:
        ok, err = g_easy.handle_action("p1", "guess", {"code": code})
        assert ok, err
    assert "p1" not in g_easy.get_public_state()["done_players"]
    ok, err = g_easy.handle_action("p1", "guess", {"code": wrong_codes[6]})
    assert ok, err
    assert "p1" in g_easy.get_public_state()["done_players"]

    # Hard mode: max_locate_guesses == 4
    g_hard = GlobeGame("GLBHD", make_players(1))
    g_hard.start_game({"difficulty": "hard", "mode": "name", "rounds": 4})
    assert g_hard.max_locate_guesses == 4
    target_h = g_hard.rounds[0]["target"]["code"]
    wrong_h = [c["code"] for c in COUNTRIES_BANK if c["code"] != target_h][:4]
    for code in wrong_h:
        ok, err = g_hard.handle_action("p1", "guess", {"code": code})
        assert ok, err
    assert g_hard.subphase == "reveal"
    assert "p1" in g_hard.get_public_state()["done_players"]

    # Easy borders_between pool restricted to top 70 most populous nations
    top_70_codes = {
        c["code"]
        for c in sorted(COUNTRIES_BANK, key=lambda c: c.get("population", 0), reverse=True)[:70]
    }
    g_brd = GlobeGame("GLBBRD", make_players(1))
    g_brd.start_game({"difficulty": "easy", "mode": "borders_between", "rounds": 8})
    for rnd in g_brd.rounds:
        assert rnd["country_a"]["code"] in top_70_codes
        assert rnd["country_b"]["code"] in top_70_codes
        assert rnd["min_between"] <= 4

    # Flag mode: sanitized data URI during question (no flag_code / /flags/xx.svg leak)
    g_flg = GlobeGame("GLBFLG", make_players(1))
    g_flg.start_game({"difficulty": "mid", "mode": "flag", "rounds": 4})
    q_pub = g_flg.get_public_state()["question"]
    t_code = g_flg.rounds[0]["target"]["code"]
    assert "flag_code" not in q_pub
    assert q_pub["flag_svg"].startswith("data:image/svg+xml;base64,")
    assert f"/flags/{t_code.lower()}.svg" not in q_pub["flag_svg"]
    g_flg._begin_reveal(time.time())
    rev_q = g_flg.get_public_state()["question"]
    assert rev_q["flag_code"] == t_code
    assert rev_q["flag_svg"].endswith(f"/flags/{t_code.lower()}.svg")


def test_qa_trivia_area_min_flag_secrecy_and_clean_question_bank(monkeypatch):
    import json
    import re
    from pathlib import Path
    import backend.games.qa_trivia_game as qa_mod
    from backend.data.country_store import COUNTRY_BY_NAME

    # 1. Verify area_min selects the smallest land area country among 4 choices
    orig_choice = qa_mod.random.choice

    def force_area_min(seq):
        if isinstance(seq, list) and seq == ["pop_max", "area_max", "area_min"]:
            return "area_min"
        return orig_choice(seq)

    monkeypatch.setattr(qa_mod.random, "choice", force_area_min)
    qs = qa_mod._build_atlas_questions(6, difficulty="mid", only_mode="population_area")
    assert len(qs) == 6
    for q in qs:
        assert "SMALLEST" in q["question"]
        areas = [COUNTRY_BY_NAME[opt.lower()]["area_km2"] for opt in q["options"]]
        assert areas[q["correct_index"]] == min(areas)
    monkeypatch.undo()

    # 2. Verify flag_svg during question hides ISO-2 country code and reveals it after answer
    qa_flags = QaTriviaGame("QAFLG2", make_players(1))
    qa_flags.start_game({"category": "Flags", "rounds": 4})
    t_code = qa_flags.questions[0]["flag_code"]
    q_pub = qa_flags.get_public_state()["question"]
    assert "flag_code" not in q_pub
    assert "correct_index" not in q_pub
    assert q_pub["flag_svg"].startswith("data:image/svg+xml;base64,")
    assert f"/flags/{t_code.lower()}.svg" not in q_pub["flag_svg"]

    ok, err = qa_flags.handle_action("p1", "answer", {"choice": qa_flags.questions[0]["correct_index"]})
    assert ok, err
    q_rev = qa_flags.get_public_state()["question"]
    assert q_rev["flag_code"] == t_code
    assert q_rev["flag_svg"].endswith(f"/flags/{t_code.lower()}.svg")
    assert "correct_index" in q_rev

    # 3. Verify qa_questions.json has 1,800 valid entries and zero synthetic placeholder templates
    bank_path = Path(__file__).resolve().parent.parent / "backend" / "data" / "qa_questions.json"
    bank = json.loads(bank_path.read_text(encoding="utf-8"))
    assert len(bank) == 1800
    patterns = [
        re.compile(r"Core\s+.+\s+Rule\s*#"),
        re.compile(r"Mastery Axiom\s*#"),
        re.compile(r"Global military operations of"),
    ]
    seen_questions: set[tuple[str, str]] = set()
    for row in bank:
        assert isinstance(row.get("options"), list) and len(row["options"]) == 4
        assert isinstance(row.get("correct_index"), int) and 0 <= row["correct_index"] < 4
        assert row.get("question") and row.get("explanation")
        blob = f"{row['question']} {' '.join(row['options'])} {row['explanation']}"
        assert not any(p.search(blob) for p in patterns), f"Placeholder found: {row['question']}"
        key = (row["category"], row["question"])
        assert key not in seen_questions
        seen_questions.add(key)


def test_chess_resign_benign_promo_move0_custom_finish_and_fen_unicode_digits():
    from backend.games.chess_game import parse_fen_placement

    # 1. Resign rejects non-players/spectators; benign promotion on non-pawn move succeeds
    g = ChessGame("CHSEC", make_players(2))
    g.start_game()
    ok_spec, _ = g.handle_action("spec1", "resign", {})
    assert not ok_spec
    assert g.phase == "playing"

    ok, err = g.handle_action("p1", "move", {"from": "g1", "to": "f3", "promotion": "Q"})
    assert ok, err
    assert g.board[5][5] == "N"

    # 2. Move-0 custom board checkmate finishes immediately on start_game()
    mate_board = [[None] * 8 for _ in range(8)]
    mate_board[0][7] = "k"  # h8
    mate_board[0][1] = "r"  # b8 defends b2
    mate_board[6][1] = "q"  # b2 checks a1
    mate_board[7][0] = "K"  # a1 checkmated!
    gc_mate = ChessGame("CHM0", make_players(2), {"custom_board": mate_board})
    gc_mate.start_game()
    assert gc_mate.phase == "finished"
    assert gc_mate.winner_ids == ["p2"]
    assert gc_mate.players[1].score == 1
    assert "Checkmate from starting setup" in gc_mate.win_reason

    # 3. Move-0 custom board stalemate finishes immediately as draw
    stale_board = [[None] * 8 for _ in range(8)]
    stale_board[0][7] = "k"  # h8
    stale_board[6][2] = "q"  # c2 covers a2, b2, b1 without checking a1
    stale_board[7][0] = "K"  # a1 stalemated!
    gc_stale = ChessGame("CHS0", make_players(2), {"custom_board": stale_board})
    gc_stale.start_game()
    assert gc_stale.phase == "finished"
    assert gc_stale.winner_ids == []
    assert "Stalemate from starting setup" in gc_stale.win_reason

    # 4. parse_fen_placement accepts valid ASCII digits and rejects Unicode digits cleanly
    assert parse_fen_placement("8/8/8/8/8/8/8/4K2k") is not None
    for bad_fen in (
        "²/8/8/8/8/8/8/4K2k",
        "١234567/8/8/8/8/8/8/4K2k",
        "８/8/8/8/8/8/8/4K2k",
    ):
        assert parse_fen_placement(bad_fen) is None


def test_backgammon_invalid_mode_last_dice_preserved_and_mahbosa_deadlock():
    import backend.games.backgammon_game as bg_mod

    # 1. Invalid mode defaults to classic
    g_inv = BackgammonGame("BGINV", make_players(2), {"mode": "not_a_real_mode"})
    assert g_inv.mode == "classic"
    g_inv.start_game({"mode": "bad_mode"})
    assert g_inv.mode == "classic"

    # 2. last_dice preserved when rolled dice have no legal moves
    g_blk = BackgammonGame("BGBLK", make_players(2))
    g_blk.start_game()
    g_blk.points = [0] * 24
    g_blk.points[0] = 15
    for pt in range(18, 24):
        g_blk.points[pt] = -2  # all entry points blocked
    g_blk.bar = {0: 1, 1: 0}
    g_blk.points[0] = 14
    g_blk.off = {0: 0, 1: 3}
    g_blk.turn_idx = 0
    g_blk.turn_player_id = "p1"
    g_blk.subphase = "roll"

    orig_randint = bg_mod.random.randint
    try:
        seq = iter([3, 5])
        bg_mod.random.randint = lambda a, b: next(seq)
        ok, err = g_blk.handle_action("p1", "roll", {})
        assert ok, err
        pub = g_blk.get_public_state()
        assert g_blk.turn_player_id == "p2"
        assert pub["dice"] == []
        assert pub["last_dice"] == [3, 5]
    finally:
        bg_mod.random.randint = orig_randint

    # 3. Mutual Mahbosa pin deadlock detection resolves match cleanly
    gm = BackgammonGame("BGMHDEAD", make_players(2), {"mode": "mahbosa"})
    gm.start_game()
    gm.points = [0] * 24
    gm.pinned = [0] * 24
    # White has 14 on point 0 (cannot go <0; cannot bear off because pinned[23]==1)
    # Black has 14 on point 23 (cannot go >23; cannot bear off because pinned[0]==-1)
    gm.points[0] = 14
    gm.pinned[0] = -1
    gm.points[23] = -14
    gm.pinned[23] = 1
    gm.off = {0: 0, 1: 0}
    gm.turn_idx = 0
    gm.turn_player_id = "p1"
    gm.subphase = "roll"
    ok, err = gm.handle_action("p1", "roll", {})
    assert ok, err
    assert gm.phase == "finished"
    assert "deadlock" in gm.win_reason.lower()


def test_snake_anticheat_bounds_and_zero_point_solo_finish():
    # Duration clamping & invalid telemetry rejection
    g_dur = SnakeGame("SNKDUR", make_players(1))
    g_dur.start_game({"duration": 5, "difficulty": "easy"})
    assert g_dur.duration == 15
    ok_bool, _ = g_dur.handle_action("p1", "sync", {"score": True, "length": 3, "alive": True})
    assert not ok_bool
    ok_str, _ = g_dur.handle_action("p1", "sync", {"score": "nan", "length": 3, "alive": True})
    assert not ok_str

    # Anti-cheat caps forged immediate score/length spikes
    g_dur.handle_action("p1", "sync", {"score": 999999, "length": 9999, "alive": True})
    assert g_dur.snakes["p1"]["score"] <= 100
    assert g_dur.snakes["p1"]["length"] <= 15

    # 0-point solo crash finishes with empty winner_ids
    g_zero = SnakeGame("SNK0", make_players(1))
    g_zero.start_game()
    ok, err = g_zero.handle_action("p1", "sync", {"score": 0, "length": 3, "alive": False})
    assert ok, err
    assert g_zero.phase == "finished"
    assert g_zero.winner_ids == []
    assert "0 points" in g_zero.win_reason


def test_dominoes_equal_ends_dedup_and_ludo_forfeit_dice_handling():
    import backend.games.ludo_game as ludo_mod

    # 1. Dominoes equal ends deduplicates playable sides to ["left"]
    dom = DominoesGame("DOMDEDUP", make_players(2))
    dom.start_game()
    dom.chain = [(4, 2), (2, 4)]
    dom.left_end = 4
    dom.right_end = 4
    dom.turn_idx = 0
    dom.turn_player_id = "p1"
    dom.hands["p1"] = [(4, 6)]
    priv = dom.get_private_state("p1")
    assert priv["playable"] == [{"tile": [4, 6], "sides": ["left"]}]
    ok_bad_tile, _ = dom.handle_action("p1", "play", {"tile": ["x", 1], "side": "left"})
    assert not ok_bad_tile

    # 2. Ludo preserves last_dice and clears dice_value on forfeit/no-move; resets consecutive_sixes on capture
    lud = LudoGame("LUDFORF", make_players(2))
    lud.start_game()
    lud.tokens["p1"] = [0, -1, -1, -1]
    lud.consecutive_sixes = 2
    orig_randint = ludo_mod.random.randint
    try:
        ludo_mod.random.randint = lambda a, b: 6
        ok, err = lud.handle_action("p1", "roll", {})
        assert ok, err
        pub = lud.get_public_state()
        assert lud.turn_player_id == "p2"
        assert pub["dice_value"] is None
        assert pub["last_dice"] == 6
        assert pub["consecutive_sixes"] == 0
    finally:
        ludo_mod.random.randint = orig_randint

    # Capture resets consecutive_sixes to 0 even when rolled 6
    lud.turn_idx = 0
    lud.turn_player_id = "p1"
    lud.subphase = "move"
    lud.dice_value = 6
    lud.consecutive_sixes = 2
    lud.tokens["p1"] = [2, -1, -1, -1]  # rel 2 + 6 = rel 8 -> track 8? Wait: track 8 is SAFE!
    # Use rel 3 + 6 = rel 9 -> track 9 (not safe). p2 color=2 (offset 26) -> rel 35 = (26+35)%52 = 9
    lud.tokens["p1"] = [3, -1, -1, -1]
    lud.tokens["p2"] = [35, -1, -1, -1]
    ok, err = lud.handle_action("p1", "move", {"token": 0})
    assert ok, err
    assert lud.tokens["p2"][0] == -1
    assert lud.consecutive_sixes == 0
    assert lud.turn_player_id == "p1"


