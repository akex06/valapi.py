from discord.ext import commands
from bot import Bot


class Linker(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="link",
        description="Link your valorant account with Discord using the OTP code"
    )
    @commands.dm_only()
    async def link(self, ctx: commands.Context, code: int) -> None:
        player_id = self.bot.database.is_code_valid(code)
        if player_id is None:
            await ctx.reply("The code provided is not valid")
            return

        try:
            self.bot.database.add_account_link(player_id, ctx.author.id)
            self.bot.database.delete_code(player_id)
            await ctx.reply(
                "Account linked successfully, use `vsetchannel` to set the channel to send the live match data")
        except ValueError:
            await ctx.reply("The account link already exists, update it or delete it.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Linker(bot))
