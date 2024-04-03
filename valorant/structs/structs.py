import os

import msgspec


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


class Version(msgspec.Struct):
    # TODO: Learn to pass the contents of valorant-api.com "data" attrib to the struct without converting to json
    manifestId: str
    branch: str
    version: str
    buildVersion: str
    engineVersion: str
    riotClientVersion: str
    riotClientBuild: str
    buildDate: str
