from discord.ext import commands
import discord
from database import get_sanctions, delete_all_sanctions
from datetime import datetime
import sqlite3

FONDATEUR = "Fondateur"
UNIVERSE = "Universe"
CREATEUR = "Créateur"
MAGISTRAL = "Magistral"
ROYAL = "Royal"

class SanctionView(discord.ui.View):

    def __init__(self, rows):
        super().__init__(timeout=120)
        self.rows = rows
        self.page = 0
        self.per_page = 5

    def build_embed(self):

        total_pages = (len(self.rows) - 1) // self.per_page + 1
        start = self.page * self.per_page
        end = start + self.per_page

        embed = discord.Embed(
            title="Historique des sanctions",
            description=f"Page {self.page+1}/{total_pages}",
            color=discord.Color.blurple()
        )

        for s_id, s_type, reason, mod_id, timestamp in self.rows[start:end]:

            date = datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M")

            embed.add_field(
                name=f"{s_type}",
                value=(
                    f"Modérateur : <@{mod_id}> ({mod_id})\n"
                    f"Date : {date}\n"
                    f"Motif : {reason}"
                ),
                inline=False
            )

        embed.timestamp = discord.utils.utcnow()
        return embed


    @discord.ui.button(label="◀", style=discord.ButtonStyle.gray)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):

        if self.page == 0:
            return await interaction.response.defer()

        self.page -= 1
        await interaction.response.edit_message(embed=self.build_embed(), view=self)


    @discord.ui.button(label="▶", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):

        max_page = (len(self.rows) - 1) // self.per_page

        if self.page >= max_page:
            return await interaction.response.defer()

        self.page += 1
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

class Sanctions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_role(self, member, roles):
        return any(r.name in roles for r in member.roles)

    # ---------------- HISTORIQUE ----------------

    @commands.command()
    async def sanction(self, ctx, user_id: int = None):

        if user_id is None:
            user_id = ctx.author.id

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        SELECT id, type, reason, moderator_id, timestamp
        FROM sanctions
        WHERE user_id=?
        AND type NOT IN ('UNBAN','UNBLACKLIST')
        ORDER BY id ASC
        """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return await ctx.send("Aucune sanction trouvée.")

        view = SanctionView(rows)
        await ctx.send(embed=view.build_embed(), view=view)

    # ---------------- DELETE SANCTION ----------------

    @commands.command()
    async def delsanction(self, ctx, user_id: int = None, number: int = None):

        if not self.has_role(ctx.author, [ROYAL, MAGISTRAL, CREATEUR, UNIVERSE, FONDATEUR]):
            return

        if user_id is None:
            user_id = ctx.author.id

        if number is None:
            await ctx.send("Indique le numéro de sanction.")
            return

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM sanctions WHERE user_id=? ORDER BY id ASC", (user_id,))
        data = cursor.fetchall()

        if not data or number < 1 or number > len(data):
            await ctx.send("Numéro invalide.")
            conn.close()
            return

        real_id = data[number - 1][0]
        cursor.execute("DELETE FROM sanctions WHERE id=?", (real_id,))
        conn.commit()
        conn.close()

        await ctx.send("Sanction supprimée.")

    @commands.command()
    async def delsanctionall(self, ctx, user_id: int = None):

        if not self.has_role(ctx.author, [MAGISTRAL, CREATEUR, UNIVERSE, FONDATEUR]):
            return

        if user_id is None:
            user_id = ctx.author.id

        delete_all_sanctions(user_id)
        await ctx.send("Toutes les sanctions ont été supprimées.")

    # ---------------- CLEAR ----------------

    @commands.command()
    async def clear(self, ctx):

        if not self.has_role(ctx.author, [MAGISTRAL, CREATEUR, UNIVERSE, FONDATEUR]):
            return

        await ctx.channel.purge(limit=200)


    # ---------------- FIND ----------------

    @commands.command()
    async def find(self, ctx, member: discord.Member):

        if not self.has_role(ctx.author, [ROYAL, MAGISTRAL, CREATEUR, UNIVERSE, FONDATEUR]):
            return

        # si en vocal
        if member.voice and member.voice.channel:

            channel = member.voice.channel

            embed = discord.Embed(
                description=f"🔎 **Utilisateur trouvé**\n\n{member.mention} est actuellement dans {channel.mention}",
                color=discord.Color.green()
            )

            embed.set_author(name="Recherche vocale")

            await ctx.send(embed=embed)
            return

        # si pas en vocal

        if member.status in [
            discord.Status.online,
            discord.Status.idle,
            discord.Status.dnd
        ]:

            await ctx.send(f"{member.mention} est AFK (pas dans une voc).")

        elif member.status == discord.Status.offline:

            await ctx.send(f"{member.mention} n'est pas connecté à Discord.")

async def setup(bot):
    await bot.add_cog(Sanctions(bot))