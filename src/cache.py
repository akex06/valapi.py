import sqlite3
import requests


class Cache:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.c = self.conn.cursor()

        self.create_tables()

    def create_tables(self) -> None:
        self.c.execute(
            "CREATE TABLE IF NOT EXISTS skins ("
            "   uuid TEXT PRIMARY KEY,"
            "   name TEXT"
            ");"
        )
        self.c.execute(
            "CREATE TABLE IF NOT EXISTS skinlevels ("
            "   uuid TEXT PRIMARY KEY,"
            "   name TEXT"
            ");"
        )

        self.conn.commit()

    def update_skins(self) -> None:
        weapons = requests.get("https://valorant-api.com/v1/weapons/skins").json()["data"]

        for weapon in weapons:
            uuid = weapon["uuid"]
            display_name = weapon["displayName"]
            try:
                self.c.execute("INSERT INTO skins (uuid, name) VALUES (?, ?)", (uuid, display_name))
            except sqlite3.IntegrityError:
                self.c.execute("UPDATE skins SET name = ? WHERE uuid = ?", (display_name, uuid))

            for level in weapon["levels"]:
                try:
                    self.c.execute(
                        "INSERT INTO skinlevels (uuid, name) VALUES (?, ?)",
                        (level["uuid"], level["displayName"])
                    )
                except sqlite3.IntegrityError:
                    self.c.execute(
                        "UPDATE skinlevels SET name = ? WHERE uuid = ?",
                        (level["displayName"], level["uuid"])
                    )

        self.conn.commit()
