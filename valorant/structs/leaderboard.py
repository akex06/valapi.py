import msgspec


class LeaderBoardPlayer(msgspec.Struct, rename="camel"):
    player_id: str
    name: str
    tagline: str
    player_card_id: str
    title_id: str
    is_banned: bool
    is_anonymized: bool
    leaderboard_rank: int
    ranked_rating: int
    wins: int
    rank: int


class LeaderBoard(msgspec.Struct, rename="camel"):
    deployment: str
    queue: str
    season_id: str
    players: list[LeaderBoardPlayer]
    total_players: int
    immortal_starting_page: int
    immortal_starting_index: int
    top_tier_rr_threshold: int
    tier_details: list[dict]
    start_index: int
    query: str
