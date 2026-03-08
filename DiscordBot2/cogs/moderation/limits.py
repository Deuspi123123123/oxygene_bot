import discord
from discord.ext import commands
from discord import AuditLogAction
import time

WINDOW_10M = 600
WINDOW_30M = 1800
WINDOW_90M = 5400
WINDOW_1H = 3600

CONTRI_LIMITS = {
1479192859646234756: {"move": (2, WINDOW_10M)},
1478166498437496933: {"move": (2, WINDOW_10M), "mute": (4, WINDOW_10M)},
1478166348659036281: {"move": (2, WINDOW_10M), "mute": (5, WINDOW_10M), "deaf": (5, WINDOW_10M)},
1479194975706284153: {"move": (2, WINDOW_10M), "mute": (5, WINDOW_10M), "deaf": (5, WINDOW_10M)},
1479834901619544125: {"move": (2, WINDOW_10M), "mute": (5, WINDOW_10M), "deaf": (5, WINDOW_10M), "disconnect": (5, WINDOW_10M), "timeout": (3, WINDOW_90M)},
1479195106237219048: {"move": (2, WINDOW_10M), "mute": (5, WINDOW_10M), "deaf": (5, WINDOW_10M), "disconnect": (5, WINDOW_10M), "timeout": (5, WINDOW_10M), "ban": (3, WINDOW_30M)},
1479194811201355830: {"all": (7, WINDOW_10M)},
1478165959973015726: {"all": (7, WINDOW_10M)},
1478165503984926771: {"all": (7, WINDOW_10M)},
1478166242593472514: {"all": (7, WINDOW_10M)}
}

actions = {}

class Limits(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def get_role_limits(self, member):

        final = {}

        for role in member.roles:

            if role.id in CONTRI_LIMITS:

                for action,data in CONTRI_LIMITS[role.id].items():

                    count,window = data

                    if action not in final:
                        final[action] = data
                    else:
                        final[action] = max(final[action], data, key=lambda x:x[0])

        return final

    def check(self,user_id,action,limit,window):

        now = time.time()

        key = (user_id,action)

        if key not in actions:
            actions[key] = [1,now]
            return True

        count,ts = actions[key]

        if now-ts > window:
            actions[key] = [1,now]
            return True

        if count >= limit:
            return False

        actions[key][0]+=1
        return True

    async def punish(self,guild,member):

        role = discord.utils.get(guild.roles,name="Membre")

        if role:
            await member.add_roles(role)

        try:
            await member.timeout(
                discord.utils.utcnow()+discord.timedelta(hours=1),
                reason="Tarte abus clic droit"
            )
        except:
            pass

        try:
            await member.send(
            "Tu as été tarté pour abus de clique droit, contacte ton supérieur pour rerank."
            )
        except:
            pass

    @commands.Cog.listener()
    async def on_member_update(self,before,after):

        guild = after.guild

        async for entry in guild.audit_logs(limit=1):

            if entry.action not in [
            AuditLogAction.member_move,
            AuditLogAction.member_disconnect,
            AuditLogAction.member_update
            ]:
                return

            executor = entry.user

            if executor.bot:
                return

            member = guild.get_member(executor.id)

            limits = self.get_role_limits(member)

            action = None

            if entry.action == AuditLogAction.member_move:
                action = "move"

            elif entry.action == AuditLogAction.member_disconnect:
                action = "disconnect"

            elif entry.action == AuditLogAction.member_update:

                if entry.before.mute != entry.after.mute:
                    action = "mute"

                if entry.before.deaf != entry.after.deaf:
                    action = "deaf"

                if entry.before.communication_disabled_until != entry.after.communication_disabled_until:
                    action = "timeout"

            if action is None:
                return

            if "all" in limits:
                limit,window = limits["all"]

            elif action in limits:
                limit,window = limits[action]

            else:
                return

            allowed = self.check(member.id,action,limit,window)

            if not allowed:

                await self.punish(guild,member)

            return

async def setup(bot):
    await bot.add_cog(Limits(bot))