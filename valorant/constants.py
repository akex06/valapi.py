class URLS:
    AUTH_URL = "https://auth.riotgames.com/api/v1/authorization"
    REGION_URL = "https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant"
    VERIFIED_URL = "https://email-verification.riotgames.com/api/v1/account/status"
    ENTITLEMENT_URL = "https://entitlements.auth.riotgames.com/api/token/v1"
    USERINFO_URL = "https://auth.riotgames.com/userinfo"


class API:
    PARTY = "/parties/v1"
    PENALTIES = "/restrictions/v3/penalties"
    CONTENT = "/content-service/v3/content"
    ACCOUNT_XP = "/account-xp/v1/players"
    PERSONALIZATION = "/personalization/v2/players"
    MMR = "/mmr/v1/players"
    LEADERBOARD = "/mmr/v1/leaderboards/affinity/na/queue/competitive/season"
    HISTORY = "/match-history/v1/history"
    MATCHES = "/match-details/v1/matches"
    CONFIG = "/v1/config"
    STORE = "/store/v2/storefront"
    PRICES = "/store/v1/offers"
    WALLET = "/store/v1/wallet"
    OWNED = "/store/v1/entitlements"
    PREGAME_PLAYER = "/pregame/v1/players"
    PREGAME_MATCH = "/pregame/v1/matches"
    CURRENT_GAME_PLAYER = "/core-game/v1/players"
    CURRENT_GAME_MATCH = "/core-game/v1/matches"
    ITEM_UPGRADES = "/contract-definitions/v3/item-upgrades"
    CONTRACTS = "/contracts/v1/contracts"
    CHAT = "/pas/v1/service/chat"


class Region:
    def __init__(self, region: str, shard: str) -> None:
        self.region = region
        self.shard = shard


class Regions:
    AsiaPacific = Region("ap", "ap")
    Brasil = Region("br", "na")
    Europe = Region("eu", "eu")
    Korea = Region("kr", "kr")
    LatinAmerica = Region("latam", "na")
    NorthAmerica = Region("na", "na")


regions = {
    "ap": Regions.AsiaPacific,
    "br": Regions.Brasil,
    "eu": Regions.Europe,
    "kr": Regions.Korea,
    "latam": Regions.LatinAmerica,
    "na": Regions.NorthAmerica
}


class Rank:
    image_url = "https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04"

    def __init__(
            self,
            tier: int,
            name: str,
            color: int,
            background_color: int,
            small_icon: str | None,
            large_icon: str | None
    ) -> None:
        self.tier = tier
        self.name = name
        self.color = color
        self.background_color = background_color
        self.small_icon = small_icon
        self.large_icon = large_icon


