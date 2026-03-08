from discord.ext import commands
import sqlite3
import discord
from datetime import datetime
from discord import AuditLogAction


FONDATEUR = "Fondateur"


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------------- CONFIG ----------------

    def toggle_log(self, key, channel_id):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM config WHERE key=?", (key,))
        data = cursor.fetchone()

        if data:
            cursor.execute("DELETE FROM config WHERE key=?", (key,))
            conn.commit()
            conn.close()
            return False
        else:
            cursor.execute("INSERT INTO config VALUES (?,?)", (key, str(channel_id)))
            conn.commit()
            conn.close()
            return True

    async def send_log(self, guild, key, embed):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key=?", (key,))
        data = cursor.fetchone()
        conn.close()

        if data:
            channel = guild.get_channel(int(data[0]))
            if channel:
                await channel.send(embed=embed)

    # ---------------- COMMANDES ----------------

    @commands.command()
    async def setmodlogs(self, ctx, channel: discord.TextChannel = None):
        if FONDATEUR not in [r.name for r in ctx.author.roles]:
            return

        channel = channel or ctx.channel
        status = self.toggle_log("mod_logs", channel.id)

        if status:
            await ctx.send(f"Logs modération activés dans {channel.mention}.")
        else:
            await ctx.send("Logs modération désactivés.")
            
    @commands.command()
    async def setrolelogs(self, ctx, channel: discord.TextChannel = None):

        if "Fondateur" not in [r.name for r in ctx.author.roles]:
            return

        channel = channel or ctx.channel
        status = self.toggle_log("role_logs", channel.id)

        if status:
            await ctx.send(f"Logs des ranks activés dans {channel.mention}.")
        else:
            await ctx.send("Logs des ranks désactivés.")

    @commands.command()
    async def setvoclogs(self, ctx, channel: discord.TextChannel = None):
        if FONDATEUR not in [r.name for r in ctx.author.roles]:
            return

        channel = channel or ctx.channel
        status = self.toggle_log("voc_logs", channel.id)

        if status:
            await ctx.send(f"Logs vocaux activés dans {channel.mention}.")
        else:
            await ctx.send("Logs vocaux désactivés.")

    # ---------------- VOICE LOGS ----------------

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        if before == after:
            return

        embed = discord.Embed()
        embed.set_footer(text=f"Date : {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')} UTC")

        executor = None
        action_type = None

        # Détection des actions vocales normales

        if not before.channel and after.channel:
            action_type = "join"

        elif before.channel and not after.channel:
            action_type = "disconnect"

        elif before.channel and after.channel and before.channel != after.channel:
            action_type = "move"

        # Détection mute / deaf forcés

        if not before.mute and after.mute:
            action_type = "mute"

        elif before.mute and not after.mute:
            action_type = "unmute"

        if not before.deaf and after.deaf:
            action_type = "deaf"

        elif before.deaf and not after.deaf:
            action_type = "undeaf"

        if not action_type:
            return

        # Vérification audit logs pour actions forcées

        async for entry in member.guild.audit_logs(limit=5):
            if entry.target and entry.target.id == member.id:
                if entry.action in [
                    AuditLogAction.member_update,
                    AuditLogAction.member_move,
                    AuditLogAction.member_disconnect
                ]:
                    if entry.user != member:
                        executor = entry.user
                    break

        # Construction des messages

        if action_type == "join":
            embed.title = f"{member.mention} s'est connecté en vocal"
            embed.color = discord.Color.green()
            embed.add_field(name="Salon", value=after.channel.name, inline=False)

        elif action_type == "disconnect":
            embed.color = discord.Color.red()
            embed.add_field(name="Salon", value=before.channel.name, inline=False)

            if executor:
                embed.title = f"{executor.mention} a déconnecté {member.mention}"
            else:
                embed.title = f"{member.mention} s'est déconnecté du vocal"

        elif action_type == "move":
            embed.color = discord.Color.orange()
            embed.add_field(name="De", value=before.channel.name)
            embed.add_field(name="Vers", value=after.channel.name)

            if executor:
                embed.title = f"{executor.mention} a déplacé {member.mention}"
            else:
                embed.title = f"{member.mention} a changé de salon vocal"

        elif action_type == "mute" and executor:
            embed.title = f"{executor.mention} a mute {member.mention}"
            embed.color = discord.Color.dark_red()

        elif action_type == "unmute" and executor:
            embed.title = f"{executor.mention} a unmute {member.mention}"
            embed.color = discord.Color.green()

        elif action_type == "deaf" and executor:
            embed.title = f"{executor.mention} a mis en sourdine {member.mention}"
            embed.color = discord.Color.dark_red()

        elif action_type == "undeaf" and executor:
            embed.title = f"{executor.mention} a retiré la sourdine de {member.mention}"
            embed.color = discord.Color.green()

        else:
            return

        await self.send_log(member.guild, "voc_logs", embed)


    @commands.Cog.listener()
    async def on_message_delete(self, message):

        embed = discord.Embed(
            title="Message supprimé",
            color=discord.Color.red()
        )

        embed.add_field(
            name="Auteur",
            value=f"{message.author} ({message.author.id})",
            inline=False
        )

        embed.add_field(
            name="Salon",
            value=message.channel.mention,
            inline=False
        )

        content = message.content if message.content else "Aucun contenu"

        embed.add_field(
            name="Contenu",
            value=content[:1000],
            inline=False
        )

        embed.timestamp = discord.utils.utcnow()

        await self.send_log(message.guild, "mod_logs", embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):

        if before.author.bot:
            return

        if before.content == after.content:
            return

        embed = discord.Embed(
            title="Message modifié",
            color=discord.Color.orange()
        )

        embed.add_field(name="Auteur", value=before.author.mention, inline=False)
        embed.add_field(name="Salon", value=before.channel.mention, inline=False)

        embed.add_field(
            name="Avant",
            value=before.content[:1000] if before.content else "Aucun contenu",
            inline=False
        )

        embed.add_field(
            name="Après",
            value=after.content[:1000] if after.content else "Aucun contenu",
            inline=False
        )

        embed.set_footer(text=f"Date : {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')} UTC")

        await self.send_log(before.guild, "mod_logs", embed)

async def setup(bot):
    await bot.add_cog(Logs(bot))