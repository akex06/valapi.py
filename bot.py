import discord
from discord.ext import commands

from database import Database


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.database = Database()

    async def on_ready(self) -> None:
        print(f"[   READY   ]: {self.user}")

    async def setup_hook(self) -> None:
        await self.load_extension("cogs.linker")
        # await self.tree.sync()
        pass


if __name__ == "__main__":
    bot = Bot(command_prefix="v", intents=discord.Intents.all())
    bot.run("")