class Ranks:
    UNRANKED = Rank(0, "UNRANKED", 0xffffffff, 0x00000000,
                    f"{Rank.image_url}/0/smallicon.png",
                    f"{Rank.image_url}/0/largeicon.png")
    UNUSED1 = Rank(1, "Unused1", 0xffffffff, 0x00000000, None, None)
    UNUSED2 = Rank(2, "Unused2", 0xffffffff, 0x00000000, None, None)
    IRON_1 = Rank(3, "IRON 1", 0x4f514fff, 0x828282ff,
                  f"{Rank.image_url}/3/smallicon.png",
                  f"{Rank.image_url}/3/largeicon.png")
    IRON_2 = Rank(4, "IRON 2", 0x4f514fff, 0x828282ff,
                  f"{Rank.image_url}/4/smallicon.png",
                  f"{Rank.image_url}/4/largeicon.png")
    IRON_3 = Rank(5, "IRON 3", 0x4f514fff, 0x828282ff,
                  f"{Rank.image_url}/5/smallicon.png",
                  f"{Rank.image_url}/5/largeicon.png")
    BRONZE_1 = Rank(6, "BRONZE 1", 0xa5855dff, 0x7c5522ff,
                    f"{Rank.image_url}/6/smallicon.png",
                    f"{Rank.image_url}/6/largeicon.png")
    BRONZE_2 = Rank(7, "BRONZE 2", 0xa5855dff, 0x7c5522ff,
                    f"{Rank.image_url}/7/smallicon.png",
                    f"{Rank.image_url}/7/largeicon.png")
    BRONZE_3 = Rank(8, "BRONZE 3", 0xa5855dff, 0x7c5522ff,
                    f"{Rank.image_url}/8/smallicon.png",
                    f"{Rank.image_url}/8/largeicon.png")
    SILVER_1 = Rank(9, "SILVER 1", 0xbbc2c2ff, 0xd1d1d1ff,
                    f"{Rank.image_url}/9/smallicon.png",
                    f"{Rank.image_url}/9/largeicon.png")
    SILVER_2 = Rank(10, "SILVER 2", 0xbbc2c2ff, 0xd1d1d1ff,
                    f"{Rank.image_url}/10/smallicon.png",
                    f"{Rank.image_url}/10/largeicon.png")
    SILVER_3 = Rank(11, "SILVER 3", 0xbbc2c2ff, 0xd1d1d1ff,
                    f"{Rank.image_url}/11/smallicon.png",
                    f"{Rank.image_url}/11/largeicon.png")
    GOLD_1 = Rank(12, "GOLD 1", 0xeccf56ff, 0xeec56aff,
                  f"{Rank.image_url}/12/smallicon.png",
                  f"{Rank.image_url}/12/largeicon.png")
    GOLD_2 = Rank(13, "GOLD 2", 0xeccf56ff, 0xeec56aff,
                  f"{Rank.image_url}/13/smallicon.png",
                  f"{Rank.image_url}/13/largeicon.png")
    GOLD_3 = Rank(14, "GOLD 3", 0xeccf56ff, 0xeec56aff,
                  f"{Rank.image_url}/14/smallicon.png",
                  f"{Rank.image_url}/14/largeicon.png")
    PLATINUM_1 = Rank(15, "PLATINUM 1", 0x59a9b6ff, 0x00c7c0ff,
                      f"{Rank.image_url}/15/smallicon.png",
                      f"{Rank.image_url}/15/largeicon.png")
    PLATINUM_2 = Rank(16, "PLATINUM 2", 0x59a9b6ff, 0x00c7c0ff,
                      f"{Rank.image_url}/16/smallicon.png",
                      f"{Rank.image_url}/16/largeicon.png")
    PLATINUM_3 = Rank(17, "PLATINUM 3", 0x59a9b6ff, 0x00c7c0ff,
                      f"{Rank.image_url}/17/smallicon.png",
                      f"{Rank.image_url}/17/largeicon.png")
    DIAMOND_1 = Rank(18, "DIAMOND 1", 0xb489c4ff, 0x763bafff,
                     f"{Rank.image_url}/18/smallicon.png",
                     f"{Rank.image_url}/18/largeicon.png")
    DIAMOND_2 = Rank(19, "DIAMOND 2", 0xb489c4ff, 0x763bafff,
                     f"{Rank.image_url}/19/smallicon.png",
                     f"{Rank.image_url}/19/largeicon.png")
    DIAMOND_3 = Rank(20, "DIAMOND 3", 0xb489c4ff, 0x763bafff,
                     f"{Rank.image_url}/20/smallicon.png",
                     f"{Rank.image_url}/20/largeicon.png")
    ASCENDANT_1 = Rank(21, "ASCENDANT 1", 0x6ae2afff, 0x1c7245ff,
                       f"{Rank.image_url}/21/smallicon.png",
                       f"{Rank.image_url}/21/largeicon.png")
    ASCENDANT_2 = Rank(22, "ASCENDANT 2", 0x6ae2afff, 0x1c7245ff,
                       f"{Rank.image_url}/22/smallicon.png",
                       f"{Rank.image_url}/22/largeicon.png")
    ASCENDANT_3 = Rank(23, "ASCENDANT 3", 0x6ae2afff, 0x1c7245ff,
                       f"{Rank.image_url}/23/smallicon.png",
                       f"{Rank.image_url}/23/largeicon.png")
    IMMORTAL_1 = Rank(24, "IMMORTAL 1", 0xbb3d65ff, 0xff5551ff,
                      f"{Rank.image_url}/24/smallicon.png",
                      f"{Rank.image_url}/24/largeicon.png")
    IMMORTAL_2 = Rank(25, "IMMORTAL 2", 0xbb3d65ff, 0xff5551ff,
                      f"{Rank.image_url}/25/smallicon.png",
                      f"{Rank.image_url}/25/largeicon.png")
    IMMORTAL_3 = Rank(26, "IMMORTAL 3", 0xbb3d65ff, 0xff5551ff,
                      f"{Rank.image_url}/26/smallicon.png",
                      f"{Rank.image_url}/26/largeicon.png")
    RADIANT = Rank(27, "RADIANT", 0xffffaaff, 0xffedaaff,
                   f"{Rank.image_url}/27/smallicon.png",
                   f"{Rank.image_url}/27/largeicon.png")


