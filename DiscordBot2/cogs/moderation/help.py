import discord
from discord.ext import commands

FONDATEUR = "Fondateur"
UNIVERSE = "Universe"
CREATEUR = "Créateur"
MAGISTRAL = "Magistral"
ROYAL = "Royal"


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def has_role(self, member, roles):
        return any(r.name == role for r in member.roles for role in roles)

    @commands.command()
    async def help(self, ctx):

        embed = discord.Embed(
            title="📖 Centre d'aide",
            color=discord.Color.blurple()
        )

        # 🔨 Modération
        if self.has_role(ctx.author, [CREATEUR, UNIVERSE, FONDATEUR]):
            embed.add_field(
                name="🔨 Modération",
                value="`=ban` `=baninfo` `=unban`",
                inline=False
            )

        # 🚫 Blacklist
        if self.has_role(ctx.author, [UNIVERSE, FONDATEUR]):
            embed.add_field(
                name="🚫 Blacklist",
                value="`=bl` `=unbl` `=blinfo` `=listbl`",
                inline=False
            )

        # 📜 Sanctions
        if self.has_role(ctx.author, [ROYAL, MAGISTRAL, CREATEUR, UNIVERSE, FONDATEUR]):
            embed.add_field(
                name="📜 Sanctions",
                value="`=sanction` `=delsanction` `=delsanctionall` `=clear` `=find`",
                inline=False
            )

        # ⏱ Timeout
        if self.has_role(ctx.author, [ROYAL, MAGISTRAL, CREATEUR, UNIVERSE, FONDATEUR]):
            embed.add_field(
                name="⏱ Timeout",
                value="`/to` `/unto` `=tempmute`",
                inline=False
            )

        # 💧 Wet system
        if self.has_role(ctx.author, [ROYAL, MAGISTRAL, CREATEUR, UNIVERSE, FONDATEUR]):
            embed.add_field(
                name="💧 Wet",
                value="`/wet` `/unwet`",
                inline=False
            )

        # ⭐ Ranks
        if self.has_role(ctx.author, [ROYAL, MAGISTRAL, CREATEUR]):
            embed.add_field(
                name="⭐ Ranks",
                value="`/rankup` `/rankdown` `/delrole`",
                inline=False
            )

        if self.has_role(ctx.author, [CREATEUR]):
            embed.add_field(
                name="⭐ Gestion Rank",
                value="`/rank`",
                inline=False
            )

        # 👑 Gestion staff
        if self.has_role(ctx.author, [FONDATEUR]):
            embed.add_field(
                name="👑 Gestion Staff",
                value="`/addrole` `=addcom` `=delcom`",
                inline=False
            )

        # 📂 Logs
        if self.has_role(ctx.author, [FONDATEUR]):
            embed.add_field(
                name="📂 Logs",
                value="`=setmodlogs` `=setvoclogs` `=setrolelogs`",
                inline=False
            )

        # 📊 Informations commandes
        if self.has_role(ctx.author, [FONDATEUR]):
            embed.add_field(
                name="📊 Informations",
                value="`=cominfo`",
                inline=False
            )

        if len(embed.fields) == 0:
            embed.description = "Aucune commande disponible."

        embed.set_footer(text=f"Serveur : {ctx.guild.name}")
        embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Help(bot))