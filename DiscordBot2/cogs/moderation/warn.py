import discord
from discord.ext import commands
import time
import datetime

warns = {}

class Warn(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    def update_warns(self, user_id):

        now = time.time()

        if user_id not in warns:
            warns[user_id] = {"count":0,"time":now}
            return warns[user_id]["count"]

        data = warns[user_id]

        days = int((now - data["time"]) / 86400)

        if days > 0:

            data["count"] = max(0, data["count"] - days)

            data["time"] = now

        return data["count"]


    async def add_warn(self, member):

        count = self.update_warns(member.id)

        warns[member.id]["count"] += 1

        warns[member.id]["time"] = time.time()

        return warns[member.id]["count"]


    @commands.command()
    async def warn(self, ctx, member: discord.Member, *, reason):

        limits = self.bot.get_cog("LimitsCom")

        if limits:
            if not await limits.handle(ctx,"warn"):
                return

        count = await self.add_warn(member)

        embed = discord.Embed(
            title="Warn",
            description=f"{member.mention} a reçu un avertissement\nRaison : {reason}",
            color=discord.Color.orange()
        )

        embed.add_field(name="Total warns", value=count)

        await ctx.send(embed=embed)

        if count >= 3:

            await member.timeout(
                discord.utils.utcnow() + datetime.timedelta(days=1),
                reason="3 warns"
            )

            await ctx.send(f"{member.mention} a reçu un timeout de 1 jour.")


    @commands.command()
    async def unwarn(self, ctx, member: discord.Member):

        if member.id not in warns:
            return await ctx.send("Cette personne n'a aucun warn.")

        warns[member.id]["count"] = max(0, warns[member.id]["count"] - 1)

        await ctx.send(f"Un warn retiré. Total : {warns[member.id]['count']}")


    @commands.command()
    async def warns(self, ctx, member: discord.Member):

        count = self.update_warns(member.id)

        await ctx.send(f"{member.mention} possède {count} warns.")


async def setup(bot):
    await bot.add_cog(Warn(bot))