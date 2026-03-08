import discord
from discord.ext import commands
from discord import app_commands
import datetime
from database import add_sanction


SANCTIONS = {

    "Troll": {
        "Troll léger": 300,
        "Troll répété": 900,
        "Provocation": 1200
    },

    "Spam": {
        "Spam léger": 300,
        "Spam répété": 600,
        "Spam massif": 1200
    },

    "Insultes": {
        "Insultes légères": 900,
        "Insultes graves": 1200,
        "Insultes racistes": 3600
    },

    "Flood": {
        "Flood léger": 300,
        "Flood important": 900,
        "Flood massif": 1800
    }
}


def get_role_limit(member):

    roles = [r.name for r in member.roles]

    if "Perm V" in roles:
        return 999999

    if "Perm IV" in roles:
        return 2700

    if "Perm III" in roles:
        return 1200

    return 0


class GravitySelect(discord.ui.Select):

    def __init__(self, member, category, staff):

        self.member = member
        self.category = category
        self.staff = staff

        options = []

        limit = get_role_limit(staff)

        for name, duration in SANCTIONS[category].items():

            if duration <= limit:

                minutes = duration // 60

                options.append(
                    discord.SelectOption(
                        label=name,
                        description=f"{minutes} minutes"
                    )
                )

        super().__init__(
            placeholder="Choisir la gravité",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        sanction = self.values[0]

        duration = SANCTIONS[self.category][sanction]

        try:

            await self.member.timeout(
                discord.utils.utcnow() + datetime.timedelta(seconds=duration),
                reason=sanction
            )

        except Exception:

            await interaction.response.send_message(
                "Impossible d'appliquer la sanction.",
                ephemeral=True
            )

            return

        add_sanction(
            self.member.id,
            interaction.user.id,
            "TEMPMUTE",
            sanction
        )

        minutes = duration // 60

        embed = discord.Embed(
            title="Tempmute appliqué",
            color=discord.Color.red()
        )

        embed.add_field(
            name="Utilisateur",
            value=self.member.mention,
            inline=False
        )

        embed.add_field(
            name="Catégorie",
            value=self.category,
            inline=True
        )

        embed.add_field(
            name="Gravité",
            value=sanction,
            inline=True
        )

        embed.add_field(
            name="Durée",
            value=f"{minutes} min",
            inline=True
        )

        embed.add_field(
            name="Modérateur",
            value=interaction.user.mention,
            inline=False
        )

        embed.timestamp = discord.utils.utcnow()

        await interaction.response.edit_message(embed=embed, view=None)


class CategorySelect(discord.ui.Select):

    def __init__(self, member, staff):

        self.member = member
        self.staff = staff

        options = [
            discord.SelectOption(label=name)
            for name in SANCTIONS
        ]

        super().__init__(
            placeholder="Choisir la catégorie",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        category = self.values[0]

        embed = discord.Embed(
            title="Choisir la gravité",
            description=f"Catégorie : {category}",
            color=discord.Color.orange()
        )

        view = GravityView(self.member, category, self.staff)

        await interaction.response.edit_message(embed=embed, view=view)


class GravityView(discord.ui.View):

    def __init__(self, member, category, staff):

        super().__init__(timeout=180)

        self.add_item(GravitySelect(member, category, staff))


class TempmuteView(discord.ui.View):

    def __init__(self, member, staff):

        super().__init__(timeout=180)

        self.add_item(CategorySelect(member, staff))


class Tempmute(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="tempmute", description="Appliquer un tempmute")

    async def tempmute(self, interaction: discord.Interaction, user_id: str):

        try:

            member = await interaction.guild.fetch_member(int(user_id))

        except:

            await interaction.response.send_message(
                "Utilisateur introuvable.",
                ephemeral=True
            )

            return

        limit = get_role_limit(interaction.user)

        if limit == 0:

            await interaction.response.send_message(
                "Tu n'as pas la permission.",
                ephemeral=True
            )

            return

        embed = discord.Embed(
            title="Tempmute",
            description=f"Choisis la catégorie pour {member.mention}",
            color=discord.Color.orange()
        )

        view = TempmuteView(member, interaction.user)

        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Tempmute(bot))