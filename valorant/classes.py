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


class Role(
    msgspec.Struct,
    rename={
        "id": "uuid",
        "name": "displayName",
        "description": "description",
        "icon": "displayIcon",
    },
):
    id: str
    name: str
    description: str
    icon: str


class Ability(
    msgspec.Struct,
    rename={
        "slot": "slot",
        "name": "displayName",
        "description": "description",
        "icon": "displayIcon",
    },
):
    slot: str
    name: str
    description: str
    icon: str


class Agent(
    msgspec.Struct,
    rename={
        "id": "uuid",
        "name": "displayName",
        "developer_name": "developerName",
        "tags": "characterTags",
        "display_icon": "displayIcon",
        "portrait": "fullPortrait",
        "kill_portrait": "killfeedPortrait",
        "colors": "backgroundGradientColors",
    },
):
    id: str
    name: str
    description: str
    developer_name: str
    display_icon: str
    portrait: str
    kill_portrait: str
    background: str
    colors: list[str]
    role: str
    abilities: list[Ability]
    tags: list[str] | None = None


class Version(msgspec.Struct):
    # TODO: Learn to pass the contents of valorant-api.com "data" attrib to the struct without converting to json
    manifestId: str
    branch: str
    version: str
    buildVersion: str
    engineVersion: str
    riotClientVersion: str
    riotClientBuild: str
    buildDate: str


class Password(msgspec.Struct):
    change_at: int = msgspec.field(name="cng_at")
    reset: bool
    must_reset: bool


class Account(
    msgspec.Struct, rename={"admin": "adm", "name": "game_name", "tagline": "tag_line"}
):
    type: int
    state: str
    admin: bool = msgspec.field(name="adm")
    name: str
    tagline: str
    created_at: int


class User(
    msgspec.Struct,
    rename={
        "player_id": "sub",
        "is_email_verified": "email_verified",
        "password": "pw",
        "is_phone_number_verified": "phone_number_verified",
        "account": "acct",
    },
):
    country: str
    player_id: str
    is_email_verified: bool
    password: Password
    is_phone_number_verified: bool
    account: Account
    jti: str
    country_at: int | None = None
    ppid: str | None = None
    player_locale: str | None = None


class Progress(msgspec.Struct, rename={"level": "Level", "xp": "XP"}):
    level: int
    xp: int


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


class Gun(
    msgspec.Struct,
    rename={
        "id": "Subject",
        "charm_instance_id": "CharmInstanceID",
        "charm_id": "CharmID",
        "charm_level_id": "CharmLevelID",
        "skin_id": "SkinID",
        "skin_level_id": "SkinLevelID",
        "chroma_id": "ChromaID",
        "attachments": "attachments",
    },
):
    id: int
    skin_id: str
    skin_level_id: str
    chroma_id: str
    attachments: list[str]
    charm_instance_id: str | None = None
    charm_id: str | None = None
    charm_level_id: str | None = None


class Spray(
    msgspec.Struct,
    rename={"slot": "EquipSlotID", "spray_id": "SprayID"},
):
    slot: str
    spray_id: str


class Identity(
    msgspec.Struct,
    rename={
        "player_card_id": "PlayerCardID",
        "player_title_id": "PlayerTitleID",
        "level": "AccountLevel",
        "level_border": "PreferredLevelBorderID",
        "hide_level": "HideAccountLevel",
    },
):
    player_card_id: str
    player_title_id: str
    level: int
    level_border: str
    hide_level: bool


class Loadout(
    msgspec.Struct,
    rename={
        "player_id": "Subject",
        "version": "Version",
        "guns": "Guns",
        "sprays": "Sprays",
        "identity": "Identity",
        "incognito": "Incognito",
    },
):
    player_id: str
    version: int
    guns: list[Gun]
    sprays: list[Spray]
    identity: Identity
    incognito: bool


