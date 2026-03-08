from discord.ext import commands
import discord
from database import add_sanction, get_sanctions, deactivate_ban

class Unban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def unban(self, ctx, user_id: int, *, reason=None):

        sanctions = get_sanctions(user_id)

        if sanctions:
            last = sanctions[-1]
            _, s_type, _, mod_id = last

            mod = ctx.guild.get_member(mod_id)
            if mod and ctx.author.top_role < mod.top_role:
                await ctx.send("Impossible. Ban provenant d’un rôle supérieur.")
                return

        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user, reason=reason)

        deactivate_ban(ctx.guild.id, user_id)

        add_sanction(user_id, ctx.author.id, "UNBAN", reason)

        embed = discord.Embed(
            title="Déban",
            color=discord.Color.green()
        )

        embed.add_field(
            name="Utilisateur",
            value=f"{user.mention} ({user.id})",
            inline=False
        )

        embed.add_field(
            name="Modérateur",
            value=f"{ctx.author.mention} ({ctx.author.id})",
            inline=False
        )

        embed.add_field(
            name="Motif",
            value=reason or "Non précisé",
            inline=False
        )

        date = discord.utils.utcnow().strftime("%d/%m/%Y %H:%M UTC")

        embed.add_field(
            name="Date",
            value=date,
            inline=False
        )

        embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)

        logs = self.bot.get_cog("Logs")
        if logs:
            await logs.send_log(ctx.guild, "mod_logs", embed)

async def setup(bot):
    await bot.add_cog(Unban(bot))