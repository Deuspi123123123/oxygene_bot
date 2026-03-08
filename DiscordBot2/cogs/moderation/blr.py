import discord
from discord.ext import commands

BLR_ROLE = "BLR"
FOUNDER = "Fondateur"

class BLR(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def blr(self, ctx, member: discord.Member):

        if not any(r.name == FOUNDER for r in ctx.author.roles):
            return await ctx.send("Accès refusé.")

        role = discord.utils.get(ctx.guild.roles, name=BLR_ROLE)

        if not role:
            return await ctx.send("Rôle BLR introuvable.")

        if role in member.roles:

            await member.remove_roles(role)

            embed = discord.Embed(
                description=f"{member.mention} n'est plus BLR",
                color=discord.Color.green()
            )

        else:

            await member.add_roles(role)

            embed = discord.Embed(
                description=f"{member.mention} est maintenant BLR",
                color=discord.Color.red()
            )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(BLR(bot))