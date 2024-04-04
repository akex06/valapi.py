import msgspec


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
