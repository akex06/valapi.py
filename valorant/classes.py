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
    # TODO: Learn to pass the contents of valorant-api.com data to the struct without converting to json
    # manifest_id: str = msgspec.field(name="manifestId")
    # branch: str = msgspec.field(name="branch")
    # version: str = msgspec.field(name="version")
    # build_version: str = msgspec.field(name="buildVersion")
    # engine_version: str = msgspec.field(name="engineVersion")
    # riot_client_version: str = msgspec.field(name="riotClientVersion")
    # riot_client_build: str = msgspec.field(name="riotClientBuild")
    # build_date: str = msgspec.field(name="buildDate")

    manifestId: str = msgspec.field(name="manifestId")
    branch: str = msgspec.field(name="branch")
    version: str = msgspec.field(name="version")
    buildVersion: str = msgspec.field(name="buildVersion")
    engineVersion: str = msgspec.field(name="engineVersion")
    riotClientVersion: str = msgspec.field(name="riotClientVersion")
    riotClientBuild: str = msgspec.field(name="riotClientBuild")
    buildDate: str = msgspec.field(name="buildDate")


class Password(msgspec.Struct):
    change_at: int = msgspec.field(name="cng_at")
    reset: bool = msgspec.field(name="reset")
    must_reset: bool = msgspec.field(name="must_reset")


class Account(msgspec.Struct):
    type: int = msgspec.field(name="type")
    state: str = msgspec.field(name="state")
    admin: bool = msgspec.field(name="adm")
    name: str = msgspec.field(name="game_name")
    tagline: str = msgspec.field(name="tag_line")
    created_at: int = msgspec.field(name="created_at")


class User(msgspec.Struct):
    country: str = msgspec.field(name="country")
    player_id: str = msgspec.field(name="sub")
    is_email_verified: bool = msgspec.field(name="email_verified")
    country_at: int | None = msgspec.field(name="country_at")
    password: Password = msgspec.field(name="pw")
    is_phone_number_verified: bool = msgspec.field(name="phone_number_verified")
    ppid: str | None = msgspec.field(name="ppid")
    player_locale: str | None = msgspec.field(name="player_locale")
    account: Account = msgspec.field(name="acct")
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


class MatchInfo(msgspec.Struct):
    id: str = msgspec.field(name="matchId")
    map_id: str = msgspec.field(name="mapId")
    game_pod_id: str = msgspec.field(name="gamePodId")
    game_loop_zone: str = msgspec.field(name="gameLoopZone")
    server: str = msgspec.field(name="gameServerAddress")
    version: str = msgspec.field(name="gameVersion")
    duration: int | None = msgspec.field(name="gameLengthMillis")
    game_start_millis: str = msgspec.field(name="gameStartMillis")
    provisioning_flow_id: Literal["Matchmaking", "CustomGame"] = msgspec.field(
        name="provisioningFlowID"
    )
    has_finished: bool = msgspec.field(name="isCompleted")
    custom_game_name: str = msgspec.field(name="customGameName")
    force_post_processing: bool = msgspec.field(name="forcePostProcessing")
    queue_id: str = msgspec.field(name="queueID")
    game_mode: str = msgspec.field(name="gameMode")
    is_ranked: bool = msgspec.field(name="isRanked")
    is_match_sampled: bool = msgspec.field(name="isMatchSampled")
    season_id: str = msgspec.field(name="seasonId")
    completion_state: Literal["Surrendered", "Completed", "VoteDraw", ""] = (
        msgspec.field(name="completionState")
    )
    party_penalties: dict = msgspec.field(name="partyRRPenalties")
    should_match_disabled_penalties: bool = msgspec.field(
        name="shouldMatchDisablePenalties"
    )


class AbilityCasts(msgspec.Struct):
    grenade: int = msgspec.field(name="grenadeCasts")
    ability1: int = msgspec.field(name="ability1Casts")
    ability2: int = msgspec.field(name="ability2Casts")
    ultimate: int = msgspec.field(name="ultimateCasts")


class PlayerStats(msgspec.Struct):
    score: int = msgspec.field(name="score")
    roundsPlayed: int = msgspec.field(name="roundsPlayed")
    kills: int = msgspec.field(name="kills")
    deaths: int = msgspec.field(name="deaths")
    assists: int = msgspec.field(name="assists")
    playtimeMillis: int = msgspec.field(name="playtimeMillis")
    ability_casts: tuple[AbilityCasts] | None = msgspec.field(name="abilityCasts")


class RoundDamage(msgspec.Struct):
    round: int = msgspec.field(name="round")
    receiver_id: str = msgspec.field(name="receiver")
    amount: int = msgspec.field(name="damage")


class Player(msgspec.Struct):
    player_id: str = msgspec.field(name="subject")
    name: str = msgspec.field(name="gameName")
    tagline: str = msgspec.field(name="tagLine")
    team: Literal["Blue", "Red"] = msgspec.field(name="teamId")
    party_id: str = msgspec.field(name="partyId")
    character_id: str = msgspec.field(name="characterId")
    stats: PlayerStats = msgspec.field(name="stats")


class Match(msgspec.Struct):
    history: MatchInfo = msgspec.field(name="matchInfo")
    players: list[Player] = msgspec.field(name="matchInfo")
    coaches: list[Coach] = msgspec.field(name="matchInfo")
    teams: list[Team] | None = msgspec.field(name="matchInfo")
    rounds: list[Round] | None = msgspec.field(name="matchInfo")
    kills: list[Kill] = msgspec.field(name="matchInfo")