ranks: dict[str, Rank] = {
    0: Ranks.UNRANKED,
    1: Ranks.UNUSED1,
    2: Ranks.UNUSED2,
    3: Ranks.IRON_1,
    4: Ranks.IRON_2,
    5: Ranks.IRON_3,
    6: Ranks.BRONZE_1,
    7: Ranks.BRONZE_2,
    8: Ranks.BRONZE_3,
    9: Ranks.SILVER_1,
    10: Ranks.SILVER_2,
    11: Ranks.SILVER_3,
    12: Ranks.GOLD_1,
    13: Ranks.GOLD_2,
    14: Ranks.GOLD_3,
    15: Ranks.PLATINUM_1,
    16: Ranks.PLATINUM_2,
    17: Ranks.PLATINUM_3,
    18: Ranks.DIAMOND_1,
    19: Ranks.DIAMOND_2,
    20: Ranks.DIAMOND_3,
    21: Ranks.ASCENDANT_1,
    22: Ranks.ASCENDANT_2,
    23: Ranks.ASCENDANT_3,
    24: Ranks.IMMORTAL_1,
    25: Ranks.IMMORTAL_2,
    26: Ranks.IMMORTAL_3,
    27: Ranks.RADIANT
}

xmpp_regions = {
    "as2": "as2",
    "asia": "jp1",
    "br1": "br1",
    "eu": "ru1",
    "eu3": "eu3",
    "eun1": "eu2",
    "euw1": "eu1",
    "jp1": "jp1",
    "kr1": "kr1",
    "la1": "la1",
    "la2": "la2",
    "na1": "na1",
    "oc1": "oc1",
    "pbe1": "pb1",
    "ru1": "ru1",
    "sea1": "sa1",
    "sea2": "sa2",
    "sea3": "sa3",
    "sea4": "sa4",
    "tr1": "tr1",
    "us": "la1",
    "us-br1": "br1",
    "us-la2": "la2",
    "us2": "us2"
}

xmpp_servers = {
    "as2": "as2.chat.si.riotgames.com",
    "asia": "jp1.chat.si.riotgames.com",
    "br1": "br.chat.si.riotgames.com",
    "eu": "ru1.chat.si.riotgames.com",
    "eu3": "eu3.chat.si.riotgames.com",
    "eun1": "eun1.chat.si.riotgames.com",
    "euw1": "euw1.chat.si.riotgames.com",
    "jp1": "jp1.chat.si.riotgames.com",
    "kr1": "kr1.chat.si.riotgames.com",
    "la1": "la1.chat.si.riotgames.com",
    "la2": "la2.chat.si.riotgames.com",
    "na1": "na2.chat.si.riotgames.com",
    "oc1": "oc1.chat.si.riotgames.com",
    "pbe1": "pbe1.chat.si.riotgames.com",
    "ru1": "ru1.chat.si.riotgames.com",
    "sea1": "sa1.chat.si.riotgames.com",
    "sea2": "sa2.chat.si.riotgames.com",
    "sea3": "sa3.chat.si.riotgames.com",
    "sea4": "sa4.chat.si.riotgames.com",
    "tr1": "tr1.chat.si.riotgames.com",
    "us": "la1.chat.si.riotgames.com",
    "us-br1": "br.chat.si.riotgames.com",
    "us-la2": "la2.chat.si.riotgames.com",
    "us2": "us2.chat.si.riotgames.com"
}
