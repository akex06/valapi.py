import msgspec


class Gun(
    msgspec.Struct,
    rename={
        "id": "Subject",
        "charm_instance_id": "CharmInstanceID",
        "charm_id": "CharmID",
        "charm_level_id": "CharmLevelID",
        "skin_id": "SkinID",
        "skin_level_id": "SkinLevelID",
        "chroma_id": "ChromaID",
        "attachments": "attachments",
    },
):
    id: int
    skin_id: str
    skin_level_id: str
    chroma_id: str
    attachments: list[str]
    charm_instance_id: str | None = None
    charm_id: str | None = None
    charm_level_id: str | None = None


class Identity(
    msgspec.Struct,
    rename={
        "player_card_id": "PlayerCardID",
        "player_title_id": "PlayerTitleID",
        "level": "AccountLevel",
        "level_border": "PreferredLevelBorderID",
        "hide_level": "HideAccountLevel",
    },
):
    player_card_id: str
    player_title_id: str
    level: int
    level_border: str
    hide_level: bool


class Spray(
    msgspec.Struct,
    rename={"slot": "EquipSlotID", "spray_id": "SprayID"},
):
    slot: str
    spray_id: str


class Loadout(
    msgspec.Struct,
    rename={
        "player_id": "Subject",
        "version": "Version",
        "guns": "Guns",
        "sprays": "Sprays",
        "identity": "Identity",
        "incognito": "Incognito",
    },
):
    player_id: str
    version: int
    guns: list[Gun]
    sprays: list[Spray]
    identity: Identity
    incognito: bool
