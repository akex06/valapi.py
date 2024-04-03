import os
from typing import Literal

import msgspec


class LockFile:
    def __init__(self, lockfile_fp: str = None) -> None:
        if lockfile_fp is None:
            lockfile_fp = (
                os.getenv("LOCALAPPDATA")
                + "\\Riot Games\\Riot Client\\Config\\lockfile"
            )

        with open(lockfile_fp, encoding="utf-8") as f:
            self.name, self.pid, self.port, self.password, self.protocol = (
                f.read().split(":")
            )


class Role(msgspec.Struct):
    id: str = msgspec.field(name="uuid")
    name: str = msgspec.field(name="displayName")
    description: str = msgspec.field(name="description")
    icon: str = msgspec.field(name="displayIcon")


class Ability(msgspec.Struct):

    slot: str = msgspec.field(name="slot")
    name: str = msgspec.field(name="displayName")
    description: str = msgspec.field(name="description")
    icon: str = msgspec.field(name="displayIcon")


class Agent(msgspec.Struct):
    id: str = msgspec.field(name="uuid")
    name: str = msgspec.field(name="displayName")
    description: str = msgspec.field(name="description")
    developer_name: str = msgspec.field(name="developerName")
    tags: list[str] | None = msgspec.field(name="characterTags")
    display_icon: str = msgspec.field(name="displayIcon")
    portrait: str = msgspec.field(name="fullPortrait")
    kill_portrait: str = msgspec.field(name="killfeedPortrait")
    background: str = msgspec.field(name="background")
    colors: list[str] = msgspec.field(name="backgroundGradientColors")
    role: str = msgspec.field(name="role")
    abilities: list[Ability] = msgspec.field(name="abilities")


class Version(msgspec.Struct):
    manifest_id: str = msgspec.field(name="manifestId")
    branch: str = msgspec.field(name="branch")
    version: str = msgspec.field(name="version")
    build_version: str = msgspec.field(name="buildVersion")
    engine_version: str = msgspec.field(name="engineVersion")
    riot_client_version: str = msgspec.field(name="riotClientVersion")
    riot_client_build: str = msgspec.field(name="riotClientBuild")
    build_date: str = msgspec.field(name="buildDate")


class User(msgspec.Struct):
    country: str = msgspec.field(name="country")
    player_id: str = msgspec.field(name="sub")
    is_email_verified: str = msgspec.field(name="email_verified")
    player_plocale: str = msgspec.field(name="player_plocale")
    country_at: str = msgspec.field(name="country_at")
    pw: str = msgspec.field(name="pw")
    is_phone_number_verified: str = msgspec.field(name="phone_number_verified")
    ppid: str = msgspec.field(name="ppid")
    player_locale: str = msgspec.field(name="player_locale")
    acct: str = msgspec.field(name="acct")
    jti: str = msgspec.field(name="jti")


class Progress(msgspec.Struct):
    level: int = msgspec.field(name="Level")
    xp: int = msgspec.field(name="XP")


class XPSource(msgspec.Struct):
    id: Literal["time-played", "match-win", "first-win-of-the-day"] = msgspec.field(
        name="ID"
    )
    amount: int = msgspec.field(name="Amount")


class AccountXPMatch(msgspec.Struct):
    start: str = msgspec.field(name="MatchStart")
    start_progress: Progress = msgspec.field(name="StartProgress")
    end_progress: Progress = msgspec.field(name="EndProgress")
    xp_delta: int = msgspec.field(name="XPDelta")
    xp_sources: list[XPSource] = msgspec.field(name="XPSources")
    xp_multipliers: list[str] = msgspec.field(name="XPMultipliers")


class AccountXP(msgspec.Struct):
    version: int = msgspec.field(name="Version")
    player_id: str = msgspec.field(name="Subject")
    progress: Progress = msgspec.field(name="Progress")
    history: list[AccountXPMatch] = msgspec.field(name="History")
    last_time_granted_first_win: str = msgspec.field(name="LastTimeGrantedFirstWin")
    next_time_first_win_available: str = msgspec.field(name="NextTimeFirstWinAvailable")


class Gun(msgspec.Struct):
    id: int = msgspec.field(name="Subject")
    charm_instance_id: str | None = msgspec.field(name="CharmInstanceID")
    charm_id: str | None = msgspec.field(name="CharmID")
    charm_level_id: str | None = msgspec.field(name="CharmLevelID")
    skin_id: str = msgspec.field(name="SkinID")
    skin_level_id: str = msgspec.field(name="SkinLevelID")
    chroma_id: str = msgspec.field(name="ChromaID")
    attachments: list[str] = msgspec.field(name="attachments")


class Spray(msgspec.Struct):
    slot: str = msgspec.field(name="EquipSlotID")
    spray_id: str = msgspec.field(name="SprayID")
    spray_level_id: None = msgspec.field(name="SprayLevelID")


class Identity(msgspec.Struct):
    player_card_id: str = msgspec.field(name="PlayerCardID")
    player_title_id: str = msgspec.field(name="PlayerTitleID")
    level: int = msgspec.field(name="AccountLevel")
    level_border: str = msgspec.field(name="PreferredLevelBorderID")
    hide_level: bool = msgspec.field(name="HideAccountLevel")


class Loadout(msgspec.Struct):
    player_id: str = msgspec.field(name="Subject")
    version: int = msgspec.field(name="Version")
    guns: list[Gun] = msgspec.field(name="Guns")
    sprays: list[Spray] = msgspec.field(name="Sprays")
    identity: Identity = msgspec.field(name="Identity")
    incognito: bool = msgspec.field(name="Incognito")
