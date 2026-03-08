from discord.ext import commands
import discord
from database import add_blacklist, get_blacklist, get_all_blacklist, add_sanction, add_founder_bl
from cogs.utils.permissions import require_permission
import datetime
import sqlite3

FONDATEUR = "Fondateur"
UNIVERSE = "Universe"
CREATEUR = "Créateur"
MAGISTRAL = "Magistral"
GALAXY = "Galaxy"
ROYAL = "Royal"


class BLView(discord.ui.View):

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
            title="Blacklist du serveur",
            description=f"Page {self.page+1}/{total_pages}",
            color=discord.Color.dark_red()
        )

        for user_id, added_by, reason, timestamp, founder_count in self.rows[start:end]:

            date = datetime.datetime.utcfromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M UTC")

            status = "Blacklist standard"
            if founder_count > 0:
                status = f"Blacklist Fondateur {founder_count}/2"

            embed.add_field(
                name="Utilisateur",
                value=(
                    f"<@{user_id}> ({user_id})\n"
                    f"Modérateur : <@{added_by}>\n"
                    f"Motif : {reason}\n"
                    f"Statut : {status}\n"
                    f"Date : {date}"
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


class Blacklist(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @require_permission("bl", roles=[UNIVERSE, FONDATEUR])
    async def bl(self, ctx, user_id: int, *, reason="Non précisé"):

        target = ctx.guild.get_member(user_id)
        existing = get_blacklist(user_id)
        roles = [r.name for r in ctx.author.roles]
        founder_count = 0

        if target:
            roles_author = [r.name for r in ctx.author.roles]
            roles_target = [r.name for r in target.roles]

            if FONDATEUR in roles_author and FONDATEUR in roles_target:
                return await ctx.send(
                    "Impossible. Un Fondateur ne peut pas blacklist un autre Fondateur."
                )

            if UNIVERSE in roles_author:
                if FONDATEUR in roles_target or GALAXY in roles_target:
                    return await ctx.send("Impossible. Rôle protégé.")

        if existing:

            added_by, old_reason, timestamp, founder_count = existing

            if FONDATEUR not in roles:
                return await ctx.send("Cet utilisateur est déjà blacklist.")

            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            cursor.execute(
                "SELECT 1 FROM founder_bl WHERE user_id=? AND founder_id=?",
                (user_id, ctx.author.id)
            )

            already = cursor.fetchone()
            conn.close()

            if already:
                return await ctx.send(
                    "Impossible de blacklist cet utilisateur car vous l’avez déjà blacklist."
                )

            if founder_count >= 2:
                return await ctx.send("Cette personne est déjà blacklist par 2 Fondateurs.")

            add_blacklist(user_id, ctx.author.id, reason, founder=True)
            add_founder_bl(user_id, ctx.author.id)

            data = get_blacklist(user_id)
            _, _, _, founder_count = data

            embed = discord.Embed(
                title="⚠️ Blacklist majorée",
                color=discord.Color.orange()
            )

            date = discord.utils.utcnow().strftime("%d/%m/%Y %H:%M UTC")

            embed.add_field(
                name="Utilisateur",
                value=f"<@{user_id}> ({user_id})",
                inline=False
            )

            embed.add_field(
                name="Action",
                value="Blacklist renforcée par un Fondateur",
                inline=False
            )

            embed.add_field(
                name="Statut",
                value=f"{founder_count}/2 Fondateurs",
                inline=False
            )

            embed.add_field(
                name="Modérateur",
                value=f"{ctx.author.mention} ({ctx.author.id})",
                inline=False
            )

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

            return

        add_blacklist(user_id, ctx.author.id, reason, founder=FONDATEUR in roles)

        if FONDATEUR in roles:
            add_founder_bl(user_id, ctx.author.id)

        add_sanction(user_id, ctx.author.id, "BLACKLIST", reason)

        data = get_blacklist(user_id)
        _, _, _, founder_count = data

        if target:
            try:
                await target.send(
                    f"Tu as été blacklist du serveur **{ctx.guild.name}**.\nMotif : {reason}"
                )
            except:
                pass

        if target:
            try:
                await target.ban(reason=reason)
            except Exception as e:
                return await ctx.send(f"Erreur ban : {e}")

        embed = discord.Embed(
            title="🚫 Blacklist appliquée",
            color=discord.Color.dark_red()
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

        if founder_count > 0:
            embed.add_field(
                name="Statut",
                value=f"Blacklist Fondateur {founder_count}/2",
                inline=False
            )

        embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)

        logs = self.bot.get_cog("Logs")
        if logs:
            await logs.send_log(ctx.guild, "mod_logs", embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):

        data = get_blacklist(member.id)

        if data:
            reason = data[1] or "Blacklist serveur"
            await member.ban(reason=reason)

    @require_permission("bl", roles=[UNIVERSE, FONDATEUR, GALAXY, CREATEUR, MAGISTRAL])
    @commands.command()
    async def listbl(self, ctx):

        rows = get_all_blacklist()

        if not rows:
            return await ctx.send("Aucune blacklist.")

        view = BLView(rows)
        await ctx.send(embed=view.build_embed(), view=view)

    @commands.command()
    async def blinfo(self, ctx, user_id: int):

        roles = [r.name for r in ctx.author.roles]

        if CREATEUR not in roles and UNIVERSE not in roles and FONDATEUR not in roles:
            return await ctx.send("Tu n'as pas la permission d'utiliser cette commande.")

        data = get_blacklist(user_id)

        if not data:
            return await ctx.send("Cet utilisateur n'est pas blacklist.")

        added_by, reason, timestamp, founder_count = data
        date = datetime.datetime.utcfromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M UTC")

        status = "Blacklist standard"
        if founder_count > 0:
            status = f"Blacklist Fondateur {founder_count}/2"

        embed = discord.Embed(
            title="Détail Blacklist",
            color=discord.Color.red()
        )

        embed.add_field(name="Utilisateur", value=f"<@{user_id}> ({user_id})", inline=False)
        embed.add_field(name="Ajouté par", value=f"<@{added_by}>", inline=False)
        embed.add_field(name="Motif", value=reason, inline=False)
        embed.add_field(name="Statut", value=status, inline=False)
        embed.add_field(name="Date", value=date, inline=False)

        embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Blacklist(bot))