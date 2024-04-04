import msgspec.json
import requests

from valorant import Valorant
from valorant.structs.agent import AgentResponse

valorant = Valorant("pitosexo69", "#Test12345")

a = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true").content

print(msgspec.json.decode(a, type=AgentResponse))
