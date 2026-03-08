import discord
from discord.ext import commands

FULL_DERANK_ALLOWED = [
1479194811201355830,
1478165959973015726,
1478165503984926771,
1478166242593472514
]

MEMBER_ROLE = 1479237313828618463

class FullDerank(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def derank(self,ctx,member:discord.Member):

        if not any(r.id in FULL_DERANK_ALLOWED for r in ctx.author.roles):
            return

        for role in member.roles:

            if role.id != ctx.guild.id:
                try:
                    await member.remove_roles(role)
                except:
                    pass

        mrole = ctx.guild.get_role(MEMBER_ROLE)

        if mrole:
            await member.add_roles(mrole)

        await ctx.message.delete()


async def setup(bot):
    await bot.add_cog(FullDerank(bot))