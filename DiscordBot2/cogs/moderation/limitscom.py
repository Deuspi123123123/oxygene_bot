import discord
from discord.ext import commands
import time

WINDOWS = {
"warn":3600,
"mv":900,
"ban":3600,
"clear":1200,
"delsanction":900,
"unblr":1800,
"addemoji":3600
}

LIMITS = {

"warn":{
1478166348659036281:15,
1479194975706284153:15,
1479834901619544125:15,
1479195106237219048:15,
1479194811201355830:15,
1478165959973015726:15,
1478165503984926771:15,
1478166242593472514:15
},

"mv":{
1479194975706284153:3,
1479834901619544125:4,
1479195106237219048:6,
1479194811201355830:6
},

"ban":{
1479834901619544125:3,
1479194811201355830:5,
1478165959973015726:5,
1478165503984926771:5,
1478166242593472514:5
},

"clear":{
1479195106237219048:2,
1479194811201355830:2
},

"delsanction":{
1479194975706284153:2,
1479834901619544125:2,
1479195106237219048:2
},

"unblr":{
1479195106237219048:5,
1479194811201355830:5
},

"addemoji":{
1479203075775266957:1
}

}

usage = {}


class LimitsCom(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    def get_limit(self, member, command):

        best = 0

        for role in member.roles:

            if role.id in LIMITS.get(command, {}):
                best = max(best, LIMITS[command][role.id])

        return best


    def check(self, user_id, command, limit):

        window = WINDOWS[command]
        now = time.time()
        key = (user_id, command)

        if key not in usage:
            usage[key] = [1, now]
            return True, 0

        count, ts = usage[key]

        if now - ts > window:
            usage[key] = [1, now]
            return True, 0

        if count >= limit:
            remaining = int(window - (now - ts))
            return False, remaining

        usage[key][0] += 1
        return True, 0


    async def handle(self, ctx, command):

        limit = self.get_limit(ctx.author, command)

        if limit == 0:
            return True

        allowed, remaining = self.check(ctx.author.id, command, limit)

        if allowed:
            return True

        try:
            await ctx.message.delete()
        except:
            pass

        msg = await ctx.send(
            f"Limite atteinte. Réessaie dans {remaining}s."
        )

        await msg.delete(delay=5)

        return False


async def setup(bot):
    await bot.add_cog(LimitsCom(bot))