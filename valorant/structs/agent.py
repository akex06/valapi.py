import msgspec


class Ability(
    msgspec.Struct,
    rename={
        "slot": "slot",
        "name": "displayName",
        "description": "description",
        "icon": "displayIcon",
    },
):
    slot: str
    name: str
    description: str
    icon: str | None


class Role(
    msgspec.Struct,
    rename={
        "id": "uuid",
        "name": "displayName",
        "description": "description",
        "icon": "displayIcon",
    },
):
    id: str
    name: str
    description: str
    icon: str


class Agent(
    msgspec.Struct,
    rename={
        "id": "uuid",
        "name": "displayName",
        "developer_name": "developerName",
        "tags": "characterTags",
        "display_icon": "displayIcon",
        "portrait": "fullPortrait",
        "kill_portrait": "killfeedPortrait",
        "colors": "backgroundGradientColors",
    },
):
    id: str
    name: str
    description: str
    developer_name: str
    display_icon: str | None
    portrait: str
    kill_portrait: str
    background: str
    colors: list[str]
    role: Role
    abilities: list[Ability]
    tags: list[str] | None


class AgentResponse(msgspec.Struct):
    status: int
    data: list[Agent]
