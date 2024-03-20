# Valorant.py
Valorant.py is a Valorant API wrapper covering most of the "hidden" API.

Show your current Valorant daily store
````py
from valorant import Valorant

player = Valorant("YourUserName", "YourPassword")

for skin in player.get_daily_skins():
    print(skin.name, skin.image, skin.price, sep="\n")
````