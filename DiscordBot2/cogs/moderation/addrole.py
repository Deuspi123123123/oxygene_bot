import discord
from discord.ext import commands
from discord import AuditLogAction

FONDATEUR = 1478165503984926771


# rôles contribution
CONTRIBUTION_ROLES = [
1479193092669050891, # ☄️
1479192607497130126, # 🌑
1479192859646234756, # ☀️
1478166498437496933, # Saturne
1478166348659036281, # ECLIPSE
1479194975706284153, # Crown
1479834901619544125, # blackhole
1479195106237219048, # ADMIN
1479203075775266957, # BOT
1479194811201355830, # WORLD
1478166242593472514  # Créateur
]


# esthétique basique
AESTHETIC_BASIC = {
1479193092669050891:1479695869925396552,
1479192607497130126:1479695869925396552,
1479192859646234756:1479695869925396552,

1478166498437496933:1479696383291162786,
1478166348659036281:1479696383291162786,
1479194975706284153:1479696383291162786,
1479834901619544125:1479696383291162786,

1479195106237219048:1479696980484821063,
1479203075775266957:1479696980484821063,
1479194811201355830:1479696980484821063,
1478166242593472514:1479696980484821063
}


BASIC_ROLES = [
1479695869925396552,
1479696383291162786,
1479696980484821063
]


PLUS_ROLES = [
1479570974943875072,
1479696980547473558,
1479697876773896212
]


class AddRole(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    def is_fondateur(self, member):
        return any(r.id == FONDATEUR for r in member.roles)


    @commands.command()
    async def addrole(self, ctx, member: discord.Member, role: discord.Role):

        if not self.is_fondateur(ctx.author):
            await ctx.send("Accès refusé.")
            return

        if role.is_default():
            await ctx.send("Rôle invalide.")
            return

        if role >= ctx.guild.me.top_role:
            await ctx.send("Je ne peux pas donner ce rôle.")
            return

        await member.add_roles(role)

        embed = discord.Embed(
            title="Rôle ajouté",
            color=discord.Color.green()
        )

        embed.add_field(
            name="Utilisateur",
            value=f"{member.mention} ({member.id})",
            inline=False
        )

        embed.add_field(
            name="Rôle",
            value=role.mention,
            inline=False
        )

        embed.add_field(
            name="Fondateur",
            value=ctx.author.mention,
            inline=False
        )

        embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)

        logs = self.bot.get_cog("Logs")

        if logs:
            await logs.send_log(ctx.guild,"role_logs",embed)


    @commands.Cog.listener()
    async def on_member_update(self,before,after):

        if before.roles == after.roles:
            return

        guild = after.guild
        executor = None

        async for entry in guild.audit_logs(limit=5):

            if entry.action == AuditLogAction.member_role_update:

                if entry.target and entry.target.id == after.id:
                    executor = entry.user
                    break


        logs = self.bot.get_cog("Logs")

        added_roles = [r for r in after.roles if r not in before.roles]
        removed_roles = [r for r in before.roles if r not in after.roles]


        for role in added_roles:

            if logs:

                embed = discord.Embed(
                    title="Rôle ajouté",
                    color=discord.Color.green()
                )

                embed.add_field(
                    name="Utilisateur",
                    value=f"{after.mention} ({after.id})",
                    inline=False
                )

                embed.add_field(
                    name="Rôle",
                    value=role.mention,
                    inline=False
                )

                embed.add_field(
                    name="Ajouté par",
                    value=executor.mention if executor else "Inconnu",
                    inline=False
                )

                embed.timestamp = discord.utils.utcnow()

                await logs.send_log(after.guild,"role_logs",embed)


        for role in removed_roles:

            if logs:

                embed = discord.Embed(
                    title="Rôle retiré",
                    color=discord.Color.red()
                )

                embed.add_field(
                    name="Utilisateur",
                    value=f"{after.mention} ({after.id})",
                    inline=False
                )

                embed.add_field(
                    name="Rôle",
                    value=role.mention,
                    inline=False
                )

                embed.add_field(
                    name="Retiré par",
                    value=executor.mention if executor else "Inconnu",
                    inline=False
                )

                embed.timestamp = discord.utils.utcnow()

                await logs.send_log(after.guild,"role_logs",embed)


        for role in added_roles:

            if role.id in CONTRIBUTION_ROLES:

                for r in after.roles:

                    if r.id in CONTRIBUTION_ROLES and r.id != role.id:
                        await after.remove_roles(r)

                for r in after.roles:

                    if r.id in BASIC_ROLES:
                        await after.remove_roles(r)

                aesthetic_id = AESTHETIC_BASIC.get(role.id)

                aesthetic = guild.get_role(aesthetic_id)

                if aesthetic:
                    await after.add_roles(aesthetic)


            if role.id in PLUS_ROLES:

                for r in after.roles:

                    if r.id in BASIC_ROLES:
                        await after.remove_roles(r)


async def setup(bot):
    await bot.add_cog(AddRole(bot))