"""
Classes and methods related to Valorant API calls
"""
import base64
import json
import socket
import ssl

import requests
import urllib3

from valostore import Cache
from valostore.classes import Skin, LockFile, Region
from valostore.constants import URLS, API, xmpp_servers, xmpp_regions, regions

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Auth:
    def __init__(self, username: str, password: str, session: requests.Session) -> None:
        self.username = username
        self.password = password
        self.session = session

        self.__access_token = None
        self.__id_token = None
        self.__entitlement_token = None
        self.__pas_token = None

    def get_access_token(self) -> tuple | None:
        if self.__access_token is not None:
            return self.__access_token

        put_data = {
            "language": "en_US",
            "password": self.password,
            "remember": "true",
            "type": "auth",
            "username": self.username
        }
        request = self.session.put(url=URLS.AUTH_URL, json=put_data).json()

        if request["type"] == "multifactor":
            raise ValueError("Multifactor needed, please disable it and try again")

        response = dict(map(
            lambda x: x.split("="),
            request["response"]["parameters"]["uri"].split("#")[1].split("&")
        ))  # weird shit, extracts anchors from url and transforms them into a dict

        self.__access_token, self.__id_token = response["access_token"], response["id_token"]
        return self.__access_token

    def get_id_token(self) -> str:
        if self.__id_token is not None:
            return self.__id_token

        self.__access_token, self.__id_token = self.get_access_token()
        return self.__id_token

    def get_entitlement_token(self) -> str:
        if self.__entitlement_token is not None:
            return self.__entitlement_token

        self.__entitlement_token = self.session.post(
            URLS.ENTITLEMENT_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.get_access_token()}"
            },
            json={}
        ).json()["entitlements_token"]

        return self.__entitlement_token

    def get_pas_token(self) -> str:
        if self.__pas_token is not None:
            return self.__pas_token

        self.__pas_token = self.session.get(
            "https://riot-geo.pas.si.riotgames.com/pas/v1/service/chat",
            headers={
                "Authorization": f"Bearer {self.get_access_token()}"
            }
        ).text
        return self.__pas_token


