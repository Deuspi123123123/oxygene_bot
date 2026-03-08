from discord.ext import commands
import discord

FONDATEUR = "Fondateur"

class ComInfo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def cominfo(self, ctx):

        if not any(r.name == FONDATEUR for r in ctx.author.roles):
            return await ctx.send("Accès refusé.")

        embed = discord.Embed(
            title="Rôles & Commandes",
            color=discord.Color.gold()
        )

        embed.add_field(
            name="Fondateur",
            value="Toutes les commandes",
            inline=False
        )

        embed.add_field(
            name="Universe",
            value="ban, bl, unbl, sanctions",
            inline=False
        )

        embed.add_field(
            name="Créateur",
            value="ban, sanctions",
            inline=False
        )

        embed.add_field(
            name="Magistral",
            value="sanctions",
            inline=False
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ComInfo(bot))