# TODO: change shitname

import os
import sqlite3
from typing import Any


def api_to_parameters(mapping: dict[str, str], data: dict[str, Any]) -> dict[str, str]:
    args = dict()
    for k, v in data.items():
        arg_name = mapping.get(k)
        if arg_name is None:
            continue

        args[arg_name] = v

    return args


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
        conn = sqlite3.connect("valorant/skins.sqlite3")
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
        conn = sqlite3.connect("valorant/skins.sqlite3")
        c = conn.cursor()

        name = c.execute("SELECT name FROM skins WHERE uuid = ?", (self.uuid,)).fetchone()
        if name is None:
            return None

        return name[0]


class Region:
    def __init__(self, region: str, shard: str) -> None:
        self.region = region
        self.shard = shard


class Regions:
    AsiaPacific = Region("ap", "ap")
    Brasil = Region("br", "na")
    Europe = Region("eu", "eu")
    Korea = Region("kr", "kr")
    LatinAmerica = Region("latam", "na")
    NorthAmerica = Region("na", "na")


class LockFile:
    def __init__(self, lockfile_fp: str = None) -> None:
        if lockfile_fp is None:
            lockfile_fp = os.getenv("LOCALAPPDATA") + "\\Riot Games\\Riot Client\\Config\\lockfile"

        with open(lockfile_fp, encoding="utf-8") as f:
            self.name, self.pid, self.port, self.password, self.protocol = f.read().split(":")


class Gun:
    def __init__(
            self,
            _id: str,
            charm_instance_id: str | None,
            charm_id: str | None,
            charm_level_id: str | None,
            skin_id: str,
            skin_level_id: str,
            chroma_id: str,
            attachments: list[str]
    ) -> None:
        self._id = _id
        self.charm_instance_id = charm_instance_id
        self.charm_id = charm_id
        self.charm_level_id = charm_level_id
        self.skin_id = skin_id
        self.skin_level_id = skin_level_id
        self.chroma_id = chroma_id
        self.attachments = attachments


class Role:
    def __init__(
            self,
            _id: str,
            name: str,
            description: str,
            display_icon: str
    ):
        self.id = _id
        self.name = name
        self.description = description
        self.display_icon = display_icon


class Ability:
    def __init__(
            self,
            name: str,
            slot: int,
            description: str,
            display_icon: str
    ):
        self.name = name
        self.slot = slot
        self.description = description
        self.display_icon = display_icon


class Agent:
    def __init__(
            self,
            _id: str,
            name: str,
            description: str,
            developer_name: str,
            tags: list[str],
            display_icon: str,
            portrait: str,
            kill_portrait: str,
            background: str,
            colors: list[str],
            role: Role,
            abilities: list[Ability]
    ):
        self.id = _id
        self.name = name
        self.description = description
        self.developer_name = developer_name
        self.tags = tags
        self.display_icon = display_icon
        self.portrait = portrait
        self.kill_portrait = kill_portrait
        self.background = background
        self.colors = colors
        self.role = role
        self.abilities = abilities

    @classmethod
    def from_api(cls, data: dict):
        mapping = {
            "uuid": "_id",
            "displayName": "name",
            "description": "description",
            "developerName": "developer_name",
            "characterTags": "tags",
            "displayIcon": "display_icon",
            "bustPortrait": "portrait",
            "killfeedPortrait": "kill_portrait",
            "background": "background",
            "backgroundGradientColors": "colors",
            "role": "role",
            "abilities": "abilities",
        }

        return cls(**api_to_parameters(mapping, data))
