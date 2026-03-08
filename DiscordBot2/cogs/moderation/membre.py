import discord
from discord.ext import commands

FONDATEUR = "Fondateur"
ROLE_NAME = "👣 | Membre"


class MassMembre(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def massmembre(self, ctx):

        if not any(r.name == FONDATEUR for r in ctx.author.roles):
            return await ctx.send("Accès refusé.")

        role = discord.utils.get(ctx.guild.roles, name=ROLE_NAME)

        if role is None:
            return await ctx.send("Rôle introuvable.")

        count = 0

        for member in ctx.guild.members:

            if member.bot:
                continue

            if role in member.roles:
                continue

            try:
                await member.add_roles(role)
                count += 1
            except Exception:
                pass

        await ctx.send(f"Rôle donné à {count} membres.")


async def setup(bot):
    await bot.add_cog(MassMembre(bot))