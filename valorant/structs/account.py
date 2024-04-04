from typing import Literal

import msgspec


class Progress(msgspec.Struct, rename={"level": "Level", "xp": "XP"}):
    level: int
    xp: int


class Account(
    msgspec.Struct, rename={"admin": "adm", "name": "game_name", "tagline": "tag_line"}
):
    type: int
    state: str
    admin: bool = msgspec.field(name="adm")
    name: str
    tagline: str
    created_at: int


class XPSource(msgspec.Struct, rename={"id": "ID", "amount": "Amount"}):
    id: Literal["time-played", "match-win", "first-win-of-the-day"]
    amount: int


class AccountXPMatch(
    msgspec.Struct,
    rename={
        "start": "MatchStart",
        "start_progress": "StartProgress",
        "end_progress": "EndProgress",
        "xp_delta": "XPDelta",
        "xp_sources": "XPSources",
        "xp_multipliers": "XPMultipliers",
    },
):
    start: str
    start_progress: Progress
    end_progress: Progress
    xp_delta: int
    xp_sources: list[XPSource]
    xp_multipliers: list[str]


class AccountXP(
    msgspec.Struct,
    rename={
        "version": "Version",
        "player_id": "Subject",
        "progress": "Progress",
        "history": "History",
        "last_time_granted_first_win": "LastTimeGrantedFirstWin",
        "next_time_first_win_available": "NextTimeFirstWinAvailable",
    },
):
    version: int
    player_id: str
    progress: Progress
    history: list[AccountXPMatch]
    last_time_granted_first_win: str
    next_time_first_win_available: str