class MatchInfo(
    msgspec.Struct,
    rename={
        "id": "matchId",
        "map_id": "mapId",
        "game_pod_id": "gamePodId",
        "game_loop_zone": "gameLoopZone",
        "server": "gameServerAddress",
        "version": "gameVersion",
        "duration": "gameLengthMillis",
        "game_start_millis": "gameStartMillis",
        "provisioning_flow_id": "provisioningFlowID",
        "has_finished": "isCompleted",
        "custom_game_name": "customGameName",
        "force_post_processing": "forcePostProcessing",
        "queue_id": "queueID",
        "game_mode": "gameMode",
        "is_ranked": "isRanked",
        "is_match_sampled": "isMatchSampled",
        "season_id": "seasonId",
        "completion_state": "completionState",
        "party_penalties": "partyRRPenalties",
        "should_match_disabled_penalties": "shouldMatchDisablePenalties",
    },
):
    id: str
    map_id: str
    game_pod_id: str
    game_loop_zone: str
    server: str
    version: str
    game_start_millis: int
    provisioning_flow_id: Literal["Matchmaking", "CustomGame"]
    has_finished: bool
    custom_game_name: str
    force_post_processing: bool
    queue_id: str
    game_mode: str
    is_ranked: bool
    is_match_sampled: bool
    season_id: str
    completion_state: Literal["Surrendered", "Completed", "VoteDraw", ""]
    party_penalties: dict
    should_match_disabled_penalties: bool
    duration: int | None = None


class AbilityCasts(
    msgspec.Struct,
    rename={
        "grenade": "grenadeCasts",
        "ability1": "ability1Casts",
        "ability2": "ability2Casts",
        "ultimate": "ultimateCasts",
    },
):
    grenade: int
    ability1: int
    ability2: int
    ultimate: int


class PlayerMatchStats(
    msgspec.Struct,
    rename={
        "rounds": "roundsPlayed",
        "playtime_millis": "playtimeMillis",
        "ability_casts": "abilityCasts",
    },
):
    score: int
    rounds: int
    kills: int
    deaths: int
    assists: int
    playtime_millis: int
    ability_casts: AbilityCasts | None = None


class RoundDamage(
    msgspec.Struct, rename={"receiver_id": "receiver", "amount": "damage"}
):
    round: int
    receiver_id: str
    amount: int


class XPModifier(msgspec.Struct, rename={"id": "ID", "multiplier": "Value"}):
    id: str
    multiplier: int


class Behavior(
    msgspec.Struct,
    rename={
        "afk_rounds": "afkRounds",
        "comms_rating_recovery": "commsRatingRecovery",
        "damage_participation_outgoing": "damageParticipationOutgoing",
        "friendly_fire_incoming": "friendlyFireIncoming",
        "friendly_fire_outgoing": "friendlyFireOutgoing",
        "mouse_movement": "mouseMovement",
        "rounds_in_spawn": "stayedInSpawnRounds",
    },
):
    afk_rounds: int
    comms_rating_recovery: int
    damage_participation_outgoing: int
    friendly_fire_incoming: int
    friendly_fire_outgoing: int
    mouse_movement: int
    rounds_in_spawn: int


class Player(
    msgspec.Struct,
    rename={
        "player_id": "subject",
        "name": "gameName",
        "tagline": "tagLine",
        "team": "teamId",
        "party_id": "partyId",
        "character_id": "characterId",
        "stats": "stats",
        "damage": "round_damage",
        "rank": "competitiveTier",
        "is_observer": "isObserver",
        "player_card_id": "playerCard",
        "player_title_id": "playerTitle",
        "border_level": "preferredLevelBorder",
        "level": "accountLevel",
        "play_time": "sessionPlayTimeMinutes",
        "xp_modifications": "xpModifications",
        "behavior": "behaviorFactors",
    },
):
    player_id: str
    name: str
    tagline: str
    team: Literal["Blue", "Red"]
    party_id: str
    character_id: str
    rank: int
    is_observer: bool
    player_card_id: str
    player_title_id: str
    level: int
    # TODO change to timedelta
    behavior: Behavior
    stats: PlayerMatchStats | None = None
    play_time: int | None = None
    damage: list[RoundDamage] | None = None
    border_level: str | Literal[""] = None
    xp_modifications: list[XPModifier] = None


class Coach(msgspec.Struct, rename={"id": "subject", "team": "teamId"}):
    id: str
    team: Literal["blue", "red"]


class Team(
    msgspec.Struct,
    rename={
        "team": "teamId",
        "won": "won",
        "rounds_played": "roundsPlayed",
        "rounds_won": "roundsWon",
        "points": "numPoints",
    },
):
    team: Literal["Blue", "Red"]
    won: bool
    rounds_played: int
    rounds_won: int
    points: int


class Location(msgspec.Struct, rename={"view_radians": "viewRadians"}):
    x: float
    y: float


