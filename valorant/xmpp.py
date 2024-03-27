import abc
import asyncio
import ssl
from typing import Callable
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from valorant import Valorant
from valorant.constants import xmpp_regions, xmpp_servers


# TODO create Match class to handle updates


class XMPP(abc.ABC):
    """
    A class to act as a client for the Riot XMPP servers.

    not stolen from https://github.com/w1gs/
    """

    def __init__(
            self,
            username: str,
            password: str
    ) -> None:
        """Initializes the RiotXMPP object."""
        self.val = Valorant(username, password)
        self.processors = {
            "presence": self.process_presence,
            "iq": self.process_iq,
            "message": self.process_message
        }

        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None

        self.region = self.val.get_region()
        self.xmpp_region = xmpp_regions[self.region.region]
        self.xmpp_server = xmpp_servers[self.xmpp_region]

        self.context = ssl.create_default_context()
        self.context.check_hostname = True
        self.context.verify_mode = ssl.CERT_REQUIRED

        self.buffer = b""

    def get_stream_element(self) -> bytes:
        """Returns the stream element in byte format."""

        stream = rf'<?xml version="1.0" encoding="UTF-8"?><stream:stream to="{self.xmpp_region}.pvp.net" xml:lang="en" version="1.0" xmlns="jabber:client" xmlns:stream="http://etherx.jabber.org/streams">'
        return stream.encode(encoding="UTF-8")

    def get_rso_auth(self) -> bytes:
        """Returns the RSO authentication element in byte format."""

        auth = Element(
            "auth",
            attrib={
                "mechanism": "X-Riot-RSO-PAS",
                "xmlns": "urn:ietf:params:xml:ns:xmpp-sasl",
            },
        )
        rso_token_elem = Element("rso_token")
        rso_token_elem.text = self.val.auth.get_access_token()
        pas_token_elem = Element("pas_token")
        pas_token_elem.text = self.val.auth.get_pas_token()
        auth.append(rso_token_elem)
        auth.append(pas_token_elem)
        return ElementTree.tostring(auth, encoding="utf-8")

    @staticmethod
    def get_bind_request() -> bytes:
        """Returns the bind request element in byte format."""

        iq_element = Element("iq", attrib={"id": "_xmpp_bind1", "type": "set"})
        bind_element = Element(
            "bind", attrib={"xmlns": "urn:ietf:params:xml:ns:xmpp-bind"}
        )

        puuid_element = Element("puuid-mode", attrib={"enabled": "true"})

        iq_element.append(bind_element)

        bind_element.append(puuid_element)

        return ElementTree.tostring(iq_element, encoding="utf-8")

    def get_entitlement_request(self) -> bytes:
        """Returns the entitlements request element in byte format."""

        iq_element = Element("iq", attrib={"id": "xmpp_entitlements_0", "type": "set"})
        entitlements_element = Element(
            "entitlements", attrib={"xmlns": "urn:riotgames:entitlements"}
        )
        token_element = Element("token")
        token_element.text = self.val.auth.get_entitlement_token()
        iq_element.append(entitlements_element)
        entitlements_element.append(token_element)
        return ElementTree.tostring(iq_element, encoding="utf-8")

    @staticmethod
    def get_session_request() -> bytes:
        """Returns the session request element in byte format."""

        iq_element = Element("iq", attrib={"id": "_xmpp_session1", "type": "set"})
        session_element = Element(
            "session", attrib={"xmlns": "urn:ietf:params:xml:ns:xmpp-session"}
        )
        platform_element = Element("platform")
        platform_element.text = "riot"
        iq_element.append(session_element)
        session_element.append(platform_element)
        return ElementTree.tostring(iq_element, encoding="utf-8")

    async def connect(self):
        """Establishes the connection to the server."""

        self.reader, self.writer = await asyncio.open_connection(
            host=self.xmpp_server, port=5223, ssl=self.context
        )
        print("Connected")

    async def send(self, message: bytes):
        self.writer.write(message)
        await self.writer.drain()

    async def close(self):
        """Closes the XMPP client connection."""

        print("Closing connection...")
        self.writer.close()
        await self.writer.wait_closed()

    async def start_auth_flow(self):
        """Starts the authentication flow for the XMPP client."""

        # TODO add in checks for separators when a stanza fails
        auth_flow = [
            {
                "stanza": self.get_stream_element(),
                "seperator": b"</stream:features>",
                "stage": "stream element",
            },
            {
                "stanza": self.get_rso_auth(),
                "seperator": b"</success>",
                "stage": "RSO auth element",
            },
            {
                "stanza": self.get_stream_element(),
                "seperator": b"</stream:features>",
                "stage": "stream element",
            },
            {
                "stanza": self.get_bind_request(),
                "seperator": b"</bind></iq>",
                "stage": "bind element",
            },
            {
                "stanza": self.get_entitlement_request(),
                "seperator": b"></iq>",
                "stage": "entitlement element",
            },
            {
                "stanza": self.get_session_request(),
                "seperator": b"</session></iq>",
                "stage": "session element",
            },
        ]

        # Start the auth flow
        for item in auth_flow:
            await self.send(item["stanza"])
            await self.reader.readuntil(item["seperator"])

        await self.send(b"<presence/>")
        await self.reader.readuntil(b"</presence>")
        print("ended auth")

    async def add_friend(self, name: str, tag: str) -> None:
        await self.send(f"<iq id=\"roster_add_10\" type=\"set\"><query xmlns=\"jabber:iq:riotgames:roster\"><item "
                        f"subscription=\"pending_out\"><id name=\"{name}\" tagline=\""
                        f"{tag}\"/></item></query></iq>".encode("utf-8"))

    async def process_messages(self):
        while True:
            self.buffer += await self.reader.read(4096)
            try:
                xml_element: Element = ElementTree.fromstring(b"<wrapper>" + self.buffer + b"</wrapper>")
                for root in xml_element:
                    processor = self.processors.get(root.tag)
                    if processor is None:
                        print("Processor not implemented for" + root.tag)
                        continue

                    await self.processors[root.tag](root)

                self.buffer = b""
            except ElementTree.ParseError:
                continue

    @abc.abstractmethod
    async def process_message(self, element: Element) -> None:
        pass

    @abc.abstractmethod
    async def process_iq(self, element: Element) -> None:
        pass

    @abc.abstractmethod
    async def process_presence(self, element: Element) -> None:
        pass
