import discord
from discord.ext import commands
from database import add_custom_permission, remove_custom_permission

FONDATEUR = "Fondateur"


class CustomCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def is_fonda(self, member):
        return any(r.name == FONDATEUR for r in member.roles)

    @commands.command()
    async def addcom(self, ctx, member: discord.Member, command_name: str):

        if not self.is_fonda(ctx.author):
            return

        add_custom_permission(member.id, command_name)

        await ctx.send(f"Commande `{command_name}` ajoutée à {member.mention}.")

    @commands.command()
    async def delcom(self, ctx, member: discord.Member, command_name: str):

        if not self.is_fonda(ctx.author):
            return

        remove_custom_permission(member.id, command_name)

        await ctx.send(f"Commande `{command_name}` retirée à {member.mention}.")


async def setup(bot):
    await bot.add_cog(CustomCommands(bot))