class Valorant:
    def __init__(self, username: str, password: str) -> None:
        self.cache = Cache()
        self.session = requests.Session()

        build = requests.get("https://valorant-api.com/v1/version").json()["data"]["riotClientBuild"]
        self.session.headers = {
            "User-Agent": f"RiotClient/{build} riot-status (Windows;10;;Professional, x64)",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "application/json, text/plain, */*"
        }

        self.client_platform = base64.b64encode(json.dumps({
            "platformType": "PC",
            "platformOS": "Windows",
            "platformOSVersion": "10.0.19042.1.256.64bit",
            "platformChipset": "Unknown"
        }).encode("utf-8"))
        self.set_auth_cookies()

        self.auth = Auth(username, password, self.session)

        self.region = self.get_region()
        self.pd_server = f"https://pd.{self.region.region}.a.pvp.net"
        self.glz_server = f"https://glz-{self.region.region}-1.{self.region.shard}.a.pvp.net"
        self.user_info = self.get_user_info()

    def get_client_version(self) -> str:
        return requests.get(
            "https://valorant-api.com/v1/version",
            timeout=30
        ).json()["data"]["riotClientVersion"]

    def get_lockfile(self) -> LockFile:
        return LockFile()

    def set_auth_cookies(self) -> None:
        post_data = {
            "acr_values": "urn:riot:bronze",
            "claims": "",
            "client_id": "riot-client",
            "nonce": "oYnVwCSrlS5IHKh7iI16oQ",
            "redirect_uri": "http://localhost/redirect",
            "response_type": "token id_token",
            "scope": "openid link ban lol_region"
        }
        self.session.post(url=URLS.AUTH_URL, json=post_data)

    def get_user_info(self) -> dict:
        return self.session.post(
            URLS.USERINFO_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            },
            json={}
        ).json()

    def get_region(self) -> Region:
        a = self.session.put(
            "https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            },
            json={
                "id_token": self.auth.get_id_token()
            }
        ).json()
        return regions[a["affinities"]["live"]]

    def get_content(self) -> dict:
        return self.session.get(
            f"{self.pd_server}{API.CONTENT}",
            headers={
                "X-Riot-ClientPlatform": f"{self.client_platform}",
                "X-Riot-ClientVersion": f"{self.get_client_version()}",
                "X-Riot-Entitlements-JWT": f"{self.auth.get_entitlement_token()}",
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def get_account_xp(self) -> dict:
        return self.session.get(
            f"{self.pd_server}{API.ACCOUNT_XP}/{self.user_info['sub']}",
            headers={
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def get_loadout(self) -> dict:
        return self.session.get(
            f"{self.pd_server}{API.PERSONALIZATION}/{self.user_info['sub']}/playerloadout",
            headers={
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def set_loadout(self, loadout: dict) -> None:
        # TODO: Make a class for loadout to make this easier
        self.session.put(
            f"{self.pd_server}{API.PERSONALIZATION}/{self.user_info['sub']}/playerloadout",
            headers={
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            },
            json=loadout
        )

    def get_player_mmr(self, player_id: str | None = None) -> dict:
        if player_id is None:
            player_id = self.user_info["sub"]

        return self.session.get(
            f"{self.pd_server}{API.MMR}/{player_id}",
            headers={
                "X-Riot-ClientPlatform": self.client_platform,
                "X-Riot-ClientVersion": self.get_client_version(),
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def get_match_history(self, player_id: str | None = None, start: int | None = 0, end: int | None = 20) -> dict:
        # TODO: add queue parameter when ids are known
        if player_id is None:
            player_id = self.user_info["sub"]

        return self.session.get(
            f"{self.pd_server}{API.HISTORY}/{player_id}?startIndex={start}&endIndex={end}",
            headers={
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def get_match_details(self, match_id: str) -> dict:
        return self.session.get(
            f"{self.pd_server}{API.MATCHES}/{match_id}",
            headers={
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def get_leaderboard(self, season_id: str, start: int = 0, amount: int = 510, username: str | None = None) -> dict:
        return self.session.get(
            f"{self.pd_server}{API.LEADERBOARD}/{season_id}?startIndex={start}&size={amount}" + f"&query={username}" if username else "",
            headers={
                "X-Riot-ClientVersion": self.get_client_version(),
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def get_penalties(self) -> dict:
        return self.session.get(
            f"{self.pd_server}{API.PENALTIES}",
            headers={
                "X-Riot-ClientPlatform": self.client_platform,
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def get_config(self) -> dict:
        return self.session.get(
            f"{self.pd_server}{API.CONFIG}/{self.region.region}",
            headers={
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def get_prices(self) -> dict:
        return self.session.get(
            f"{self.pd_server}{API.PRICES}",
            headers={
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def get_store(self) -> dict:
        return requests.get(
            f"{self.pd_server}{API.STORE}{self.user_info['sub']}",
            headers={
                "Authorization": f"Bearer {self.auth.get_access_token()}",
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "X-Riot-ClientPlatform": self.client_platform,
                "X-Riot-ClientVersion": self.get_client_version(),
                "Content-Type": "application/json"
            }
        ).json()

    def get_wallet(self) -> dict:
        return self.session.get(
            f"{self.pd_server}{API.WALLET}/{self.user_info['sub']}",
            headers={
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def get_items(self, item_type: str) -> dict:
        return self.session.get(
            f"{self.pd_server}{API.OWNED}/{self.user_info['sub']}/{item_type}",
            headers={
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }

        ).json()

    def get_daily_skins(self) -> list[Skin]:
        offers = self.get_store()["SkinsPanelLayout"]["SingleItemStoreOffers"]

        skins: list[Skin] = list()
        for skin in offers:
            price = skin["Cost"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]
            skins.append(Skin.from_level_uuid(skin["OfferID"], price=price))

        return skins

    def get_pregame_id(self, player_id: str | None = None) -> dict:
        if player_id is None:
            player_id = self.user_info['sub']

        return self.session.get(
            f"{self.glz_server}{API.PREGAME_PLAYER}/{player_id}",
            headers={
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def get_pregame_match(self, pregame_match_id: str | None = None) -> dict:
        if pregame_match_id is None:
            pregame_match_id = self.get_pregame_id()["MatchID"]

        return self.session.get(
            f"{self.glz_server}{API.PREGAME_MATCH}/{pregame_match_id}",
            headers={
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def get_pregame_loadout(self, pregame_match_id: str | None = None) -> dict:
        if pregame_match_id is None:
            pregame_match_id = self.get_pregame_id()["MatchID"]

        return self.session.get(
            f"{self.glz_server}{API.PREGAME_MATCH}/{pregame_match_id}/loadouts",
            headers={
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def select_agent(self, agent_id: str, pregame_match_id: str | None = None) -> dict:
        print("SELECTING AGENT")
        if pregame_match_id is None:
            pregame_match_id = self.get_pregame_id()

        return self.session.post(
            f"{self.glz_server}{API.MATCHES}/{pregame_match_id}/select/{agent_id}",
            headers={
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def lock_agent(self, agent_id: str, pregame_match_id: str | None = None) -> dict:
        if pregame_match_id is None:
            pregame_match_id = self.get_pregame_id()

        return self.session.post(
            f"{self.glz_server}{API.MATCHES}/{pregame_match_id}/lock/{agent_id}",
            headers={
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def quit_pregame(self, pregame_match_id: str | None = None) -> dict:
        if pregame_match_id is None:
            pregame_match_id = self.get_pregame_id()

        return self.session.post(
            f"{self.glz_server}{API.MATCHES}/{pregame_match_id}/quit",
            headers={
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def get_current_game_player(self, player_id: str | None = None) -> dict:
        if player_id is None:
            player_id = self.user_info["sub"]

        return self.session.get(
            f"{self.glz_server}{API.CURRENT_GAME_PLAYER}/{player_id}"
        ).json()

    def get_current_game_match(self, current_match_id: str | None = None) -> dict:
        if current_match_id is None:
            current_match_id = self.get_pregame_id()["MatchID"]

        return self.session.get(
            f"{self.glz_server}{API.CURRENT_GAME_MATCH}/{current_match_id}",
            headers={
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def get_current_game_loadout(self, current_match_id: str | None = None) -> dict:
        if current_match_id is None:
            current_match_id = self.get_pregame_id()["MatchID"]

        return self.session.get(
            f"{self.glz_server}{API.CURRENT_GAME_MATCH}/{current_match_id}/loadouts",
            headers={
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def get_item_upgrades(self) -> dict:
        return self.session.get(
            f"{self.pd_server}{API.ITEM_UPGRADES}",
            headers={
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def get_contracts(self, player_id: str | None = None) -> dict:
        if player_id is None:
            player_id = self.user_info["sub"]

        return self.session.get(
            f"{self.pd_server}{API.CONTRACTS}/{player_id}",
            headers={
                "X-Riot-ClientVersion": self.get_client_version(),
                "X-Riot-Entitlements-JWT": self.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.auth.get_access_token()}"
            }
        ).json()

    def start_xmpp_server(self):
        xmpp_region = xmpp_regions[self.region.region]
        address, port = xmpp_servers[xmpp_region], 5223

        context = ssl.create_default_context()
        with context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=address) as s:
            s.connect((address, port))
            print("connected")
            xmlData = [
                f'<?xml version="1.0"?><stream:stream to="{xmpp_region}.pvp.net" version="1.0" xmlns:stream="http://etherx.jabber.org/streams">',
                f'<auth mechanism="X-Riot-RSO-PAS" xmlns="urn:ietf:params:xml:ns:xmpp-sasl"><rso_token>{self.auth.get_access_token()}</rso_token><pas_token>{self.auth.get_pas_token()}</pas_token></auth>',
                f'<?xml version="1.0"?><stream:stream to="{xmpp_region}.pvp.net" version="1.0" xmlns:stream="http://etherx.jabber.org/streams">',
                '<iq id="_xmpp_bind1" type="set"><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"></bind></iq>',
                '<iq id="_xmpp_session1" type="set"><session xmlns="urn:ietf:params:xml:ns:xmpp-session"/></iq>'
            ]

            for m in xmlData:
                s.sendall(m.encode('utf-8'))
                response = s.recv(4096)
                print(response.decode('utf-8'))
