import asyncio
import base64
import json
import time
from io import BytesIO
from xml.etree.ElementTree import Element

import requests
from PIL import Image, ImageFont, ImageDraw

from database import Database
from valorant import Valorant
from valorant.constants import ranks
from valorant.xmpp import XMPP

emojis = {
    0: ("unranked", 1222269195560161302),
    3: ("iron_1", 1222269197862699141),
    4: ("iron_2", 1222269200618487878),
    5: ("iron_3", 1222269202883412052),
    6: ("bronze_1", 1222269205814968371),
    7: ("bronze_2", 1222269208453185537),
    8: ("bronze_3", 1222269211196260533),
    9: ("silver_1", 1222269213889134692),
    10: ("silver_2", 1222269216477151252),
    11: ("silver_3", 1222269218888614020),
    12: ("gold_1", 1222269221581623407),
    13: ("gold_2", 1222269224202928188),
    14: ("gold_3", 1222269226623176900),
    15: ("platinum_1", 1222269229408190636),
    16: ("platinum_2", 1222269231794622656),
    17: ("platinum_3", 1222269234420256798),
    18: ("diamond_1", 1222269238123823164),
    19: ("diamond_2", 1222269240829018273),
    20: ("diamond_3", 1222269247032659978),
    21: ("ascendant_1", 1222269249360498720),
    22: ("ascendant_2", 1222269252145516575),
    23: ("ascendant_3", 1222269254834061503),
    24: ("immortal_1", 1222269257254047905),
    25: ("immortal_2", 1222269259959373906),
    26: ("immortal_3", 1222269263788904719),
    27: ("radiant", 1222269267961970919)
}

BOT_TOKEN = ""


