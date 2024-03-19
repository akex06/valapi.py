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
from valostore.classes import Skin, LockFile
from valostore.constants import URLS, API, xmpp_servers, xmpp_regions

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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

        self.username = username
        self.password = password

        self.set_auth_cookies()

        self.lockfile = self.get_lockfile()

        self.access_token, self.id_token = self.get_access_token()
        self.entitlement_token = self.get_entitlement_token()
        self.pas_token = self.get_pas_token()

        self.region = self.get_region()
        self.server = f"https://pd.{self.region}.a.pvp.net"
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

    def get_access_token(self) -> tuple | None:
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

        return response["access_token"], response["id_token"]

    def get_entitlement_token(self) -> str:
        return self.session.post(
            URLS.ENTITLEMENT_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            },
            json={}
        ).json()["entitlements_token"]

    def get_pas_token(self) -> str:
        return self.session.get(
            "https://riot-geo.pas.si.riotgames.com/pas/v1/service/chat",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            }
        ).text

    def get_user_info(self) -> dict:
        return self.session.post(
            URLS.USERINFO_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            },
            json={}
        ).json()

    def get_region(self) -> str:
        return self.session.put(
            "https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            },
            json={
                "id_token": self.id_token
            }
        ).json()["affinities"]["live"]

    def get_content(self) -> dict:
        return self.session.get(
            f"{self.server}{API.CONTENT}",
            headers={
                "X-Riot-ClientPlatform": f"{self.client_platform}",
                "X-Riot-ClientVersion": f"{self.get_client_version()}",
                "X-Riot-Entitlements-JWT": f"{self.entitlement_token}",
                "Authorization": f"Bearer {self.access_token}"
            }
        ).json()

    def get_account_xp(self) -> dict:
        return self.session.get(
            f"{self.server}{API.ACCOUNT_XP}/{self.user_info['sub']}",
            headers={
                "X-Riot-Entitlements-JWT": self.entitlement_token,
                "Authorization": f"Bearer {self.access_token}"
            }
        ).json()

    def get_loadout(self) -> dict:
        return self.session.get(
            f"{self.server}{API.PERSONALIZATION}/{self.user_info['sub']}/playerloadout",
            headers={
                "X-Riot-Entitlements-JWT": self.entitlement_token,
                "Authorization": f"Bearer {self.access_token}"
            }
        ).json()

    def set_loadout(self, loadout: dict) -> None:
        # TODO: Make a class for loadout to make this easier
        self.session.put(
            f"{self.server}{API.PERSONALIZATION}/{self.user_info['sub']}/playerloadout",
            headers={
                "X-Riot-Entitlements-JWT": self.entitlement_token,
                "Authorization": f"Bearer {self.access_token}"
            },
            json=loadout
        )

    def get_player_mmr(self, player_id: str | None = None) -> dict:
        if player_id is None:
            player_id = self.user_info["sub"]

        return self.session.get(
            f"{self.server}{API.MMR}/{player_id}",
            headers={
                "X-Riot-ClientPlatform": self.client_platform,
                "X-Riot-ClientVersion": self.get_client_version(),
                "X-Riot-Entitlements-JWT": self.entitlement_token,
                "Authorization": f"Bearer {self.access_token}"
            }
        ).json()

    def get_match_history(self, player_id: str | None = None, start: int | None = 0, end: int | None = 20):
        # TODO: add queue parameter when ids are known
        if player_id is None:
            player_id = self.user_info["sub"]
        print(f"{self.server}{API.HISTORY}/{player_id}?startIndex={start}&endIndex={end}")
        return self.session.get(
            f"{self.server}{API.HISTORY}/{player_id}?startIndex={start}&endIndex={end}",
            headers={
                "X-Riot-Entitlements-JWT": self.entitlement_token,
                "Authorization": f"Bearer {self.access_token}"
            }
        ).json()

    def get_match_details(self, match_id: str) -> None:
        return self.session.get(
            f"{self.server}{API.MATCHES}/{match_id}",
            json={
                "X-Riot-Entitlements-JWT": self.entitlement_token,
                "Authorization": f"Bearer {self.access_token}"
            }
        ).json()

    def get_store(self) -> dict:
        return requests.get(
            f"{self.server}{API.STORE}{self.user_info['sub']}",
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "X-Riot-Entitlements-JWT": self.entitlement_token,
                "X-Riot-ClientPlatform": self.client_platform,
                "X-Riot-ClientVersion": self.get_client_version(),
                "Content-Type": "application/json"
            }
        ).json()

    def get_prices(self) -> dict:
        return self.session.get(
            f"{self.server}{API.PRICES}",
            headers={
                "X-Riot-Entitlements-JWT": self.entitlement_token,
                "Authorization": f"Bearer {self.access_token}"
            }
        ).json()

    def get_daily_skins(self) -> list[Skin]:
        offers = self.get_store()["SkinsPanelLayout"]["SingleItemStoreOffers"]

        skins: list[Skin] = list()
        for skin in offers:
            price = skin["Cost"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]
            skins.append(Skin.from_level_uuid(skin["OfferID"], price=price))

        return skins

    def get_wallet(self):
        pass

    def start_xmpp_server(self):
        xmpp_region = xmpp_regions[self.region]
        address, port = xmpp_servers[xmpp_region], 5223

        context = ssl.create_default_context()
        with context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=address) as sock:
            sock.connect((address, port))
            print("connected")
            xmlData = [
                f'<?xml version="1.0"?><stream:stream to="{xmpp_region}.pvp.net" version="1.0" xmlns:stream="http://etherx.jabber.org/streams">',
                f'<auth mechanism="X-Riot-RSO-PAS" xmlns="urn:ietf:params:xml:ns:xmpp-sasl"><rso_token>{self.access_token}</rso_token><pas_token>{self.pas_token}</pas_token></auth>',
                f'<?xml version="1.0"?><stream:stream to="{xmpp_region}.pvp.net" version="1.0" xmlns:stream="http://etherx.jabber.org/streams">',
                '<iq id="_xmpp_bind1" type="set"><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"></bind></iq>',
                '<iq id="_xmpp_session1" type="set"><session xmlns="urn:ietf:params:xml:ns:xmpp-session"/></iq>'
            ]

            for m in xmlData:
                sock.sendall(m.encode('utf-8'))
                response = sock.recv(4096)
                print(response.decode('utf-8'))
