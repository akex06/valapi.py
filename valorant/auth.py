import os

import httpx

from valorant.constants import URLS


class LockFile:
    def __init__(self, lockfile_path: str = None) -> None:
        if lockfile_path is None:
            lockfile_path = (
                os.getenv("LOCALAPPDATA")
                + "\\Riot Games\\Riot Client\\Config\\lockfile"
            )

        with open(lockfile_path, encoding="utf-8") as f:
            self.name, self.pid, self.port, self.password, self.protocol = (
                f.read().split(":")
            )


class Auth:
    def __init__(self, client: httpx.AsyncClient, username: str, password: str) -> None:
        self.client = client

        self.username = username
        self.password = password

        self.__access_token = None
        self.__id_token = None
        self.__entitlement_token = None
        self.__pas_token = None

    async def set_auth_cookies(self) -> None:
        await self.client.post(
            url=URLS.AUTH_URL,
            json={
                "acr_values": "urn:riot:bronze",
                "claims": "",
                "client_id": "riot-client",
                "nonce": "oYnVwCSrlS5IHKh7iI16oQ",
                "redirect_uri": "http://localhost/redirect",
                "response_type": "token id_token",
                "scope": "openid link ban lol_region",
            },
        )

    async def get_access_token(self) -> str:
        if self.__access_token is not None:
            return self.__access_token

        request = (
            await self.client.put(
                url=URLS.AUTH_URL,
                json={
                    "language": "en_US",
                    "password": self.password,
                    "remember": "true",
                    "type": "auth",
                    "username": self.username,
                },
            )
        ).json()

        if request["type"] == "multifactor":
            raise ValueError("Multifactor needed, please disable it and try again")

        tokens = dict(
            map(
                lambda x: x.split("="),
                request["response"]["parameters"]["uri"].split("#")[1].split("&"),
            )
        )  # weird shit, extracts anchors from url and transforms them into a dict

        self.__access_token, self.__id_token = (
            tokens["access_token"],
            tokens["id_token"],
        )
        return self.__access_token

    async def get_id_token(self) -> str:
        if self.__id_token is not None:
            return self.__id_token

        self.__access_token, self.__id_token = await self.get_access_token()
        return self.__id_token

    async def get_entitlement_token(self) -> str:
        if self.__entitlement_token is not None:
            return self.__entitlement_token

        self.__entitlement_token = (
            await self.client.post(
                URLS.ENTITLEMENT_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {await self.get_access_token()}",
                },
                json={},
            )
        ).json()["entitlements_token"]

        return self.__entitlement_token

    async def get_pas_token(self) -> str:
        if self.__pas_token is not None:
            return self.__pas_token

        self.__pas_token = (
            await self.client.get(
                "https://riot-geo.pas.si.riotgames.com/pas/v1/service/chat",
                headers={"Authorization": f"Bearer {await self.get_access_token()}"},
            )
        ).text
        return self.__pas_token
