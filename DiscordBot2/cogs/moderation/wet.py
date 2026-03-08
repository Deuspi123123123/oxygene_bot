import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import time
import asyncio
import random

from database import (
    has_custom_permission,
    add_sanction,
    remove_blacklist,
    deactivate_ban
)

FONDATEUR = "Fondateur"
WET_COOLDOWN = 604800

wet_limits = {}
return_attempts = {}


class Wet(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    def is_fonda(self, member):
        return any(r.name == FONDATEUR for r in member.roles)


    def has_permission(self, member):

        if self.is_fonda(member):
            return True

        if has_custom_permission(member.id, "wet"):
            return True

        return False


    def generate_ip(self):
        return ".".join(str(random.randint(1, 255)) for _ in range(4))


    def add_wet(self, user_id, author_id):

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS wet_users(
            user_id INTEGER PRIMARY KEY,
            author_id INTEGER,
            timestamp REAL
        )
        """)

        cursor.execute(
            "INSERT OR REPLACE INTO wet_users VALUES (?,?,?)",
            (user_id, author_id, time.time())
        )

        conn.commit()
        conn.close()


    def remove_wet(self, user_id):

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM wet_users WHERE user_id=?",
            (user_id,)
        )

        conn.commit()
        conn.close()


    def get_wet(self, user_id):

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT author_id FROM wet_users WHERE user_id=?",
            (user_id,)
        )

        data = cursor.fetchone()
        conn.close()

        return data


    @app_commands.command(name="wet", description="Exclusion définitive")
    async def wet(self, interaction: discord.Interaction, user: discord.Member):

        if not self.has_permission(interaction.user):
            return await interaction.response.send_message(
                "Permission insuffisante.",
                ephemeral=True
            )

        await interaction.response.defer()

        msg = await interaction.followup.send("Initialisation protocole WET...")

        await asyncio.sleep(1)
        await msg.edit(content="Collecte des adresses IP █░░░░")

        await asyncio.sleep(1)
        await msg.edit(content="Collecte des adresses IP ███░░")

        await asyncio.sleep(1)
        await msg.edit(content="Détection VPN / Proxy █████")

        await asyncio.sleep(1)

        fake_ip = self.generate_ip()

        await msg.edit(content=f"Adresse IP identifiée : `{fake_ip}`")

        await asyncio.sleep(1)

        self.add_wet(user.id, interaction.user.id)

        try:
            await user.send(
                "ACCÈS RÉVOQUÉ\n\n"
                "Ton accès au serveur est terminé.\n\n"
                "Si tu veux revenir il faudra contribuer.\n"
                "Contacte Deuspi.\n\n"
                "Sinon abandonne."
            )
        except:
            pass

        try:
            await user.kick(reason="WET sanction")
        except:
            pass

        embed = discord.Embed(
            title="💧 WET EXECUTÉ",
            description=f"{user.mention} est marqué WET.",
            color=discord.Color.dark_red()
        )

        embed.add_field(
            name="Utilisateur",
            value=f"{user} ({user.id})",
            inline=False
        )

        embed.add_field(
            name="Staff",
            value=interaction.user.mention,
            inline=False
        )

        embed.add_field(
            name="Salon",
            value=interaction.channel.mention,
            inline=False
        )

        embed.timestamp = discord.utils.utcnow()

        await interaction.followup.send(embed=embed)

        add_sanction(user.id, interaction.user.id, "WET", "Exclusion définitive")

        logs = self.bot.get_cog("Logs")

        if logs:
            await logs.send_log(interaction.guild, "mod_logs", embed)

        await asyncio.sleep(5)

        try:
            await msg.delete()
        except:
            pass


    @app_commands.command(name="unwet", description="Retirer un wet")
    async def unwet(self, interaction: discord.Interaction, user_id: str):

        try:
            user_id = int(user_id)
        except:
            return await interaction.response.send_message(
                "ID invalide.",
                ephemeral=True
            )

        data = self.get_wet(user_id)

        if not data:
            return await interaction.response.send_message(
                "Aucun wet actif.",
                ephemeral=True
            )

        author_id = data[0]

        if interaction.user.id != author_id:
            return await interaction.response.send_message(
                "Seul le Fondateur qui a appliqué le WET peut le retirer.",
                ephemeral=True
            )

        self.remove_wet(user_id)

        remove_blacklist(user_id)
        deactivate_ban(interaction.guild.id, user_id)

        try:
            user = await self.bot.fetch_user(user_id)
            await interaction.guild.unban(user)
        except:
            pass

        add_sanction(user_id, interaction.user.id, "UNWET", "Retrait du wet")

        embed = discord.Embed(
            title="WET annulé",
            color=discord.Color.green()
        )

        embed.add_field(
            name="Utilisateur",
            value=f"<@{user_id}>",
            inline=False
        )

        embed.add_field(
            name="Staff",
            value=interaction.user.mention,
            inline=False
        )

        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

        logs = self.bot.get_cog("Logs")

        if logs:
            await logs.send_log(interaction.guild, "mod_logs", embed)


    @commands.Cog.listener()
    async def on_member_join(self, member):

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT user_id FROM wet_users")
        rows = cursor.fetchall()

        conn.close()

        wet_ids = [r[0] for r in rows]

        if member.id not in wet_ids:
            return

        attempts = return_attempts.get(member.id, 0)

        if attempts == 0:

            return_attempts[member.id] = 1

            try:
                await member.send(
                    "Tu essaies de revenir ?\n\n"
                    "Ton accès est fermé.\n\n"
                    "Si tu veux revenir il faudra contribuer.\n"
                    "Contacte Deuspi."
                )
            except:
                pass

            await asyncio.sleep(4)

            try:
                await member.kick(reason="Retour WET")
            except:
                pass

        else:

            try:
                await member.send(
                    "Deuxième tentative.\n\n"
                    "Ton accès est définitivement fermé."
                )
            except:
                pass

            await asyncio.sleep(4)

            try:
                await member.ban(reason="Retour WET définitif")
            except:
                pass


async def setup(bot):
    await bot.add_cog(Wet(bot))