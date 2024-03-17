"""
Classes and methods related to Valorant API calls
"""
import os.path
import sqlite3

import requests
import urllib3
from requests.auth import HTTPBasicAuth

from src import Cache

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Skin:
    def __init__(self, uuid: str, name: str = None, price: int = None):
        self.uuid = uuid
        self.price = price

        self.name = name or self.get_name()
        self.image = f"https://media.valorant-api.com/weaponskins/{self.uuid}/displayicon.png"

    def __repr__(self) -> str:
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )

    @classmethod
    def from_level_uuid(cls, level_uuid: str, price: int = None):
        conn = sqlite3.connect("src/skins.sqlite3")
        c = conn.cursor()

        skin_info = c.execute(
            """
                SELECT
                    skins.uuid,
                    skins.name
                FROM skins
                WHERE skins.name = (
                    SELECT
                        skinlevels.name
                    FROM skinlevels
                    WHERE skinlevels.uuid = ?)
            """,
            (level_uuid,)
        ).fetchone()
        if skin_info is None:
            raise ValueError("The provided UUID is not valid")

        uuid, name = skin_info
        return cls(uuid, name=name, price=price)

    def get_name(self) -> str | None:
        conn = sqlite3.connect("src/skins.sqlite3")
        c = conn.cursor()

        name = c.execute("SELECT name FROM skins WHERE uuid = ?", (self.uuid,)).fetchone()
        if name is None:
            return None

        return name[0]


class API:
    accountXP = "/account-xp/v1/players/"
    mmr = "/mmr/v1/players/"
    store = "/store/v2/storefront/"
    wallet = "/store/v1/wallet/"
    owned = "/store/v1/entitlements/"
    chat = "/pas/v1/service/chat"


class URLS:
    AUTH_URL = "https://auth.riotgames.com/api/v1/authorization"
    REGION_URL = "https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant"
    VERIFIED_URL = "https://email-verification.riotgames.com/api/v1/account/status"
    ENTITLEMENT_URL = "https://entitlements.auth.riotgames.com/api/token/v1"
    USERINFO_URL = "https://auth.riotgames.com/userinfo"


class LockFile:
    def __init__(self, lockfile_fp: str = None) -> None:
        if lockfile_fp is None:
            lockfile_fp = os.getenv("LOCALAPPDATA") + "\\Riot Games\\Riot Client\\Config\\lockfile"

        with open(lockfile_fp, encoding="utf-8") as f:
            self.name, self.pid, self.port, self.password, self.protocol = f.read().split(":")


class Valorant:
    def __init__(self, username: str, password: str, auth=True) -> None:
        self.cache = Cache()
        self.session = requests.Session()

        build = requests.get("https://valorant-api.com/v1/version").json()["data"]["riotClientBuild"]
        self.session.headers = {
            "User-Agent": f"RiotClient/{build} riot-status (Windows;10;;Professional, x64)",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "application/json, text/plain, */*"
        }

        if auth:
            self.username = username
            self.password = password

            self.lockfile = self.get_lockfile()

            self.access_token, self.id_token = self.get_access_token()
            self.entitlement_token = self.get_entitlement_token()

            self.region = self.get_region()
            self.user_info = self.get_user_info()

            self.rso_token = self.get_rso_token()
            self.pas_token = self.get_pas_token()

        else:
            self.username = None
            self.password = None

            self.lockfile = None

            self.access_token, self.id_token = None, None
            self.entitlement_token = None

            self.region = None
            self.user_info = None

            self.rso_token = None
            self.pas_token = None

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

    def get_lockfile(self) -> LockFile:
        return LockFile()

    def get_access_token(self) -> tuple | None:
        self.set_auth_cookies()

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

    def get_entitlement_token(self):
        return self.session.post(
            URLS.ENTITLEMENT_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            },
            json={}
        ).json()

    def get_user_info(self):
        return self.session.post(
            URLS.USERINFO_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            },
            json={}
        ).json()

    def get_region(self):
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

    def get_store(self):
        server = f"https://pd.{self.region}.a.pvp.net"
        client_version = requests.get(
            "https://valorant-api.com/v1/version",
            timeout=30
        ).json()["data"]["riotClientVersion"]
        client_platform = ("ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmV"
                           "yc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Riot-Entitlements-JWT": self.entitlement_token,
            "X-Riot-ClientPlatform": client_platform,
            "X-Riot-ClientVersion": client_version,
            "Content-Type": "application/json"
        }

        store_api = f"{server}{API.store}{self.user_info['sub']}"
        return requests.get(store_api, headers=headers).json()

    def get_daily_skins(self) -> list[Skin]:
        offers = self.get_store()["SkinsPanelLayout"]["SingleItemStoreOffers"]

        skins: list[Skin] = list()
        for skin in offers:
            price = skin["Cost"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]
            skins.append(Skin.from_level_uuid(skin["OfferID"], price=price))

        return skins

    def get_rso_token(self) -> str:
        rso = self.session.get(
            f"{self.lockfile.protocol}://127.0.0.1:{self.lockfile.port}/entitlements/v2/token",
            auth=HTTPBasicAuth("riot", self.lockfile.password),
            verify=False
        ).json()
        return rso["authorization"]["accessToken"]["token"]

    def get_pas_token(self) -> str:
        pas = self.session.get(
            "https://riot-geo.pas.si.riotgames.com/pas/v1/service/chat",
            headers={"Authorization": f"Bearer {self.rso_token}"},
            verify=False
        ).text

        return pas
