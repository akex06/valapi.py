# ValAPI.py

ValAPI.py is a Valorant API wrapper and XMPP client.


## Examples
### Getting your player ID
```py
from valorant import Valorant


player = Valorant("Lorem", "Ipsum")
player_id = player.user_info.player_id
print(f"Your player ID is {player_id}")
```

###
### Implementing your own XMPP

```py
import asyncio
from valorant import XMPP
from xml.etree.ElementTree import Element


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


async def main():
    xmpp_client = MyCustomXMPPClient("Lorem", "Ipsum")
    await xmpp_client.connect()
    await xmpp_client.start_auth_flow()
    await xmpp_client.process_messages()
    
asyncio.run(main())
```
