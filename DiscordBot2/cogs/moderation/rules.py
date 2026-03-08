import discord
from discord.ext import commands

ROLE_MEMBER = "Membre"


class AcceptView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Accepter le règlement",
        style=discord.ButtonStyle.green,
        emoji="✅",
        custom_id="accept_rules"
    )
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        role = discord.utils.get(interaction.guild.roles, name=ROLE_MEMBER)

        if not role:
            return await interaction.response.send_message(
                "Rôle membre introuvable.",
                ephemeral=True
            )

        if role in interaction.user.roles:
            return await interaction.response.send_message(
                "Tu as déjà accepté le règlement.",
                ephemeral=True
            )

        await interaction.user.add_roles(role)

        await interaction.response.send_message(
            "Règlement accepté. Accès au serveur accordé.",
            ephemeral=True
        )


class Rules(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(AcceptView())


    @commands.command()
    async def rules(self, ctx):

        embed = discord.Embed(
            title="Règlement Officiel • O²",
            description=(
                "Bienvenue sur **O²**.\n\n"
                "Notre objectif est de maintenir une communauté respectueuse, sécurisée et agréable pour tous.\n"
                "La participation au serveur implique l’acceptation complète du règlement ainsi que des politiques officielles de Discord."
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Politiques Discord",
            value=(
                "Chaque membre doit respecter les règles officielles de Discord.\n\n"
                "Conditions d’utilisation\n"
                "https://discord.com/terms\n\n"
                "Règles communautaires\n"
                "https://discord.com/guidelines"
            ),
            inline=False
        )

        embed.add_field(
            name="Règles générales",
            value=(
                "Respect du staff\n"
                "L’équipe O² veille au bon fonctionnement du serveur. Tout comportement irrespectueux envers un membre du staff pourra entraîner une sanction.\n\n"
                "Contestations\n"
                "Toute contestation de sanction doit être effectuée calmement via le support.\n\n"
                "Responsabilité des membres\n"
                "Chaque membre reste responsable de son comportement sur le serveur."
            ),
            inline=False
        )

        embed.add_field(
            name="Salons textuels",
            value=(
                "Respect et tolérance\n"
                "Les insultes, propos discriminatoires ou attaques personnelles ne sont pas tolérés.\n\n"
                "Protection des informations\n"
                "La divulgation d’informations personnelles est interdite.\n\n"
                "Spam et publicité\n"
                "Le spam, le flood et la publicité non autorisée sont interdits.\n\n"
                "Contenus inappropriés\n"
                "Les contenus pornographiques, violents ou choquants sont interdits."
            ),
            inline=False
        )

        embed.add_field(
            name="Salons vocaux",
            value=(
                "Comportement en vocal\n"
                "Respecte les autres utilisateurs et évite toute nuisance sonore.\n\n"
                "Soundboards et modification de voix\n"
                "Les effets sonores perturbants sont interdits.\n\n"
                "Contenus diffusés\n"
                "Aucun contenu illégal, sensible ou choquant ne doit être diffusé."
            ),
            inline=False
        )

        embed.add_field(
            name="Sécurité et conformité",
            value=(
                "Signalement\n"
                "Tout comportement problématique doit être signalé au staff.\n\n"
                "Respect des règles Discord\n"
                "Toute violation des règles de Discord peut entraîner une exclusion du serveur."
            ),
            inline=False
        )

        embed.add_field(
            name="Sanctions",
            value=(
                "Le non respect du règlement peut entraîner :\n\n"
                "Avertissement\n"
                "Timeout\n"
                "Kick\n"
                "Bannissement permanent"
            ),
            inline=False
        )

        embed.set_footer(text="O² Community • Règlement officiel")
        embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed, view=AcceptView())


async def setup(bot):
    await bot.add_cog(Rules(bot))