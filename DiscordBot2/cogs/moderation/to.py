import discord
from discord.ext import commands
from discord import app_commands
import datetime
import time
from database import add_sanction

MAGISTRAL = "Magistral"
CREATEUR = "Créateur"
UNIVERSE = "Universe"
FONDATEUR = "Fondateur"

COOLDOWN = 14400

timeout_limits = {}


def has_permission(member):
    roles = [r.name for r in member.roles]
    return any(r in roles for r in [MAGISTRAL, CREATEUR, UNIVERSE, FONDATEUR])


def get_limit(member):
    roles = [r.name for r in member.roles]

    if FONDATEUR in roles:
        return None

    if UNIVERSE in roles:
        return None

    if CREATEUR in roles:
        return 10

    if MAGISTRAL in roles:
        return 5

    return 0


def check_limit(user_id, limit):

    if limit is None:
        return True, 0

    now = time.time()

    if user_id not in timeout_limits:
        timeout_limits[user_id] = [1, now]
        return True, 0

    count, ts = timeout_limits[user_id]

    if now - ts > COOLDOWN:
        timeout_limits[user_id] = [1, now]
        return True, 0

    if count >= limit:
        remaining = int(COOLDOWN - (now - ts))
        return False, remaining

    timeout_limits[user_id][0] += 1
    return True, 0


class Timeout(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="to", description="Timeout un utilisateur")
    @app_commands.describe(
        member="Utilisateur à sanctionner",
        duration="Durée du timeout",
        reason="Raison du timeout"
    )
    @app_commands.choices(duration=[
        app_commands.Choice(name="1 minute", value=60),
        app_commands.Choice(name="5 minutes", value=300),
        app_commands.Choice(name="15 minutes", value=900),
        app_commands.Choice(name="30 minutes", value=1800),
        app_commands.Choice(name="1 heure", value=3600),
        app_commands.Choice(name="1 jour", value=86400),
        app_commands.Choice(name="1 semaine", value=604800)
    ])
    async def to(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        duration: app_commands.Choice[int],
        reason: str
    ):

        if not has_permission(interaction.user):
            return await interaction.response.send_message(
                "Permission insuffisante.",
                ephemeral=True
            )

        limit = get_limit(interaction.user)

        allowed, remaining = check_limit(interaction.user.id, limit)

        if not allowed:
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60

            return await interaction.response.send_message(
                f"Limite atteinte. Réessaye dans {hours}h {minutes}min.",
                ephemeral=True
            )

        seconds = duration.value

        await member.timeout(
            discord.utils.utcnow() + datetime.timedelta(seconds=seconds),
            reason=reason
        )

        add_sanction(
            member.id,
            interaction.user.id,
            "TIMEOUT",
            reason
        )

        embed = discord.Embed(
            title="Timeout appliqué",
            color=discord.Color.red()
        )

        embed.add_field(
            name="Utilisateur",
            value=f"{member.mention} ({member.id})",
            inline=False
        )

        embed.add_field(
            name="Durée",
            value=duration.name,
            inline=True
        )

        embed.add_field(
            name="Raison",
            value=reason,
            inline=True
        )

        embed.add_field(
            name="Modérateur",
            value=interaction.user.mention,
            inline=False
        )

        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

        logs = self.bot.get_cog("Logs")
        if logs:
            await logs.send_log(interaction.guild, "mod_logs", embed)


    @app_commands.command(name="unto", description="Retirer le timeout")
    @app_commands.describe(
        user_id="ID de l'utilisateur",
        reason="Raison du retrait"
    )
    async def unto(
        self,
        interaction: discord.Interaction,
        user_id: str,
        reason: str = "Timeout retiré"
    ):

        if not has_permission(interaction.user):
            return await interaction.response.send_message(
                "Permission insuffisante.",
                ephemeral=True
            )

        try:
            member = await interaction.guild.fetch_member(int(user_id))
        except:
            return await interaction.response.send_message(
                "Utilisateur introuvable.",
                ephemeral=True
            )

        await member.timeout(None, reason=reason)

        embed = discord.Embed(
            title="Timeout retiré",
            color=discord.Color.green()
        )

        embed.add_field(
            name="Utilisateur",
            value=f"{member.mention} ({member.id})",
            inline=False
        )

        embed.add_field(
            name="Modérateur",
            value=interaction.user.mention,
            inline=True
        )

        embed.add_field(
            name="Raison",
            value=reason,
            inline=True
        )

        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

        logs = self.bot.get_cog("Logs")
        if logs:
            await logs.send_log(interaction.guild, "mod_logs", embed)


async def setup(bot):
    await bot.add_cog(Timeout(bot))