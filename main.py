import requests


agents = requests.get("https://valorant-api.com/v1/agents").json()["data"]
for agent in agents:
    print(agent)
    break