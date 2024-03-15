"""
Classes and methods related to Valorant API calls
"""

import sqlite3

import requests

from src import Cache


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


class URLS:
    AUTH_URL = "https://auth.riotgames.com/api/v1/authorization"
    REGION_URL = "https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant"
    VERIFIED_URL = "https://email-verification.riotgames.com/api/v1/account/status"
    ENTITLEMENT_URL = "https://entitlements.auth.riotgames.com/api/token/v1"
    USERINFO_URL = "https://auth.riotgames.com/userinfo"


class Valorant:
    def __init__(self, username: str, password: str, auth=True) -> None:
        self.conn = sqlite3.connect("src/skins.sqlite3")
        self.c = self.conn.cursor()

        self.cache = Cache(self.conn)

        build = requests.get("https://valorant-api.com/v1/version").json()["data"]["riotClientBuild"]

        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": f"RiotClient/{build} riot-status (Windows;10;;Professional, x64)",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "application/json, text/plain, */*"
        }

        self.username = username
        self.password = password

        self.access_token, self.id_token = None, None
        self.entitlement_token = None

        self.region = None
        self.user_info = None

        if auth:
            self.auth()

    def auth(self, mfa_code: str = None) -> None:
        if mfa_code is None:
            self.access_token, self.id_token = self.get_access_token()
        else:
            self.access_token, self.id_token = self.get_access_token_with_mfa(mfa_code)

        self.entitlement_token = self.get_entitlement_token()

        self.region = self.get_region()
        self.user_info = self.get_user_info()

    def get_access_token(self) -> tuple | None:
        post_data = {
            "acr_values": "urn:riot:bronze",
            "claims": "",
            "client_id": "riot-client",
            "nonce": "oYnVwCSrlS5IHKh7iI16oQ",
            "redirect_uri": "http://localhost/redirect",
            "response_type": "token id_token",
            "scope": "openid link ban lol_region"
        }
        put_data = {
            "language": "en_US",
            "password": self.password,
            "remember": "true",
            "type": "auth",
            "username": self.username
        }

        self.session.post(url=URLS.AUTH_URL, json=post_data)
        request = self.session.put(url=URLS.AUTH_URL, json=put_data).json()

        if request["type"] == "multifactor":
            raise ValueError("Multifactor needed")

        response = dict(map(
            lambda x: x.split("="),
            request["response"]["parameters"]["uri"].split("#")[1].split("&")
        ))  # weird shit, extracts anchors from url and transforms them into a dict

        return response["access_token"], response["id_token"]

    def get_access_token_with_mfa(self, mfa_code: str) -> tuple:
        request = self.session.put(
            url=URLS.AUTH_URL,
            json={
                "type": "multifactor",
                "code": mfa_code,
                "rememberDevice": True
            }
        )
        print(request.text)
        return 1, 1

    def get_entitlement_token(self):
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        })

        return self.session.post(URLS.ENTITLEMENT_URL, json={}).json()["entitlements_token"]

    def get_user_info(self):
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        })

        return self.session.post(URLS.USERINFO_URL, json={}).json()

    def get_region(self):
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        })

        return self.session.put(
            "https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant",
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
