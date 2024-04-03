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
    "na": Regions.NorthAmerica,
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
    "us2": "us2",
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
    "us2": "us2.chat.si.riotgames.com",
}
