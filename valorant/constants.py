from valorant.classes import Regions, Agent


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


regions = {
    "ap": Regions.AsiaPacific,
    "br": Regions.Brasil,
    "eu": Regions.Europe,
    "kr": Regions.Korea,
    "latam": Regions.LatinAmerica,
    "na": Regions.NorthAmerica
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


class Agents:
    Gekko = Agent.from_uuid("e370fa57-4757-3604-3648-499e1f642d3f")
    Fade = Agent.from_uuid("dade69b4-4f5a-8528-247b-219e5a1facd6")
    Breach = Agent.from_uuid("5f8d3a7f-467b-97f3-062c-13acf203c006")
    Deadlock = Agent.from_uuid("cc8b64c8-4b25-4ff9-6e7f-37b4da43d235")
    Raze = Agent.from_uuid("f94c3b30-42be-e959-889c-5aa313dba261")
    Chamber = Agent.from_uuid("22697a3d-45bf-8dd7-4fec-84a9e28c69d7")
    KAYO = Agent.from_uuid("601dbbe7-43ce-be57-2a40-4abd24953621")
    Skye = Agent.from_uuid("6f2a04ca-43e0-be17-7f36-b3908627744d")
    Cypher = Agent.from_uuid("117ed9e3-49f3-6512-3ccf-0cada7e3823b")
    Sova = Agent.from_uuid("320b2a48-4d9b-a075-30f1-1f93a9b638fa")
    Killjoy = Agent.from_uuid("1e58de9c-4950-5125-93e9-a0aee9f98746")
    Harbor = Agent.from_uuid("95b78ed7-4637-86d9-7e41-71ba8c293152")
    Viper = Agent.from_uuid("707eab51-4836-f488-046a-cda6bf494859")
    Phoenix = Agent.from_uuid("eb93336a-449b-9c1b-0a54-a891f7921d69")
    Astra = Agent.from_uuid("41fb69c1-4189-7b37-f117-bcaf1e96f1bf")
    Brimstone = Agent.from_uuid("9f0d8ba9-4140-b941-57d3-a7ad57c6b417")
    Iso = Agent.from_uuid("0e38b510-41a8-5780-5e8f-568b2a4f2d6c")
    Neon = Agent.from_uuid("bb2a4828-46eb-8cd1-e765-15848195d751")
    Yoru = Agent.from_uuid("7f94d92c-4234-0a36-9646-3a87eb8b5c89")
    Sage = Agent.from_uuid("569fdd95-4d10-43ab-ca70-79becc718b46")
    Reyna = Agent.from_uuid("a3bfb853-43b2-7238-a4f1-ad90e9e46bcc")
    Omen = Agent.from_uuid("8e253930-4c05-31dd-1b6c-968525494517")
    Jett = Agent.from_uuid("add6443a-41bd-e414-f6ad-e58d267f4e95")
