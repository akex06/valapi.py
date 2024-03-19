# TODO: change shitname

import os
import sqlite3


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
        conn = sqlite3.connect("valostore/skins.sqlite3")
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
        conn = sqlite3.connect("valostore/skins.sqlite3")
        c = conn.cursor()

        name = c.execute("SELECT name FROM skins WHERE uuid = ?", (self.uuid,)).fetchone()
        if name is None:
            return None

        return name[0]


class LockFile:
    def __init__(self, lockfile_fp: str = None) -> None:
        if lockfile_fp is None:
            lockfile_fp = os.getenv("LOCALAPPDATA") + "\\Riot Games\\Riot Client\\Config\\lockfile"

        with open(lockfile_fp, encoding="utf-8") as f:
            self.name, self.pid, self.port, self.password, self.protocol = f.read().split(":")


class Player:
    def __init__(
            self,
            game_name: str,
            game_tag: str,
            name: str,
            note: str,
            pid: str,
            puuid: str,
            region: str
    ) -> None:
        self.game_name = game_name
        self.game_tag = game_tag
        self.name = name
        self.note = note
        self.pid = pid
        self.id = puuid
        self.region = region


class Friend(Player):
    def __init__(
            self,
            active_platform: str | None,
            display_group: str,
            game_name: str,
            game_tag: str,
            group: str,
            last_online_ts: str | None,
            name: str,
            note: str,
            pid: str,
            puuid: str,
            region: str
    ) -> None:
        super().__init__(game_name, game_tag, name, note, pid, puuid, region)
        self.active_platform = active_platform
        self.display_group = display_group
        self.game_name = game_name
        self.game_tag = game_tag
        self.group = group
        self.last_online_ts = last_online_ts
        self.name = name
        self.note = note
        self.pid = pid
        self.puuid = puuid
        self.region = region
