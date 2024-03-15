import os

import discord
from discord.ext import commands


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def on_ready(self) -> None:
        print(f"[ READY ]: {self.user}")

    async def setup_hook(self) -> None:
        for cog in os.listdir("cogs"):
            if not cog.endswith(".py"):
                continue

            await self.load_extension(f"cogs.{cog[:-3]}")


if __name__ == "__main__":
    bot = Bot(command_prefix="..", intents=discord.Intents.all())
    bot.run("MTIwMzA5MzA1MzEwODEzMzkzOA.Gz4PeH.UhW_IUNpH-7vJcyYKdC3J9gr9QWAODkfV-ZfnY")
