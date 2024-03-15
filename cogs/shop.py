import discord
from discord.ext import commands

from src import Valorant


class Shop(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def shop(self, ctx: commands.Context):
        val = Valorant("pitosexo69", "#Test12345")

        embeds = list()
        for skin in val.get_daily_skins():
            embed = discord.Embed(description=f"Price {skin.price}")
            embed.set_author(name=skin.name)
            embed.set_image(url=skin.image)
            embeds.append(embed)

        await ctx.send(embeds=embeds)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Shop(bot))
