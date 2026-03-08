import discord
from discord.ext import commands
import sqlite3
import time
import random
import asyncio

DB = "database.db"
ROLE_REQUIRED = "Perm III"


def init_giveaway():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS giveaways(
        message_id INTEGER PRIMARY KEY,
        channel_id INTEGER,
        guild_id INTEGER,
        prize TEXT,
        winners INTEGER,
        end_time REAL,
        participants TEXT,
        ended INTEGER
    )
    """)

    conn.commit()
    conn.close()


def has_required_role(member):

    required_role = discord.utils.get(member.guild.roles, name=ROLE_REQUIRED)

    if not required_role:
        return False

    return member.top_role.position >= required_role.position


class JoinButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Participer",
            style=discord.ButtonStyle.green,
            emoji="🎉",
            custom_id="giveaway_join"
        )

    async def callback(self, interaction: discord.Interaction):

        if not has_required_role(interaction.user):

            return await interaction.response.send_message(
                "Vous ne remplissez pas les conditions.",
                ephemeral=True
            )

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT participants FROM giveaways WHERE message_id=?",
            (interaction.message.id,)
        )

        data = cursor.fetchone()

        if not data:
            conn.close()
            return await interaction.response.send_message(
                "Giveaway expiré.",
                ephemeral=True
            )

        participants = data[0].split(",") if data[0] else []

        if str(interaction.user.id) in participants:

            return await interaction.response.send_message(
                "Tu participes déjà.",
                ephemeral=True
            )

        participants.append(str(interaction.user.id))

        cursor.execute(
            "UPDATE giveaways SET participants=? WHERE message_id=?",
            (",".join(participants), interaction.message.id)
        )

        conn.commit()
        conn.close()

        embed = interaction.message.embeds[0]

        embed.set_field_at(
            0,
            name="Participants",
            value=str(len(participants)),
            inline=True
        )

        await interaction.message.edit(embed=embed)

        await interaction.response.send_message(
            "Participation enregistrée.",
            ephemeral=True
        )


class GiveawayView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(JoinButton())


class Giveaway(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        init_giveaway()
        bot.loop.create_task(self.check_giveaways())

    async def check_giveaways(self):

        await self.bot.wait_until_ready()

        while not self.bot.is_closed():

            conn = sqlite3.connect(DB)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM giveaways WHERE ended=0 AND end_time<?",
                (time.time(),)
            )

            rows = cursor.fetchall()

            for row in rows:

                message_id = row[0]
                channel_id = row[1]
                guild_id = row[2]
                prize = row[3]
                winners_count = row[4]
                participants = row[6].split(",") if row[6] else []

                guild = self.bot.get_guild(guild_id)
                channel = guild.get_channel(channel_id)

                try:
                    message = await channel.fetch_message(message_id)
                except:
                    continue

                if len(participants) < winners_count:
                    winners = []
                else:
                    winners = random.sample(participants, winners_count)

                mentions = " ".join([f"<@{w}>" for w in winners]) if winners else "Aucun gagnant"

                embed = message.embeds[0]
                embed.color = discord.Color.red()

                embed.add_field(
                    name="Gagnants",
                    value=mentions,
                    inline=True
                )

                await message.edit(embed=embed, view=None)

                if winners:
                    await channel.send(
                        f"🎉 Félicitations {mentions} vous gagnez **{prize}**"
                    )

                cursor.execute(
                    "UPDATE giveaways SET ended=1 WHERE message_id=?",
                    (message_id,)
                )

                conn.commit()

            conn.close()

            await asyncio.sleep(10)

    @commands.command()
    async def giveaway(self, ctx, duration: int, winners: int, *, prize: str):

        end_time = time.time() + duration

        embed = discord.Embed(
            title="🎉 Giveaway",
            description=f"Récompense : **{prize}**",
            color=discord.Color.green()
        )

        embed.add_field(name="Participants", value="0", inline=True)
        embed.add_field(name="Gagnants", value=str(winners), inline=True)
        embed.add_field(
            name="Fin",
            value=f"<t:{int(end_time)}:R>",
            inline=True
        )

        message = await ctx.send(embed=embed, view=GiveawayView())

        role = discord.utils.get(ctx.guild.roles, name="Giveaways 🎁")

        if role:
            ping = await ctx.send(role.mention)
            await asyncio.sleep(2)
            await ping.delete()

        await ctx.message.delete()

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO giveaways VALUES (?,?,?,?,?,?,?,0)
        """, (
            message.id,
            ctx.channel.id,
            ctx.guild.id,
            prize,
            winners,
            end_time,
            ""
        ))

        conn.commit()
        conn.close()

    @commands.command()
    async def reroll(self, ctx, message_id: int):

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT participants,winners,prize FROM giveaways WHERE message_id=?",
            (message_id,)
        )

        data = cursor.fetchone()
        conn.close()

        if not data:
            return await ctx.send("Giveaway introuvable.")

        participants = data[0].split(",") if data[0] else []
        winners = data[1]
        prize = data[2]

        if not participants:
            return await ctx.send("Aucun participant.")

        new = random.sample(participants, winners)

        mentions = " ".join([f"<@{w}>" for w in new])

        await ctx.send(
            f"Nouveaux gagnants : {mentions} pour **{prize}**"
        )

    @commands.command()
    async def cancel(self, ctx, message_id: int):

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM giveaways WHERE message_id=?",
            (message_id,)
        )

        conn.commit()
        conn.close()

        await ctx.send("Giveaway annulé.")


async def setup(bot):
    await bot.add_cog(Giveaway(bot))