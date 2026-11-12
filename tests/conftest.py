"""Shared pytest fixtures isolating persistent leaderboard storage and WebSocket room state."""

from __future__ import annotations

import pytest

import backend.main as main_mod
import backend.room_manager as rm_mod
from backend.room_manager import LeaderboardStore


@pytest.fixture(autouse=True)
def isolate_room_manager_and_leaderboard(tmp_path, monkeypatch):
    """Redirect LeaderboardStore to tmp_path and reset RoomManager state for every test."""
    tmp_lb_path = tmp_path / "leaderboard.json"
    monkeypatch.setattr(rm_mod, "LEADERBOARD_PATH", tmp_lb_path)
    monkeypatch.setattr(main_mod.room_manager, "leaderboard", LeaderboardStore(path=tmp_lb_path))
    main_mod.room_manager.clients.clear()
    main_mod.room_manager.rooms.clear()
    main_mod.room_manager._disconnecting.clear()
    try:
        yield main_mod.room_manager.leaderboard
    finally:
        main_mod.room_manager.clients.clear()
        main_mod.room_manager.rooms.clear()
        main_mod.room_manager._disconnecting.clear()
