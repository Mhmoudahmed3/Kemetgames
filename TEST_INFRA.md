# E2E Test Infra: Blackout Arcade Platform Expansion

## Test Philosophy
- **Opaque-box, requirement-driven**: Tests derive strictly from `ORIGINAL_REQUEST.md` and public API/wire contracts (`BaseGame`, `RoomManager`, WebSocket protocol), exercising the system as an end user and opaque client.
- **Methodology**: Systematic 4-tier testing combining Category-Partition, Boundary Value Analysis (BVA), Pairwise Combinatorial Testing, and Real-World Workload Testing.
- **Zero regression**: Verification preserves the stability of all existing games and platform features.

## Feature Inventory
| # | Feature | Source (requirement) | Tier 1 (Min >=5) | Tier 2 (Min >=5) | Tier 3 (Pairwise) | Tier 4 (Workloads) |
|---|---------|---------------------|:----------------:|:----------------:|:-----------------:|:------------------:|
| 1 | Platform Integration & Session Architecture | ORIGINAL_REQUEST §R1 | 6 | 6 | ✓ | ✓ |
| 2 | Tic-Tac-Toe Module | ORIGINAL_REQUEST §R2 | 6 | 6 | ✓ | ✓ |
| 3 | Rock-Paper-Scissors Module | ORIGINAL_REQUEST §R3 | 6 | 5 | ✓ | ✓ |
| 4 | Connect 4 Module | ORIGINAL_REQUEST §R4 | 6 | 5 | ✓ | ✓ |
| 5 | Playing Cards Module | ORIGINAL_REQUEST §R5 | 6 | 6 | ✓ | ✓ |
| **Total** | | | **30** | **28** | **6** | **5** |

## Test Architecture
- **Test Runner**:
  - Invocation: `python -m pytest tests/test_e2e_platform_suite.py -v` (or `pytest tests/test_e2e_platform_suite.py -v`)
  - Framework: Pytest 9.2+, Starlette `TestClient` for synchronous WebSocket testing (`with client.websocket_connect("/ws/<id>") as ws:`)
  - Pass/Fail semantics: All tests must exit code 0, 0 failures, 0 errors.
- **Directory Layout**:
  - `tests/test_e2e_platform_suite.py`: Primary 4-tier E2E platform test suite.
  - `tests/conftest.py`: Shared test fixtures (isolated room manager, player slot factories, temporary leaderboards).
  - `tests/test_tic_tac_toe.py`: Dedicated Tic-Tac-Toe unit & engine tests.
  - `tests/test_rock_paper_scissors.py`: Dedicated Rock-Paper-Scissors unit & engine tests.
  - `tests/test_connect4_game.py`: Dedicated Connect 4 unit & engine tests.
  - `tests/test_playing_cards_game.py`: Dedicated Playing Cards unit & engine tests.

## Test Case Breakdown by Tier

### Tier 1: Feature Coverage (30 Tests)
- **R1: Platform Integration & Session Architecture**
  1. `test_t1_r1_catalog_registration_15_games`: Verifies all 15 games exist in `GAME_REGISTRY` and `/api/games`.
  2. `test_t1_r1_room_creation_and_join_multiplayer`: Host creates room, guest joins via room code, verifies `ROOM_JOINED` and `ROOM_UPDATE`.
  3. `test_t1_r1_solo_vs_ai_launch`: Solo challenge creates room with bot and transitions immediately to `playing`.
  4. `test_t1_r1_spectator_join_and_action_rejection`: Spectator connects, receives state broadcasts, but cannot submit gameplay actions.
  5. `test_t1_r1_duel_forfeit_on_leave`: Disconnecting/leaving in a 2P duel forfeits match to remaining player.
  6. `test_t1_r1_rematch_reset_and_to_lobby`: Rematch resets phase and scores, supports immediate restart or return to lobby.
- **R2: Tic-Tac-Toe**
  7. `test_t1_r2_tictactoe_classic_3x3_win_and_draw`: Standard 3x3 win line detection (horizontal, vertical, diagonal) and full-board draw.
  8. `test_t1_r2_tictactoe_misere_mode_win_condition`: Completing 3-in-a-row triggers loss for active player; opponent wins.
  9. `test_t1_r2_tictactoe_extended_grids_4x4_and_5x5`: 4x4 and 5x5 grids require 4-in-a-row to win.
  10. `test_t1_r2_tictactoe_ultimate_routing_and_macro_win`: Opponent's cell routes next sub-board; winning 3 sub-boards wins macro game.
  11. `test_t1_r2_tictactoe_ultimate_free_placement_fallback`: If target sub-board is won or full, player can place in any open sub-board.
  12. `test_t1_r2_tictactoe_ai_minimax_unbeatable`: Minimax AI vs opponent across iterations never loses (win or draw).