class Match:
    def __init__(
            self,
            val: Valorant,
            uuid: str,
            match_data: dict
    ) -> None:
        self.image_id = 1
        self.val = val
        self.player_id = uuid
        self.match_data = match_data

        self.ended = False

        self.score: tuple[int, int] = (
            match_data["partyOwnerMatchScoreAllyTeam"],
            match_data["partyOwnerMatchScoreEnemyTeam"]
        )

        self.discord_session = requests.Session()
        self.discord_session.headers.update({
            "Authorization": f"Bot {BOT_TOKEN}"
        })

        self.map = self.get_map()
        self.username, self.tagline = self.get_user()

        self.player_card = requests.get(
            f"https://valorant-api.com/v1/playercards/{match_data['playerCardId']}"
        ).json()["data"]

        self.thumbnail = self.get_thumbnail()

        self.channel_id = 1218009024159678667
        self.message_id = self.send_message()["id"]

    def get_payload(self, *, updating: bool = False) -> dict:
        ally_score, enemy_score = self.score
        if ally_score == enemy_score:
            match_status, color = "Tied", 0x808080
        elif ally_score > enemy_score:
            match_status, color = "Won" if self.ended else "Winning", 0x00FF48
        else:
            match_status, color = "Lost" if self.ended else "Loosing", 0xFF1919

        rank = ranks[self.match_data['competitiveTier']]
        emoji_data = emojis[rank.tier]
        rank_emoji = f"<:{emoji_data[0]}:{emoji_data[1]}>"

        message = {
            "embeds": [{
                "author": {
                    "name": f"{self.username}#{self.tagline} - {self.match_data['queueId'].title()} {self.score[0]}-{self.score[1]}",
                    "icon_url": self.player_card["displayIcon"]
                },
                "thumbnail": {
                    "url": "attachment://thumbnail.png"
                },
                "fields": [
                    {
                        "name": "Level",
                        "value": f"{self.match_data['accountLevel']}",
                        "inline": True
                    }, {
                        "name": "Rank",
                        "value": f"{rank.name.title()} {rank_emoji}",
                        "inline": True
                    }
                ],
                "color": color,
                "image": {
                    "url": "attachment://image.png"
                }
            }]
        }
        if updating:
            message["attachments"] = [{"id": 1}, {"id": 2}]

        return message

    def update(self, match_data: dict) -> bool:
        self.match_data = match_data
        total_score = self.match_data["partyOwnerMatchScoreAllyTeam"] + self.match_data["partyOwnerMatchScoreEnemyTeam"]

        if sum(self.score) > 0 and total_score == 0:
            self.ended = True
            return True

        self.score = self.match_data["partyOwnerMatchScoreAllyTeam"], self.match_data["partyOwnerMatchScoreEnemyTeam"]
        self.update_message()

        return False

    def send_message(self) -> dict:
        payload = self.get_payload()
        return self.discord_session.post(
            f"https://discord.com/api/v9/channels/{self.channel_id}/messages",
            files=[
                ("files[1]", ("image.png", self.get_match_image())),
                ("files[2]", ("thumbnail.png", self.get_thumbnail())),
                ("payload_json", ("", json.dumps(payload), "application/json"))
            ]
        ).json()

    def update_message(self) -> dict:
        return self.discord_session.patch(
            f"https://discord.com/api/v9/channels/{self.channel_id}/messages/{self.message_id}",
            files=[
                ("files[1]", ("image.png", self.get_match_image())),
                ("files[2]", ("thumbnail.png", self.get_thumbnail())),
                ("payload_json", ("", json.dumps(self.get_payload(updating=True)), "application/json"))
            ]
        ).json()

    def get_user(self) -> tuple[str, str]:
        user = self.val.session.put(
            "https://pd.eu.a.pvp.net/name-service/v2/players",
            headers={
                "X-Riot-Entitlements-JWT": self.val.auth.get_entitlement_token(),
                "Authorization": f"Bearer {self.val.auth.get_access_token()}"
            },
            json=[self.player_id, ]
        ).json()[0]
        return user["GameName"], user["TagLine"]

    def get_map(self) -> dict:
        return list(filter(
            lambda _map: _map["mapUrl"] == self.match_data["matchMap"],
            requests.get("https://valorant-api.com/v1/maps").json()["data"]
        ))[0]

    @staticmethod
    def image_to_buffer(image: Image) -> BytesIO:
        image_bytes = BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        return image_bytes

    def get_match_image(self) -> BytesIO:
        background = Image.open(BytesIO(requests.get(self.map["splash"]).content))
        background = background.crop((0, 100, background.width, background.height - 300))

        tungsten_font_large = ImageFont.truetype("resources/tungsten_bold.ttf", 300)
        tungsten_font_small = ImageFont.truetype("resources/tungsten_bold.ttf", 200)

        map_name = self.map["displayName"].upper()
        draw = ImageDraw.Draw(background)
        _, _, w, h = draw.textbbox((0, 0), map_name, font=tungsten_font_large)
        draw.text(
            (
                (background.width - w) // 2,
                100
            ),
            map_name,
            font=tungsten_font_large,
            fill=(255, 255, 255)
        )

        score_text = f"{self.score[0]}-{self.score[1]}"
        _, _, w, h = draw.textbbox((0, 0), score_text, font=tungsten_font_small)
        draw.text(
            (
                (background.width - w) // 2,
                400
            ),
            score_text,
            font=tungsten_font_small,
            fill=(255, 255, 255)
        )

        return self.image_to_buffer(background)

    def get_thumbnail(self) -> BytesIO:
        thumbnail = Image.open(BytesIO(requests.get(self.player_card["displayIcon"]).content))

        border_level = Image.open("resources/borderlevel.png")

        font = ImageFont.truetype("resources/din_next_regular.otf", 16)
        draw = ImageDraw.Draw(border_level)
        _, _, w, h = draw.textbbox((0, 0), str(self.match_data["accountLevel"]), font=font)
        draw.text(
            (
                (border_level.width - w) // 2,
                (border_level.height - h) // 2
            ),
            str(self.match_data["accountLevel"]),
            font=font
        )

        thumbnail.paste(border_level, ((thumbnail.width - border_level.width) // 2, 95), border_level)

        return self.image_to_buffer(thumbnail)


class DiscordXMPP(XMPP):
    def __init__(self, username: str, password: str) -> None:
        super().__init__(
            username,
            password
        )

        self.matches: dict[str, Match] = dict()
        self.database = Database()

    async def send_message(self, player_jid: str, message: str) -> None:
        await self.send(
            f'<message id="{time.time() * 1000}:1" to="{player_jid}" type="chat"><body>{message}</body></message>'
            .encode("utf-8")
        )

    async def process_presence(self, presence_element: Element) -> None:
        games = presence_element.find("games")
        if games is None:
            return

        game = games.find("valorant")
        if game is None:
            return

        match_data = json.loads(base64.b64decode(game.find("p").text + "==").decode("utf-8"))
        if match_data["sessionLoopState"] != "INGAME":
            return

        uuid = presence_element.get("from").split("@")[0]
        if uuid not in self.matches:
            if match_data["matchMap"] == "":
                return

            self.matches[uuid] = Match(self.val, uuid, match_data)
            return

        delete_match = self.matches[uuid].update(match_data)
        if delete_match:
            del self.matches[uuid]

    async def process_message(self, message_element: Element) -> None:
        await self.send_message(message_element.get("from").split("/")[0], "Hey!")

    async def process_iq(self, iq_element: Element) -> None:
        query = iq_element.find("{jabber:iq:riotgames:roster}query")
        if query is None:
            return

        item = query.find("{jabber:iq:riotgames:roster}item")
        subscription = item.get("subscription")

        uuid = iq_element.get("from").split("@")[0]
        if subscription == "pending_in":
            player = item.find("{jabber:iq:riotgames:roster}id")
            await self.add_friend(player.get("name"), player.get("tagline"))
            player_jid = item.get("jid")
            otp_code = self.database.set_otp_code(uuid)
            await self.send_message(
                player_jid,
                (
                    f"Hey there, your OTP code is {otp_code}, dm the code to Foo#Faa or use the /link command in my dms"
                    " to start the configuration, you can add the bot to your server, invite in"
                    " https://github.com/akex06/valorant.py"
                ))


async def main():
    xmpp = DiscordXMPP("pitosexo69", "#Test12345")

    await xmpp.connect()
    await xmpp.start_auth_flow()
    await xmpp.process_messages()


asyncio.run(main())
