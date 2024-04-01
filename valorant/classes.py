import abc
import os
from typing import Self

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
                "scope": "openid link ban lol_region"
            }
        )

    def get_access_token(self) -> str:
        if self.__access_token is not None:
            return self.__access_token

        put_data = {
            "language": "en_US",
            "password": self.password,
            "remember": "true",
            "type": "auth",
            "username": self.username
        }
        request = self.session.put(url=URLS.AUTH_URL, json=put_data).json()

        if request["type"] == "multifactor":
            raise ValueError("Multifactor needed, please disable it and try again")

        tokens = dict(map(
            lambda x: x.split("="),
            request["response"]["parameters"]["uri"].split("#")[1].split("&")
        ))  # weird shit, extracts anchors from url and transforms them into a dict

        self.__access_token, self.__id_token = tokens["access_token"], tokens["id_token"]
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
                "Authorization": f"Bearer {self.get_access_token()}"
            },
            json={}
        ).json()["entitlements_token"]

        return self.__entitlement_token

    def get_pas_token(self) -> str:
        if self.__pas_token is not None:
            return self.__pas_token

        self.__pas_token = self.session.get(
            "https://riot-geo.pas.si.riotgames.com/pas/v1/service/chat",
            headers={
                "Authorization": f"Bearer {self.get_access_token()}"
            }
        ).text
        return self.__pas_token


class LockFile:
    def __init__(self, lockfile_fp: str = None) -> None:
        if lockfile_fp is None:
            lockfile_fp = os.getenv("LOCALAPPDATA") + "\\Riot Games\\Riot Client\\Config\\lockfile"

        with open(lockfile_fp, encoding="utf-8") as f:
            self.name, self.pid, self.port, self.password, self.protocol = f.read().split(":")


class APIConverter(abc.ABC):
    @abc.abstractmethod
    def __init__(self, **kwargs) -> None:
        raise NotImplementedError("__init__ must be defined on subclass")

    @property
    @abc.abstractmethod
    def mapping(self) -> dict[str, str | tuple[str, Self]]:
        """
        A mapping of the names of the parameters.

        Consists of a str denoting the API parameter name output and a union of str and tuple[str, Self].
        If the map value is a str, the converter will just pass the value, if it's an instance of APIConverter or
        a list of APIConverter it will convert them individually using the APIConverter.from_api_output method.

        :return: dict[str, tuple[str, APIConverter]]
        """
        pass

    @classmethod
    def from_api_output(cls, data: dict):
        """
        Returns the class based on the mapping specified at the subclass

        :param data: The API output
        :return: An instance of the subclass
        """

        params = dict()
        for k, v in data.items():
            param = cls.mapping.get(k)
            if param is None:
                continue

            if isinstance(param, str):  # Assign parameter if there's no type passed
                params[param] = v
            else:  #
                param, _type = param
                if _type.__base__ == APIConverter:  # Filter the type passed
                    if (
                            isinstance(v, (list, tuple, set))
                            and not isinstance(v, str)
                    ):  # If it's a collection, convert all elements individually
                        params[param] = [_type.from_api_output(x) for x in v]
                    else:
                        params[param] = _type.from_api_output(v)
                else:
                    raise ValueError(f"Type {_type} is not a subclass of APIConverter")

        return cls(**params)


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


class Role(APIConverter):
    mapping = {
        "uuid": "_id",
        "displayName": "name",
        "description": "description",
        "displayIcon": "display_icon"
    }

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


class Ability(APIConverter):
    mapping = {
        "slot": "slot",
        "displayName": "name",
        "description": "description",
        "displayIcon": "display_icon"
    }

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


class Agent(APIConverter):
    mapping = {
        "uuid": "_id",
        "displayName": "name",
        "description": "description",
        "developerName": "developer_name",
        "characterTags": "tags",
        "displayIcon": "display_icon",
        "fullPortrait": "portrait",
        "killfeedPortrait": "kill_portrait",
        "background": "background",
        "backgroundGradientColors": "colors",
        "role": ("role", Role),
        "abilities": ("abilities", Ability)
    }

    def __init__(
            self,
            _id: str,
            name: str,
            description: str,
            developer_name: str,
            tags: list[str] | None,
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
    def from_uuid(cls, uuid: str):
        return cls.from_api_output(requests.get(f"https://valorant-api.com/v1/agents/{uuid}").json()["data"])


class Agents:
    def __init__(self):
        agent_list = requests.get("https://valorant-api.com/v1/agents/").json()["data"]
        agents = {agent["uuid"]: agent for agent in agent_list}

        self.GEKKO = Agent.from_api_output(agents["e370fa57-4757-3604-3648-499e1f642d3f"])
        self.FADE = Agent.from_api_output(agents["dade69b4-4f5a-8528-247b-219e5a1facd6"])
        self.BREACH = Agent.from_api_output(agents["5f8d3a7f-467b-97f3-062c-13acf203c006"])
        self.DEADLOCK = Agent.from_api_output(agents["cc8b64c8-4b25-4ff9-6e7f-37b4da43d235"])
        self.RAZE = Agent.from_api_output(agents["f94c3b30-42be-e959-889c-5aa313dba261"])
        self.CHAMBER = Agent.from_api_output(agents["22697a3d-45bf-8dd7-4fec-84a9e28c69d7"])
        self.KAYO = Agent.from_api_output(agents["601dbbe7-43ce-be57-2a40-4abd24953621"])
        self.SKYE = Agent.from_api_output(agents["6f2a04ca-43e0-be17-7f36-b3908627744d"])
        self.CYPHER = Agent.from_api_output(agents["117ed9e3-49f3-6512-3ccf-0cada7e3823b"])
        self.SOVA = Agent.from_api_output(agents["320b2a48-4d9b-a075-30f1-1f93a9b638fa"])
        self.KILLJOY = Agent.from_api_output(agents["1e58de9c-4950-5125-93e9-a0aee9f98746"])
        self.HARBOR = Agent.from_api_output(agents["95b78ed7-4637-86d9-7e41-71ba8c293152"])
        self.VIPER = Agent.from_api_output(agents["707eab51-4836-f488-046a-cda6bf494859"])
        self.PHOENIX = Agent.from_api_output(agents["eb93336a-449b-9c1b-0a54-a891f7921d69"])
        self.ASTRA = Agent.from_api_output(agents["41fb69c1-4189-7b37-f117-bcaf1e96f1bf"])
        self.BRIMSTONE = Agent.from_api_output(agents["9f0d8ba9-4140-b941-57d3-a7ad57c6b417"])
        self.ISO = Agent.from_api_output(agents["0e38b510-41a8-5780-5e8f-568b2a4f2d6c"])
        self.NEON = Agent.from_api_output(agents["bb2a4828-46eb-8cd1-e765-15848195d751"])
        self.YORU = Agent.from_api_output(agents["7f94d92c-4234-0a36-9646-3a87eb8b5c89"])
        self.SAGE = Agent.from_api_output(agents["569fdd95-4d10-43ab-ca70-79becc718b46"])
        self.REYNA = Agent.from_api_output(agents["a3bfb853-43b2-7238-a4f1-ad90e9e46bcc"])
        self.OMEN = Agent.from_api_output(agents["8e253930-4c05-31dd-1b6c-968525494517"])
        self.JETT = Agent.from_api_output(agents["add6443a-41bd-e414-f6ad-e58d267f4e95"])
        self.CLOVE = Agent.from_api_output(agents["1dbf2edd-4729-0984-3115-daa5eed44993"])
