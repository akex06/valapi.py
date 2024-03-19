import discord
from discord import app_commands
from discord.ext import commands

from valostore import Valorant


class Shop(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="shop",
        description="Check your shop"
    )
    async def shop(self, interaction: discord.Interaction, user: str, password: str) -> None:
        await interaction.response.send_message("Espera un momento")

        val = Valorant(user, password)
        try:
            val.auth()
        except ValueError:
            msg = await self.bot.wait_for("message", check=lambda message: message.author == interaction.user)
            val.auth(msg.content)
        skins = val.get_daily_skins()

        embeds = list()
        for skin in skins:
            embed = discord.Embed(description=f"Price {skin.price}")
            embed.set_author(name=skin.name)
            embed.set_image(url=skin.image)
            embeds.append(embed)

        await interaction.channel.send(embeds=embeds)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Shop(bot))
