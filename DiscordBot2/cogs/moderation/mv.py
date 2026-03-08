import discord
from discord.ext import commands

class Move(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def mv(self, ctx, user_id: int):

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(
                "Tu dois être dans un salon vocal pour utiliser cette commande."
            )

        try:
            member = await ctx.guild.fetch_member(user_id)
        except:
            return await ctx.send("Utilisateur introuvable.")

        if not member.voice or not member.voice.channel:
            return await ctx.send("Cette personne n'est pas dans un salon vocal.")

        channel = ctx.author.voice.channel

        await member.move_to(channel)

        embed = discord.Embed(
            description=f"{member.mention} a été déplacé dans {channel.mention}",
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Move(bot))