import discord
from discord.ext import commands
import time
from database import has_custom_permission

FONDATEUR = "Fondateur"
GALAXY = "Galaxy"
UNIVERSE = "Universe"

# rôles esthétiques basiques
PALESTINE = "| 𝐏𝐚𝐥𝐞𝐬𝐭𝐢𝐧𝐞 尉"
SPACE = "| ᦓρꪖᥴꫀ ぢ"
FREE = "| Free ぢ"

# rôles esthétiques +
LEVEL1 = "레벨 I"
LEVEL2 = "레벨 II"
LEVEL3 = "레벨 III"

# cooldown
COOLDOWN = 300
LIMIT = 2

usage = {}


class UHQ(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def has_access(self, member):

        roles = [r.name for r in member.roles]

        if FONDATEUR in roles:
            return True

        if GALAXY in roles:
            return True

        if UNIVERSE in roles:
            return True

        if has_custom_permission(member.id, "uhq"):
            return True

        return False

    def check_limit(self, user_id):

        now = time.time()

        if user_id not in usage:
            usage[user_id] = [1, now]
            return True, 0

        count, ts = usage[user_id]

        if now - ts > COOLDOWN:
            usage[user_id] = [1, now]
            return True, 0

        if count >= LIMIT:
            remaining = int(COOLDOWN - (now - ts))
            return False, remaining

        usage[user_id][0] += 1
        return True, 0

    @commands.command()
    async def uhq(self, ctx):

        if not self.has_access(ctx.author):
            return await ctx.send("Permission refusée.")

        allowed, remaining = self.check_limit(ctx.author.id)

        if not allowed:
            return await ctx.send(f"Limite atteinte. Réessaie dans {remaining}s.")

        guild = ctx.guild
        member = ctx.author

        palestine = discord.utils.get(guild.roles, name=PALESTINE)
        space = discord.utils.get(guild.roles, name=SPACE)
        free = discord.utils.get(guild.roles, name=FREE)

        lvl1 = discord.utils.get(guild.roles, name=LEVEL1)
        lvl2 = discord.utils.get(guild.roles, name=LEVEL2)
        lvl3 = discord.utils.get(guild.roles, name=LEVEL3)

        before_role = None
        after_role = None

        if palestine in member.roles:

            before_role = PALESTINE
            after_role = LEVEL1

            await member.remove_roles(palestine)
            await member.add_roles(lvl1)

        elif lvl1 in member.roles:

            before_role = LEVEL1
            after_role = PALESTINE

            await member.remove_roles(lvl1)
            await member.add_roles(palestine)

        elif space in member.roles:

            before_role = SPACE
            after_role = LEVEL2

            await member.remove_roles(space)
            await member.add_roles(lvl2)

        elif lvl2 in member.roles:

            before_role = LEVEL2
            after_role = SPACE

            await member.remove_roles(lvl2)
            await member.add_roles(space)

        elif free in member.roles:

            before_role = FREE
            after_role = LEVEL3

            await member.remove_roles(free)
            await member.add_roles(lvl3)

        elif lvl3 in member.roles:

            before_role = LEVEL3
            after_role = FREE

            await member.remove_roles(lvl3)
            await member.add_roles(free)

        else:
            return await ctx.send("Aucun rôle compatible.")

        embed = discord.Embed(
            title="UHQ activé",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Utilisateur",
            value=f"{member.mention} ({member.id})",
            inline=False
        )

        embed.add_field(
            name="Ancien rôle",
            value=before_role,
            inline=True
        )

        embed.add_field(
            name="Nouveau rôle",
            value=after_role,
            inline=True
        )

        embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)

        logs = self.bot.get_cog("Logs")

        if logs:
            await logs.send_log(ctx.guild, "role_logs", embed)


async def setup(bot):
    await bot.add_cog(UHQ(bot))