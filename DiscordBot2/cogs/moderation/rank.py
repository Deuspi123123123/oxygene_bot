import discord
from discord.ext import commands
from discord import app_commands
import asyncio



OXY_ROLE_ID = 1479031485431545887
MOD_ROLE_ID = 1479930398585782453

RANKS = [
(1478864305129652486,1478865837396852837),
(1478864424893681694,1478867068559298612),
(1478864665013522513,1479030695190859776),
(1478864736979390484,1479031903477563445),
(1479033923936981002,1479034267542753350),
(1479034033236213841,1479034365299392522),
(1479034109798912020,1479034466377924648)
]

RANK_CHOICES = [
app_commands.Choice(name="💫 | Vœu",value=6),
app_commands.Choice(name="✨ | Constellation",value=5),
app_commands.Choice(name="🌙 | Croissant de lune",value=4),
app_commands.Choice(name="💐 | Fleures",value=3),
app_commands.Choice(name="🌱 | Vie",value=2),
app_commands.Choice(name="🌨️ | Neige",value=1),
app_commands.Choice(name="🌪️ | Tempête",value=0)
]

MULT = [
app_commands.Choice(name="x1",value=1),
app_commands.Choice(name="x2",value=2),
app_commands.Choice(name="x3",value=3)
]

CONTRI_LIMIT = {
1479192859646234756:2,
1478166498437496933:2,
1478166348659036281:5,
1479194975706284153:6,
1479834901619544125:6,
1479195106237219048:6,
1479194811201355830:6,
1478165959973015726:999,
1478165503984926771:999,
1478166242593472514:999
}

DERANK_ALLOWED = [
1479192859646234756,
1478166498437496933,
1478166348659036281,
1479834901619544125,
1479195106237219048,
1479194811201355830,
1478165959973015726,
1478165503984926771,
1478166242593472514
]


class Rank(commands.Cog):

    def __init__(self,bot):
        self.bot=bot


    def get_rank_index(self,member):

        for i,(perm_id,style_id) in enumerate(RANKS):

            if any(r.id==perm_id for r in member.roles):
                return i

            if any(r.id==style_id for r in member.roles):
                return i

        return None


    def get_limit(self,member):

        best = -1

        for role in member.roles:

            if role.id in CONTRI_LIMIT:

                best = max(best, CONTRI_LIMIT[role.id])

        if best == -1:
            return None

        return best


    async def clear_ranks(self,guild,member):

        for perm_id,style_id in RANKS:

            role_perm=guild.get_role(perm_id)
            role_style=guild.get_role(style_id)

            if role_perm and role_perm in member.roles:
                await member.remove_roles(role_perm)

            if role_style and role_style in member.roles:
                await member.remove_roles(role_style)


    async def apply_rank(self,guild,member,index):

        await self.clear_ranks(guild,member)

        perm_id,style_id = RANKS[index]

        role_perm = guild.get_role(perm_id)
        role_style = guild.get_role(style_id)

        if role_perm:
            await member.add_roles(role_perm)

        if role_style:
            await member.add_roles(role_style)

        oxy_role = guild.get_role(OXY_ROLE_ID)
        mod_role = guild.get_role(MOD_ROLE_ID)

        if index <= 3:

            if oxy_role and oxy_role not in member.roles:
                await member.add_roles(oxy_role)

            if mod_role and mod_role in member.roles:
                await member.remove_roles(mod_role)

        else:

            if mod_role and mod_role not in member.roles:
                await member.add_roles(mod_role)

            if oxy_role and oxy_role in member.roles:
                await member.remove_roles(oxy_role)

        return role_perm.name if role_perm else "Rank"


    async def log(self,interaction,action,member,before,after):

        logs=self.bot.get_cog("Logs")

        if not logs:
            return

        embed=discord.Embed(title="Rank Update",color=discord.Color.blurple())

        embed.add_field(name="Utilisateur",value=f"{member.mention} ({member.id})",inline=False)
        embed.add_field(name="Staff",value=f"{interaction.user.mention}",inline=False)
        embed.add_field(name="Action",value=action)
        embed.add_field(name="Avant",value=str(before))
        embed.add_field(name="Après",value=str(after))

        embed.timestamp=discord.utils.utcnow()

        await logs.send_log(interaction.guild,"role_logs",embed)


    @app_commands.command(name="rank")
    @app_commands.choices(rank=RANK_CHOICES)
    async def rank(self,interaction:discord.Interaction,member:discord.Member,rank:app_commands.Choice[int]):

        await interaction.response.defer()

        try:

            limit=self.get_limit(interaction.user)

            if limit is None:
                return await interaction.followup.send("Permission refusée.",ephemeral=True)

            if rank.value>limit:
                return await interaction.followup.send("Tu ne peux pas donner ce rank.",ephemeral=True)

            before=self.get_rank_index(member)

            perm=await self.apply_rank(interaction.guild,member,rank.value)

            msg=await interaction.followup.send(f"{member.mention} est maintenant **{perm}**")

            await self.log(interaction,"RANK",member,before,perm)

            await asyncio.sleep(5)
            await msg.delete()

        except Exception as e:

            await interaction.followup.send(f"Erreur : {e}",ephemeral=True)

    @app_commands.command(name="rankup")
    @app_commands.choices(multiplicateur=MULT)
    async def rankup(self,interaction:discord.Interaction,member:discord.Member,multiplicateur:app_commands.Choice[int]):

        await interaction.response.defer()

        limit=self.get_limit(interaction.user)

        if limit is None:
            return await interaction.followup.send("Permission refusée.",ephemeral=True)

        index=self.get_rank_index(member)

        if index is None:
            index=0
        else:
            index+=multiplicateur.value

        index=min(index,limit)

        before=self.get_rank_index(member)

        perm=await self.apply_rank(interaction.guild,member,index)

        msg=await interaction.followup.send(f"{member.mention} est maintenant **{perm}**")

        await self.log(interaction,"RANKUP",member,before,perm)

        await asyncio.sleep(5)
        await msg.delete()


    @app_commands.command(name="derank")
    @app_commands.choices(multiplicateur=MULT)
    async def derank(self,interaction:discord.Interaction,member:discord.Member,multiplicateur:app_commands.Choice[int]):

        await interaction.response.defer()

        if not any(r.id in DERANK_ALLOWED for r in interaction.user.roles):
            return await interaction.followup.send("Permission refusée.",ephemeral=True)

        index=self.get_rank_index(member)

        if index is None:
            return await interaction.followup.send("Aucun rank.",ephemeral=True)

        before=index

        index=max(index-multiplicateur.value,0)

        perm=await self.apply_rank(interaction.guild,member,index)

        msg=await interaction.followup.send(f"{member.mention} est maintenant **{perm}**")

        await self.log(interaction,"DERANK",member,before,perm)

        await asyncio.sleep(5)
        await msg.delete()


async def setup(bot):
    await bot.add_cog(Rank(bot))