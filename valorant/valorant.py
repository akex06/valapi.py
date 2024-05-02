"""
Classes and methods related to Valorant API calls
"""

import base64
import json

import httpx
import msgspec.json
import requests

from valorant.auth import Auth
from valorant.constants import URLS, API, Region, regions

from valorant.structs import (
    Auth,
    AccountXP,
    LeaderBoard,
    Loadout,
    MatchDetails,
    HistoryMatch,
    HistoryMatchResponse,
    Version,
    User
)


class Valorant:
    def __init__(self, username: str, password: str) -> None:
        self.client = httpx.AsyncClient()
        self.auth = Auth(self.client, username, password)

        build = requests.get("https://valorant-api.com/v1/version").json()["data"][
            "riotClientBuild"
        ]
        self.client.headers.update(
            {
                "User-Agent": f"RiotClient/{build} riot-status (Windows;10;;Professional, x64)",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "application/json, text/plain, */*",
            }
        )

        self.__region = None
        self.__user = None

    async def start(self) -> None:
        await self.auth.set_auth_cookies()

    async def get_pd_server(self) -> str:
        region = await self.get_region()
        return f"https://pd.{region.region}.a.pvp.net"

    async def get_glz_server(self) -> str:
        region = await self.get_region()
        return f"https://glz-{region.region}-1.{region.shard}.a.pvp.net"

    @property
    def client_platform(self) -> bytes:
        return base64.b64encode(
            json.dumps(
                {
                    "platformType": "PC",
                    "platformOS": "Windows",
                    "platformOSVersion": "10.0.19042.1.256.64bit",
                    "platformChipset": "Unknown",
                }
            ).encode("utf-8")
        )

    @property
    def client_version(self) -> Version:
        version = requests.get(
            "https://valorant-api.com/v1/version", timeout=30
        ).json()["data"]

        return Version(**version)

    async def get_user(self) -> User:
        if self.__user is not None:
            return self.__user
        user_info = await self.client.post(
            URLS.USERINFO_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
            json={},
        )
        user = msgspec.json.decode(user_info.content, type=User)
        self.__user = user
        return user

    async def get_region(self) -> Region:
        if self.__region is not None:
            return self.__region

        region = await self.client.put(
            "https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
            json={"id_token": await self.auth.get_id_token()},
        )
        region = regions[region.json()["affinities"]["live"]]
        self.__region = region
        return region

    async def get_content(self) -> dict:
        content = await self.client.get(
            f"{await self.get_pd_server()}{API.CONTENT}",
            headers={
                "X-Riot-ClientPlatform": f"{self.client_platform}",
                "X-Riot-ClientVersion": f"{self.client_version.riotClientVersion}",
                "X-Riot-Entitlements-JWT": f"{await self.auth.get_entitlement_token()}",
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )
        return content.json()

    async def get_account_xp(self) -> AccountXP:
        account_xp = await self.client.get(
            f"{await self.get_pd_server()}{API.ACCOUNT_XP}/{(await self.get_user()).player_id}",
            headers={
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )

        return msgspec.json.decode(account_xp.content, type=AccountXP)

    async def get_loadout(self) -> Loadout:
        loadout = await self.client.get(
            f"{await self.get_pd_server()}{API.PERSONALIZATION}/{(await self.get_user()).player_id}/playerloadout",
            headers={
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )
        return msgspec.json.decode(loadout.content, type=Loadout)

    async def set_loadout(self, loadout: Loadout) -> None:
        await self.client.put(
            f"{await self.get_pd_server()}{API.PERSONALIZATION}/{(await self.get_user()).player_id}/playerloadout",
            headers={
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
            json=msgspec.json.encode(loadout),
        )

    async def get_player_mmr(self, player_id: str | None = None) -> dict:
        if player_id is None:
            player_id = (await self.get_user()).player_id

        player_mmr = await self.client.get(
            f"{await self.get_pd_server()}{API.MMR}/{player_id}",
            headers={
                "X-Riot-ClientPlatform": self.client_platform,
                "X-Riot-ClientVersion": self.client_version.riotClientVersion,
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )
        return player_mmr.json()

    async def get_match_history(
        self,
        player_id: str | None = None,
        offset: int | None = 0,
        amount: int | None = 20,
    ) -> list[HistoryMatch]:
        # TODO: add queue parameter when ids are known
        if player_id is None:
            player_id = (await self.get_user()).player_id

        history = await self.client.get(
            f"{await self.get_pd_server()}{API.HISTORY}/{player_id}?startIndex={offset}&endIndex={amount}",
            headers={
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )
        # TODO make this return a list of MatchHistory
        return msgspec.json.decode(history.content, type=HistoryMatchResponse).History

    async def get_match_details(self, match_id: str) -> MatchDetails:
        match = await self.client.get(
            f"{await self.get_pd_server()}{API.MATCHES}/{match_id}",
            headers={
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )
        return msgspec.json.decode(match.content, type=MatchDetails)

    async def get_leaderboard(
        self,
        season_id: str,
        start: int = 0,
        amount: int = 510,
        username: str | None = None,
    ) -> LeaderBoard:
        leaderboard = await self.client.get(
            (
                f"{await self.get_pd_server()}{API.LEADERBOARD}/{season_id}?startIndex={start}&size={amount}"
                + f"&query={username}"
                if username
                else ""
            ),
            headers={
                "X-Riot-ClientVersion": self.client_version.riotClientVersion,
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )
        return msgspec.json.decode(leaderboard.content, type=LeaderBoard)

    async def get_penalties(self) -> dict:
        penalties = await self.client.get(
            f"{await self.get_pd_server()}{API.PENALTIES}",
            headers={
                "X-Riot-ClientPlatform": self.client_platform,
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )
        return penalties.json()

    async def get_config(self) -> dict:
        region = await self.get_region()
        config = await self.client.get(
            f"{await self.get_pd_server()}{API.CONFIG}/{region.region}",
            headers={
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )
        return config.json()

    async def get_prices(self) -> dict:
        prices = await self.client.get(
            f"{await self.get_pd_server()}{API.PRICES}",
            headers={
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )

        return prices.json()

    async def get_store(self) -> dict:
        store = await self.client.get(
            f"{await self.get_pd_server()}{API.STORE}/{(await self.get_user()).player_id}",
            headers={
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "X-Riot-ClientPlatform": self.client_platform,
                "X-Riot-ClientVersion": self.client_version.riotClientVersion,
                "Content-Type": "application/json",
            },
        )

        return store.json()

    async def get_wallet(self) -> dict:
        wallet = await self.client.get(
            f"{await self.get_pd_server()}{API.WALLET}/{(await self.get_user()).player_id}",
            headers={
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )
        return wallet.json()

    async def get_items(self, item_type: str) -> dict:
        items = await self.client.get(
            f"{await self.get_pd_server()}{API.OWNED}/{(await self.get_user()).player_id}/{item_type}",
            headers={
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )
        return items.json()

    async def get_pregame_id(self, player_id: str | None = None) -> dict:
        if player_id is None:
            player_id = (await self.get_user()).player_id

        pregame = await self.client.get(
            f"{await self.get_glz_server()}{API.PREGAME_PLAYER}/{player_id}",
            headers={
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )

        return pregame.json()

    async def get_pregame_match(self, pregame_match_id: str | None = None) -> dict:
        if pregame_match_id is None:
            pregame_match_id = (await self.get_pregame_id())["MatchID"]

        pregame_match = await self.client.get(
            f"{await self.get_glz_server()}{API.PREGAME_MATCH}/{pregame_match_id}",
            headers={
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )
        return pregame_match.json()

    async def get_pregame_loadout(self, pregame_match_id: str | None = None) -> dict:
        if pregame_match_id is None:
            pregame_match_id = (await self.get_pregame_id())["MatchID"]

        pregame_loadout = await self.client.get(
            f"{await self.get_glz_server()}{API.PREGAME_MATCH}/{pregame_match_id}/loadouts",
            headers={
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )
        return pregame_loadout.json()

    async def select_agent(
        self, agent_id: str, pregame_match_id: str | None = None
    ) -> dict:
        if pregame_match_id is None:
            pregame_match_id = self.get_pregame_id()

        agent_select = await self.client.post(
            f"{await self.get_glz_server()}{API.MATCHES}/{pregame_match_id}/select/{agent_id}",
            headers={
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )
        return agent_select.json()

    async def lock_agent(
        self, agent_id: str, pregame_match_id: str | None = None
    ) -> dict:
        if pregame_match_id is None:
            pregame_match_id = self.get_pregame_id()

        agent_lock = await self.client.post(
            f"{await self.get_glz_server()}{API.MATCHES}/{pregame_match_id}/lock/{agent_id}",
            headers={
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )
        return agent_lock.json()

    async def quit_pregame(self, pregame_match_id: str | None = None) -> dict:
        if pregame_match_id is None:
            pregame_match_id = self.get_pregame_id()

        pregame_quit = await self.client.post(
            f"{await self.get_glz_server()}{API.MATCHES}/{pregame_match_id}/quit",
            headers={
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )
        return pregame_quit.json()

    async def get_current_game_player(self, player_id: str | None = None) -> dict:
        if player_id is None:
            player_id = (await self.get_user()).player_id

        current_game_player = await self.client.get(
            f"{await self.get_glz_server()}{API.CURRENT_GAME_PLAYER}/{player_id}",
            headers={
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )
        return current_game_player.links

    async def get_current_game_match(self, current_match_id: str | None = None) -> dict:
        if current_match_id is None:
            current_match_id = (await self.get_pregame_id())["MatchID"]

        current_game_match = await self.client.get(
            f"{await self.get_glz_server()}{API.CURRENT_GAME_MATCH}/{current_match_id}",
            headers={
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )
        return current_game_match.json()

    async def get_current_game_loadout(
        self, current_match_id: str | None = None
    ) -> dict:
        if current_match_id is None:
            current_match_id = (await self.get_pregame_id())["MatchID"]

        current_game_loadout = await self.client.get(
            f"{await self.get_glz_server()}{API.CURRENT_GAME_MATCH}/{current_match_id}/loadouts",
            headers={
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )
        return current_game_loadout.json()

    async def get_item_upgrades(self) -> dict:
        item_upgrades = await self.client.get(
            f"{await self.get_pd_server()}{API.ITEM_UPGRADES}",
            headers={
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )

        return item_upgrades.json()

    async def get_contracts(self, player_id: str | None = None) -> dict:
        if player_id is None:
            player_id = (await self.get_user()).player_id

        contracts = await self.client.get(
            f"{await self.get_pd_server()}{API.CONTRACTS}/{player_id}",
            headers={
                "X-Riot-ClientVersion": self.client_version.riotClientVersion,
                "X-Riot-Entitlements-JWT": await self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {await self.auth.get_access_token()}",
            },
        )
        return contracts.json()
