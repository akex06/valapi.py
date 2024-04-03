import os
from typing import Literal

import msgspec
import requests

from valorant.constants import URLS


class Auth:
    def __init__(self, session: requests.Session, username: str, password: str) -> None:
        self.session = session

        self.username = username
        self.password = password

        self.__access_token = None
        self.__id_token = None
        self.__entitlement_token = None
        self.__pas_token = None

    def set_auth_cookies(self) -> None:
        self.session.post(
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

    def get_access_token(self) -> str:
        if self.__access_token is not None:
            return self.__access_token

        put_data = {
            "language": "en_US",
            "password": self.password,
            "remember": "true",
            "type": "auth",
            "username": self.username,
        }
        request = self.session.put(url=URLS.AUTH_URL, json=put_data).json()

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
                "Authorization": f"Bearer {self.get_access_token()}",
            },
            json={},
        ).json()["entitlements_token"]

        return self.__entitlement_token

    def get_pas_token(self) -> str:
        if self.__pas_token is not None:
            return self.__pas_token

        self.__pas_token = self.session.get(
            "https://riot-geo.pas.si.riotgames.com/pas/v1/service/chat",
            headers={"Authorization": f"Bearer {self.get_access_token()}"},
        ).text
        return self.__pas_token


class LockFile:
    def __init__(self, lockfile_fp: str = None) -> None:
        if lockfile_fp is None:
            lockfile_fp = (
                os.getenv("LOCALAPPDATA")
                + "\\Riot Games\\Riot Client\\Config\\lockfile"
            )

        with open(lockfile_fp, encoding="utf-8") as f:
            self.name, self.pid, self.port, self.password, self.protocol = (
                f.read().split(":")
            )


class Role(msgspec.Struct):
    id: str = msgspec.field(name="uuid")
    name: str = msgspec.field(name="displayName")
    description: str = msgspec.field(name="description")
    icon: str = msgspec.field(name="displayIcon")


class Ability(msgspec.Struct):

    slot: str = msgspec.field(name="slot")
    name: str = msgspec.field(name="displayName")
    description: str = msgspec.field(name="description")
    icon: str = msgspec.field(name="displayIcon")


class Agent(msgspec.Struct):
    id: str = msgspec.field(name="uuid")
    name: str = msgspec.field(name="displayName")
    description: str = msgspec.field(name="description")
    developer_name: str = msgspec.field(name="developerName")
    tags: list[str] | None = msgspec.field(name="characterTags")
    display_icon: str = msgspec.field(name="displayIcon")
    portrait: str = msgspec.field(name="fullPortrait")
    kill_portrait: str = msgspec.field(name="killfeedPortrait")
    background: str = msgspec.field(name="background")
    colors: list[str] = msgspec.field(name="backgroundGradientColors")
    role: str = msgspec.field(name="role")
    abilities: list[Ability] = msgspec.field(name="abilities")


class Version(msgspec.Struct):
    manifest_id: str = msgspec.field(name="manifestId")
    branch: str = msgspec.field(name="branch")
    version: str = msgspec.field(name="version")
    build_version: str = msgspec.field(name="buildVersion")
    engine_version: str = msgspec.field(name="engineVersion")
    riot_client_version: str = msgspec.field(name="riotClientVersion")
    riot_client_build: str = msgspec.field(name="riotClientBuild")
    build_date: str = msgspec.field(name="buildDate")


class User(msgspec.Struct):
    country: str = msgspec.field(name="country")
    player_id: str = msgspec.field(name="sub")
    is_email_verified: str = msgspec.field(name="email_verified")
    player_plocale: str = msgspec.field(name="player_plocale")
    country_at: str = msgspec.field(name="country_at")
    pw: str = msgspec.field(name="pw")
    is_phone_number_verified: str = msgspec.field(name="phone_number_verified")
    ppid: str = msgspec.field(name="ppid")
    player_locale: str = msgspec.field(name="player_locale")
    acct: str = msgspec.field(name="acct")
    jti: str = msgspec.field(name="jti")


class Progress(msgspec.Struct):
    level: int = msgspec.field(name="Level")
    xp: int = msgspec.field(name="XP")


class XPSource(msgspec.Struct):
    id: Literal["time-played", "match-win", "first-win-of-the-day"] = msgspec.field(
        name="ID"
    )
    amount: int = msgspec.field(name="Amount")


class AccountXPMatch(msgspec.Struct):
    start: str = msgspec.field(name="MatchStart")
    start_progress: Progress = msgspec.field(name="StartProgress")
    end_progress: Progress = msgspec.field(name="EndProgress")
    xp_delta: int = msgspec.field(name="XPDelta")
    xp_sources: list[XPSource] = msgspec.field(name="XPSources")
    xp_multipliers: list[str] = msgspec.field(name="XPMultipliers")


class AccountXP(msgspec.Struct):
    version: int = msgspec.field(name="Version")
    player_id: str = msgspec.field(name="Subject")
    progress: Progress = msgspec.field(name="Progress")
    history: list[AccountXPMatch] = msgspec.field(name="History")
    last_time_granted_first_win: str = msgspec.field(name="LastTimeGrantedFirstWin")
    next_time_first_win_available: str = msgspec.field(name="NextTimeFirstWinAvailable")
