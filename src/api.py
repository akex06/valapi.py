"""
Classes and methods related to Valorant API calls
"""

import sqlite3

import requests

from src import Cache


class Api:
    accountXP = '/account-xp/v1/players/'
    mmr = '/mmr/v1/players/'
    store = '/store/v2/storefront/'
    wallet = '/store/v1/wallet/'
    owned = '/store/v1/entitlements/'


class URLS:
    AUTH_URL = "https://auth.riotgames.com/api/v1/authorization"
    REGION_URL = 'https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant'
    VERIFIED_URL = "https://email-verification.riotgames.com/api/v1/account/status"
    ENTITLEMENT_URL = 'https://entitlements.auth.riotgames.com/api/token/v1'
    USERINFO_URL = "https://auth.riotgames.com/userinfo"


class Valorant:
    def __init__(self, username: str, password: str, auth=True) -> None:
        self.conn = sqlite3.connect("skins.sqlite3")
        self.c = self.conn.cursor()

        self.cache = Cache(self.conn)

        build = requests.get('https://valorant-api.com/v1/version').json()['data']['riotClientBuild']

        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": f"RiotClient/{build} riot-status (Windows;10;;Professional, x64)",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "application/json, text/plain, */*"
        }

        self.username = username
        self.password = password

        if auth:
            self.access_token, self.id_token = self.get_access_token()
            self.entitlement_token = self.get_entitlement_token()

            self.region = self.get_region()
            self.user_info = self.get_user_info()

    def get_access_token(self) -> tuple:
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
        request = self.session.put(url=URLS.AUTH_URL, json=put_data)

        response = dict(map(
            lambda x: x.split("="),
            request.json()["response"]["parameters"]["uri"].split("#")[1].split("&")
        ))  # weird shit, extracts anchors from url and transforms them into a dict

        return response["access_token"], response["id_token"]

    def get_entitlement_token(self):
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        })

        return self.session.post(URLS.ENTITLEMENT_URL, json={}).json()["entitlements_token"]

    def get_user_info(self):
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        })

        return self.session.post(URLS.USERINFO_URL, json={}).json()

    def get_region(self):
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
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
            'https://valorant-api.com/v1/version',
            timeout=30
        ).json()['data']['riotClientVersion']
        client_platform = ('ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmV'
                           'yc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9')

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Riot-Entitlements-JWT': self.entitlement_token,
            'X-Riot-ClientPlatform': client_platform,
            'X-Riot-ClientVersion': client_version,
            'Content-Type': 'application/json'
        }

        store_api = f"{server}{Api.store}{self.user_info['sub']}"
        return requests.get(store_api, headers=headers).json()

    def get_daily_skins(self) -> list[Weapon]:
        offers = self.get_store()["SkinsPanelLayout"]["SingleItemStoreOffers"]

        skins: list[Weapon] = list()
        for skin in offers:
            skin_uuid, skin_name = self.get_skin_by_level(skin["OfferID"])
            skin_image = f"https://media.valorant-api.com/weaponskins/{skin_uuid}/displayicon.png"
            price = skin["Cost"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]
            skins.append(Weapon(skin_uuid, skin_name, price, skin_image))

        return skins

    def get_skin_by_level(self, uuid: str) -> tuple:
        self.c.execute(
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
            (uuid,)
        )

        return self.c.fetchone()
