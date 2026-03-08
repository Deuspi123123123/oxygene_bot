import discord
from discord.ext import commands

FONDATEUR = "Fondateur"


class RolesList(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roles(self, ctx):

        if not any(r.name == FONDATEUR for r in ctx.author.roles):
            return await ctx.send("Accès refusé.")

        roles = ctx.guild.roles

        names = []

        for role in roles:

            if role.name == "@everyone":
                continue

            names.append(role.name)

        text = "\n".join(names)

        if len(text) > 1900:
            await ctx.send("Trop de rôles pour un seul message.")
            return

        embed = discord.Embed(
            title="Liste des rôles du serveur",
            description=text,
            color=discord.Color.blurple()
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(RolesList(bot))