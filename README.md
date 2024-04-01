# ValAPI.py

ValAPI.py is a Valorant API wrapper and XMPP client.

Implementing your own XMPP

```py
from valorant import XMPP


class MyCustomXMPPClient(XMPP):
    def __init__(
            self,
            username: str,
            password: str
    ) -> None:
        super().__init__(username, password)

    async def process_message(self, element: Element) -> None:
        pass

    async def process_iq(self, element: Element) -> None:
        pass

    async def process_presence(self, element: Element) -> None:
        pass
```