- **R3: Rock-Paper-Scissors**
  13. `test_t1_r3_rps_classic_3_choice_rules`: All 9 outcomes of Rock/Paper/Scissors evaluate to canonical win/loss/tie.
  14. `test_t1_r3_rps_lizard_spock_5_choice_rules`: All 25 outcomes of 5-choice variant evaluate correctly.
  15. `test_t1_r3_rps_best_of_3_format`: First player to 2 round wins triggers match victory.
  16. `test_t1_r3_rps_best_of_5_format`: First player to 3 round wins triggers match victory.
  17. `test_t1_r3_rps_endless_streak_mode`: Consecutive wins increment streak; loss resets current streak.
  18. `test_t1_r3_rps_secret_commit_isolation`: Player choice is hidden from public state until both commit.
- **R4: Connect 4**
  19. `test_t1_r4_connect4_classic_drop_and_gravity`: Discs settle into lowest available row in column.
  20. `test_t1_r4_connect4_horizontal_vertical_diagonal_wins`: Tests all 4 win directions.
  21. `test_t1_r4_connect4_pop_out_mechanics`: Popping bottom-row disc removes it and shifts upper discs down by 1 row.
  22. `test_t1_r4_connect4_pop_out_simultaneous_double_win_tie`: Simultaneous double-win resolves to a TIE (draw).
  23. `test_t1_r4_connect4_5_in_a_row_9x7_grid`: 9x7 grid requires 5-in-a-row (4-in-a-row does not win).
  24. `test_t1_r4_connect4_blitz_5s_timer`: Exceeding 5-second turn timer in Blitz mode triggers timeout.
- **R5: Playing Cards**
  25. `test_t1_r5_deck_fisher_yates_integrity`: 52 unique cards, 4 suits x 13 ranks; shuffle preserves complete deck.
  26. `test_t1_r5_blackjack_scoring_and_dealer_rules`: Soft Ace (11) converts to Hard Ace (1) to prevent bust; dealer draws to 17.
  27. `test_t1_r5_blackjack_actions_hit_stand_double_split`: Validates Hit, Stand, Double Down, and Split.
  28. `test_t1_r5_war_battle_and_3_card_tiebreaker`: Higher card takes round; ties trigger 3-card war pile.
  29. `test_t1_r5_memory_concentration_matching_and_timer`: Matching pair keeps cards face-up; mismatches flip back; timer tracks elapsed time.
  30. `test_t1_r5_high_low_streak_and_push_preservation`: Correct guess increments multiplier; equal rank preserves streak (push).

### Tier 2: Boundary & Corner Cases (28 Tests)
- **R1: Platform Boundaries**
  31. `test_t2_r1_bnd_player_count_out_of_bounds`: Rejects `< MIN_PLAYERS` and `> MAX_PLAYERS`.
  32. `test_t2_r1_bnd_unknown_game_type`: `CREATE_ROOM` with invalid game type rejected.
  33. `test_t2_r1_bnd_invalid_room_code`: `JOIN_ROOM` with non-existent code rejected.
  34. `test_t2_r1_bnd_unwhitelisted_settings_pruned`: Forbidden settings keys filtered out.
  35. `test_t2_r1_bnd_oversized_ws_frame`: Frame > 64 KB rejected.
  36. `test_t2_r1_bnd_session_hijacking_rejected`: Duplicate client ID with mismatched secret rejected.
- **R2: Tic-Tac-Toe Boundaries**
  37. `test_t2_r2_bnd_out_of_bounds_cell_coords`: Coordinates `< 0` or `>= grid_size` rejected.
  38. `test_t2_r2_bnd_play_in_occupied_cell`: Placement in marked cell rejected.
  39. `test_t2_r2_bnd_play_out_of_turn`: Non-turn player move rejected.
  40. `test_t2_r2_bnd_action_after_game_finished`: Moves rejected when match finished.
  41. `test_t2_r2_bnd_ultimate_wrong_subboard`: Placement in wrong sub-board rejected when target is active.
  42. `test_t2_r2_bnd_extended_grid_3_in_a_row_not_win`: 3-in-a-row in 4x4 or 5x5 does not trigger win.
