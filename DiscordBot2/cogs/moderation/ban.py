from discord.ext import commands
import discord
from database import add_sanction, add_ban_detail, get_active_ban
import sqlite3
import time
import datetime
from cogs.utils.permissions import require_permission

FONDATEUR = "Fondateur"
UNIVERSE = "Universe"
CREATEUR = "Créateur"

COOLDOWN = 43200


class Ban(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def check_limit(self, user_id, limit):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ban_limits(
            user_id INTEGER,
            count INTEGER,
            timestamp REAL
        )
        """)

        cursor.execute(
            "SELECT count, timestamp FROM ban_limits WHERE user_id=?",
            (user_id,)
        )

        data = cursor.fetchone()
        now = time.time()

        if not data:
            cursor.execute(
                "INSERT INTO ban_limits VALUES(?,?,?)",
                (user_id, 1, now)
            )
            conn.commit()
            conn.close()
            return True, 0

        count, ts = data

        if now - ts > COOLDOWN:
            cursor.execute(
                "UPDATE ban_limits SET count=?, timestamp=? WHERE user_id=?",
                (1, now, user_id)
            )
            conn.commit()
            conn.close()
            return True, 0

        if count >= limit:
            remaining = int(COOLDOWN - (now - ts))
            conn.close()
            return False, remaining

        cursor.execute(
            "UPDATE ban_limits SET count=count+1 WHERE user_id=?",
            (user_id,)
        )
        conn.commit()
        conn.close()
        return True, 0


    @commands.command()
    async def baninfo(self, ctx, user_id: int):

        try:
            await ctx.guild.fetch_ban(discord.Object(id=user_id))
        except discord.NotFound:
            return await ctx.send("La personne n'est pas bannie du serveur.")

        data = get_active_ban(ctx.guild.id, user_id)

        if not data:
            return await ctx.send("Aucune donnée active trouvée.")

        case_id, mod_id, reason, channel_id, ts = data

        mod = ctx.guild.get_member(mod_id)
        channel = ctx.guild.get_channel(channel_id)

        now = time.time()
        delta = int(now - ts)

        days = delta // 86400
        hours = (delta % 86400) // 3600
        minutes = (delta % 3600) // 60

        date = datetime.datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M:%S")

        embed = discord.Embed(
            title="Ban actif",
            color=discord.Color.orange()
        )

        embed.add_field(name="Utilisateur ID", value=str(user_id), inline=False)
        embed.add_field(
            name="Modérateur",
            value=mod.mention if mod else str(mod_id),
            inline=False
        )
        embed.add_field(
            name="Salon d'exécution",
            value=channel.mention if channel else "Inconnu",
            inline=False
        )
        embed.add_field(name="Raison", value=reason or "Non précisé", inline=False)
        embed.add_field(name="Date", value=date, inline=False)
        embed.add_field(
            name="Temps écoulé",
            value=f"{days}j {hours}h {minutes}m",
            inline=False
        )

        embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)


    @commands.command()
    @require_permission("ban", roles=[CREATEUR, UNIVERSE, FONDATEUR])
    async def ban(self, ctx, member: discord.Member, *, reason=None):

        if ctx.author.top_role <= member.top_role:
            return await ctx.send(
                "Impossible de bannir ce membre. Son rôle est égal ou supérieur au tien."
            )

        roles = [r.name for r in ctx.author.roles]

        if CREATEUR in roles:
            allowed, remaining = self.check_limit(ctx.author.id, 5)
            if not allowed:
                hours = remaining // 3600
                minutes = (remaining % 3600) // 60
                return await ctx.send(
                    f"Limite atteinte. Réessaye dans {hours}h {minutes}min."
                )

        if UNIVERSE in roles:
            allowed, remaining = self.check_limit(ctx.author.id, 15)
            if not allowed:
                hours = remaining // 3600
                minutes = (remaining % 3600) // 60
                return await ctx.send(
                    f"Limite atteinte. Réessaye dans {hours}h {minutes}min."
                )

        try:
            await member.ban(reason=reason)
        except Exception as e:
            return await ctx.send(f"Erreur lors du ban : {e}")

        add_sanction(member.id, ctx.author.id, "BAN", reason)

        embed = discord.Embed(
            title="Ban appliqué",
            color=discord.Color.red()
        )

        embed.add_field(
            name="Membre",
            value=f"{member.mention} ({member.id})",
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

        msg = await ctx.send(embed=embed)

        add_ban_detail(
            ctx.guild.id,
            member.id,
            ctx.author.id,
            reason,
            ctx.channel.id,
            msg.id
        )

        logs = self.bot.get_cog("Logs")
        if logs:
            await logs.send_log(ctx.guild, "mod_logs", embed)


async def setup(bot):
    await bot.add_cog(Ban(bot))