import discord
from discord.ext import commands
import sqlite3

DB = "database.db"


class InviteTracker(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.invites = {}

    async def get_invites(self, guild):
        return await guild.invites()

    @commands.Cog.listener()
    async def on_ready(self):

        for guild in self.bot.guilds:
            self.invites[guild.id] = await self.get_invites(guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):

        guild = member.guild

        old_invites = self.invites.get(guild.id, [])
        new_invites = await self.get_invites(guild)

        used = None

        for invite in new_invites:
            for old in old_invites:
                if invite.code == old.code and invite.uses > old.uses:
                    used = invite
                    break

        self.invites[guild.id] = new_invites

        if not used:
            return

        inviter = used.inviter

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT OR IGNORE INTO invites(user_id,count) VALUES(?,0)",
            (inviter.id,)
        )

        cursor.execute(
            "UPDATE invites SET count=count+1 WHERE user_id=?",
            (inviter.id,)
        )

        conn.commit()
        conn.close()

        channel = discord.utils.get(guild.text_channels, name="invites")

        if channel:
            await channel.send(
                f"{member.mention} a rejoint via l'invitation de {inviter.mention}"
            )


    @commands.command()
    async def invites(self, ctx, member: discord.Member = None):

        member = member or ctx.author

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT count FROM invites WHERE user_id=?",
            (member.id,)
        )

        data = cursor.fetchone()
        conn.close()

        count = data[0] if data else 0

        embed = discord.Embed(
            description=f"{member.mention} a invité **{count}** membre(s)",
            color=discord.Color.blurple()
        )

        await ctx.send(embed=embed)


    @commands.command()
    async def topinvites(self, ctx):

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT user_id,count FROM invites ORDER BY count DESC LIMIT 10"
        )

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return await ctx.send("Aucune donnée.")

        text = ""

        for i,(uid,count) in enumerate(rows,1):
            user = ctx.guild.get_member(uid)
            name = user.mention if user else str(uid)
            text += f"{i}. {name} — {count} invitations\n"

        embed = discord.Embed(
            title="Classement des invitations",
            description=text,
            color=discord.Color.blurple()
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(InviteTracker(bot))