class PlayerLocation(
    msgspec.Struct,
    rename={
        "player_id": "subject",
        "view_radians": "viewRadians",
        "location": "plantLocation",
    },
):
    player_id: str
    view_radians: float
    location: Location


class FinishingDamage(
    msgspec.Struct,
    rename={
        "type": "damageType",
        "item": "damageItem",
        "is_secondary_fire_mode": "isSecondaryFireMode",
    },
):
    type: Literal["Weapon", "Bomb", "Ability", "Fall", "Melee", "Invalid", ""]
    item: (
        str
        | Literal["Ultimate", "Ability1", "Ability2", "GrenadeAbility", "Primary", ""]
    )
    is_secondary_fire_mode: bool


class PlantPlayerLocation(msgspec.Struct, rename={"player_id": "subject"}):
    player_id: str
    view_radians: float = msgspec.field(name="viewRadians")
    location: Location


class Kill(
    msgspec.Struct,
    rename={
        "game_time": "gameTime",
        "round_time": "roundTime",
        "killer_id": "killer",
        "victim_id": "victim",
        "victim_location": "victimLocation",
        "assistants": "assistants",
        "player_locations": "playerLocations",
        "finishing_damage": "finishingDamage",
    },
):
    game_time: int
    round_time: int
    killer_id: str
    victim_id: str
    victim_location: Location
    assistants: list[str]
    player_locations: list[PlantPlayerLocation]
    finishing_damage: FinishingDamage


class Damage(msgspec.Struct):
    receiver_id: str = msgspec.field(name="receiver")
    damage: int
    legshots: int
    bodyshots: int
    headshots: int


class Economy(
    msgspec.Struct,
    rename={
        "credits": "loadoutValue",
        "weapon_id": "weapon",
        "armor_id": "armor",
    },
):
    credits: int
    weapon_id: str | Literal[""]
    armor_id: str | Literal[""]
    remaining: int
    spent: int


class PlayerStats(
    msgspec.Struct,
    rename={
        "player_id": "subject",
        "afk": "wasAfk",
        "penalized": "wasPenalized",
        "stayed_in_spawn": "stayedInSpawn",
    },
):
    player_id: str
    kills: list[Kill]
    damage: list[Damage]
    score: int
    economy: Economy
    afk: bool
    penalized: bool
    stayed_in_spawn: bool


class Score(msgspec.Struct):
    player_id: str = msgspec.field(name="subject")
    score: int


class Round(
    msgspec.Struct,
    rename={
        "number": "roundNum",
        "result": "roundResult",
        "ceremony": "roundCeremony",
        "who_won": "winningTeam",
        "bomb_planter_id": "bombPlanter",
        "bomb_defuser_id": "bombDefuser",
        "time_since_plant": "plantRoundTime",
        "site": "plantSite",
        "time_until_defuse": "defuseRoundTime",
        "defuse_location": "defuseLocation",
        "player_stats": "playerStats",
        "plant_player_locations": "plantPlayerLocations",
        "defuse_player_locations": "defusePlayerLocations",
        "round_result": "roundResultCode",
    },
):
    number: int
    result: Literal[
        "Eliminated",
        "Bomb detonated",
        "Bomb defused",
        "Surrendered",
        "Round timer expired",
    ]
    ceremony: Literal[
        "CeremonyDefault",
        "CeremonyTeamAce",
        "CeremonyFlawless",
        "CeremonyCloser",
        "CeremonyClutch",
        "CeremonyThrifty",
        "CeremonyAce",
        "",
    ]
    who_won: Literal["Blue", "Red"]
    # TODO change to timedelta
    time_since_plant: int
    site: Literal["A", "B", "C", ""]
    # TODO change to timedelta
    time_until_defuse: int
    defuse_location: Location
    player_stats: list[PlayerStats]
    round_result: Literal["Elimination", "Detonate", "Defuse", "Surrendered", ""]
    defuse_player_locations: list[PlayerLocation] | None = None
    player_economies: list[Economy] | None = None
    player_scores: list[Score] | None = None
    plant_player_locations: list[PlantPlayerLocation] | None = None
    bomb_defuser_id: str | None = None
    bomb_planter_id: str | None = None


class Match(
    msgspec.Struct,
    rename={"info": "matchInfo", "rounds": "roundResults"},
):
    info: MatchInfo
    players: list[Player]
    coaches: list[Coach]
    kills: list[Kill]
    teams: list[Team] | None = None
    rounds: list[Round] | None = None