- **R3: Rock-Paper-Scissors Boundaries**
  43. `test_t2_r3_bnd_invalid_choice_rejected`: Unrecognized choice rejected.
  44. `test_t2_r3_bnd_double_commit_rejected`: Multiple commits in single round rejected.
  45. `test_t2_r3_bnd_round_tie_does_not_advance_match_score`: Ties in Bo3/Bo5 do not award points.
  46. `test_t2_r3_bnd_choice_rejection_after_round_resolution`: Moves submitted during countdown rejected.
  47. `test_t2_r3_bnd_max_streak_retention`: `max_streak` persists when current streak resets.
- **R4: Connect 4 Boundaries**
  48. `test_t2_r4_bnd_drop_in_full_column_rejected`: Dropping into full column rejected.
  49. `test_t2_r4_bnd_invalid_column_index`: Column `< 0` or `>= cols` rejected.
  50. `test_t2_r4_bnd_pop_opponent_disc_rejected`: Popping opponent's disc rejected.
  51. `test_t2_r4_bnd_pop_empty_column_rejected`: Popping from empty column rejected.
  52. `test_t2_r4_bnd_board_full_draw`: All 42 cells filled without 4-in-a-row declares draw.
- **R5: Playing Cards Boundaries**
  53. `test_t2_r5_bnd_deck_exhaustion`: Drawing from empty deck handled safely.
  54. `test_t2_r5_bnd_blackjack_bust_immediate_loss`: Hand > 21 immediately busts.
  55. `test_t2_r5_bnd_blackjack_split_only_on_matching_rank`: Splitting non-matching cards rejected.
  56. `test_t2_r5_bnd_war_insufficient_cards_for_war`: Player with < 4 cards in War handled safely.
  57. `test_t2_r5_bnd_memory_flip_already_matched_or_active`: Flipping matched card rejected.
  58. `test_t2_r5_bnd_clean_deck_reset_between_rounds`: Reset restores 52 fresh cards and clears hands.

### Tier 3: Cross-Feature Combinations (6 Tests)
| # | Test Name | Features Exercised | Interaction / Rationale |
|---|-----------|-------------------|-------------------------|
| 59 | `test_t3_combo_tictactoe_misere_with_minimax_ai` | Tic-Tac-Toe, AI | Misère inversion evaluated under Minimax decision tree |
| 60 | `test_t3_combo_connect4_pop_out_in_blitz_mode` | Connect 4, Timers | Pop-out action mechanics executed under strict 5s Blitz timer |
| 61 | `test_t3_combo_rps_lizard_spock_in_best_of_5` | RPS, Match Formats | 5-choice cyclic graph scored across multi-round match format |
| 62 | `test_t3_combo_playing_cards_blackjack_split_with_aces` | Blackjack, Deck | Splitting Aces with dynamic Ace soft/hard scoring evaluation |
| 63 | `test_t3_combo_ultimate_tictactoe_opponent_win_redirection` | Ultimate TTT, Routing | Move directed to completed sub-board invokes free placement fallback |
| 64 | `test_t3_combo_playing_cards_war_chained_double_war` | War, Deck | Consecutive rank ties trigger chained 3-card war piles |

### Tier 4: Real-World Application Scenarios (5 Tests)
| # | Scenario | Features Exercised | Complexity | Description |
|---|----------|--------------------|------------|-------------|
| 65 | `test_t4_scenario_full_connect4_match_with_rematch` | Connect 4, RoomManager, Rematch | High | 2 WebSocket clients play Connect 4 to victory, request rematch, and reset for game 2 |
| 66 | `test_t4_scenario_tictactoe_duel_disconnect_forfeit` | Tic-Tac-Toe, Duel Forfeit, WS | Medium | 2 WebSocket clients play Tic-Tac-Toe; rival disconnects, triggering duel forfeit win |
| 67 | `test_t4_scenario_rps_secret_commit_and_reveal_flow` | RPS, Secret Commit, Countdown | Medium | 2 WebSocket clients play Bo3 RPS with simultaneous secret commits and round resolution |
| 68 | `test_t4_scenario_playing_cards_blackjack_multiplayer_or_solo` | Blackjack, Dealer Rules, Leaderboard | High | Full Blackjack shoe with hits, stands, and dealer resolution with leaderboard entry |
| 69 | `test_t4_scenario_memory_concentration_complete_game` | Memory, Move Tracker, Timer, Game Over | Medium | Complete Memory game playthrough verifying move counter, timer, and `GAME_OVER` event |

## Coverage Thresholds
- Tier 1: ≥5 per feature (Total: 30)
- Tier 2: ≥5 per feature (Total: 28)
- Tier 3: Pairwise coverage of major feature interactions (Total: 6)
- Tier 4: ≥5 realistic application scenarios (Total: 5)
- **Suite Total**: 69 test cases
