import base64
import json
import socket
import ssl

from valorant.constants import xmpp_servers, xmpp_regions


class XMPP:
    def __init__(self, rso_token: str, pas_token: str):
        self.rso_token = rso_token
        self.pas_token = pas_token

        region = json.loads(base64.b64decode(pas_token.split(".")[1] + "=="))["affinity"]
        self.port = 5223
        self.server = xmpp_servers[region]
        self.region = xmpp_regions[region]

        ssl_context = ssl.create_default_context()
        self.sock = ssl_context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=self.server)
        self.sock.connect((self.server, self.port))

    def auth(self) -> None:
        auth_data = [
            f"<?xml version=\"1.0\"?><stream:stream to=\"{self.region}.pvp.net\" version=\"1.0\" xmlns:stream=\"http://etherx.jabber.org/streams\">",
            f"<auth mechanism=\"X-Riot-RSO-PAS\" xmlns=\"urn:ietf:params:xml:ns:xmpp-sasl\"><rso_token>{self.rso_token}</rso_token><pas_token>{self.pas_token}</pas_token></auth>",
            f"<?xml version=\"1.0\"?><stream:stream to=\"{self.region}.pvp.net\" version=\"1.0\" xmlns:stream=\"http://etherx.jabber.org/streams\">",
            f"<iq id=\"_xmpp_bind1\" type=\"set\"><bind xmlns=\"urn:ietf:params:xml:ns:xmpp-bind\"></bind></iq>",
            f"<iq id=\"_xmpp_session1\" type=\"set\"><session xmlns=\"urn:ietf:params:xml:ns:xmpp-session\"/></iq>"
        ]
        for i in auth_data:
            self.sock.sendall(i.encode())
            print(self.sock.recv(4096))



