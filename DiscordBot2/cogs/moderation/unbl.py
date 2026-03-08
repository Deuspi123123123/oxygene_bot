import discord
from discord.ext import commands
from cogs.utils.permissions import require_permission
from database import (
    get_blacklist,
    remove_blacklist,
    add_sanction,
    deactivate_ban,
    remove_founder_bl
)
import sqlite3

FONDATEUR = "Fondateur"
UNIVERSE = "Universe"


class UnBlacklist(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @require_permission("unbl", roles=[UNIVERSE, FONDATEUR])
    async def unbl(self, ctx, user_id: int, *, reason="Non précisé"):

        data = get_blacklist(user_id)

        if not data:
            return await ctx.send("Cet utilisateur n'est pas blacklist.")

        added_by, bl_reason, timestamp, founder_count = data
        roles = [r.name for r in ctx.author.roles]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM founder_bl WHERE user_id=? AND founder_id=?",
            (user_id, ctx.author.id)
        )

        has_validation = cursor.fetchone()
        conn.close()

        # Cas blacklist Fondateur
        if founder_count > 0:

            if not has_validation:
                return await ctx.send(
                    "Impossible. Cette blacklist a été posée par un autre Fondateur."
                )

            # Cas 2 fondateurs
            if founder_count > 1:

                conn = sqlite3.connect("database.db")
                cursor = conn.cursor()

                new_count = founder_count - 1

                cursor.execute(
                    "UPDATE blacklist SET founder_count=? WHERE user_id=?",
                    (new_count, user_id)
                )

                conn.commit()
                conn.close()

                remove_founder_bl(user_id, ctx.author.id)

                embed = discord.Embed(
                    title="Retrait partiel de blacklist",
                    color=discord.Color.orange()
                )

                embed.add_field(
                    name="Utilisateur",
                    value=f"<@{user_id}> ({user_id})",
                    inline=False
                )

                embed.add_field(
                    name="Statut",
                    value=f"Blacklist Fondateur {new_count}/2",
                    inline=False
                )

                embed.add_field(
                    name="Modérateur",
                    value=ctx.author.mention,
                    inline=False
                )

                embed.timestamp = discord.utils.utcnow()

                await ctx.send(embed=embed)

                logs = self.bot.get_cog("Logs")
                if logs:
                    await logs.send_log(ctx.guild, "mod_logs", embed)

                return

            # Cas 1 seul fondateur
            remove_blacklist(user_id)
            remove_founder_bl(user_id, ctx.author.id)

        else:
            # blacklist normale
            remove_blacklist(user_id)

        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=reason)
        except:
            pass

        deactivate_ban(ctx.guild.id, user_id)
        add_sanction(user_id, ctx.author.id, "UNBLACKLIST", reason)

        embed = discord.Embed(
            title="Blacklist retirée",
            color=discord.Color.green()
        )

        embed.add_field(
            name="Utilisateur",
            value=f"<@{user_id}> ({user_id})",
            inline=False
        )

        embed.add_field(
            name="Modérateur",
            value=ctx.author.mention,
            inline=True
        )

        embed.add_field(
            name="Motif",
            value=reason,
            inline=True
        )

        embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)

        logs = self.bot.get_cog("Logs")
        if logs:
            await logs.send_log(ctx.guild, "mod_logs", embed)


async def setup(bot):
    await bot.add_cog(UnBlacklist(bot))